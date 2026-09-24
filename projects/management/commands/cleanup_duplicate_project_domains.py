from collections import defaultdict

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from projects.domains import project_domain
from projects.models import Project


def keeper_order(project):
    # Preserve a live curated listing before a pending/inactive/spam submission.
    visible = project.published and project.active and not project.might_be_spam
    return (not visible, not (project.active and not project.might_be_spam), project.date_added, project.pk)


class Command(BaseCommand):
    help = "Preview duplicate project domains; --apply deactivates extras without deleting data."

    def add_arguments(self, parser):
        parser.add_argument("--domain", help="Limit cleanup to one hostname (or URL).")
        parser.add_argument("--keep-id", type=int, help="Keep this project; requires --domain.")
        parser.add_argument("--apply", action="store_true", help="Apply the previewed deactivations.")

    def handle(self, *args, **options):
        target = options["domain"]
        if target:
            try:
                target = project_domain(target if "://" in target else f"https://{target}")
            except ValidationError as exc:
                raise CommandError("--domain must be a valid hostname or URL.") from exc
        if options["keep_id"] and not target:
            raise CommandError("--keep-id requires --domain.")

        groups = defaultdict(list)
        for project in Project.objects.only("id", "url").iterator():
            try:
                domain = project_domain(project.url)
            except ValidationError:
                self.stderr.write(f"Skipping project {project.pk}: invalid URL.")
                continue
            if target is None or domain == target:
                groups[domain].append(project.pk)
        if options["keep_id"] and options["keep_id"] not in groups.get(target, []):
            raise CommandError("--keep-id does not belong to the selected domain.")

        count = 0
        for domain, ids in sorted(groups.items()):
            if len(ids) < 2:
                continue
            with transaction.atomic():
                # Re-read under project locks, preserving concurrent owner edits.
                projects = Project.objects.filter(pk__in=ids).order_by("pk")
                if options["apply"]:
                    projects = projects.select_for_update()
                projects = [p for p in projects if project_domain(p.url) == domain]
                if len(projects) < 2:
                    continue
                if options["keep_id"]:
                    keeper = next((p for p in projects if p.pk == options["keep_id"]), None)
                    if keeper is None:
                        raise CommandError("The selected keeper changed domains; rerun the preview.")
                else:
                    keeper = min(projects, key=keeper_order)
                self.stdout.write(f"{domain}: keep #{keeper.pk} ({keeper.title})")
                duplicates = [p for p in projects if p.pk != keeper.pk]
                for project in duplicates:
                    changed = project.published or project.active
                    action = "deactivate" if changed else "already inactive"
                    self.stdout.write(f"  {action} #{project.pk} ({project.title})")
                    count += bool(changed)
                if options["apply"]:
                    Project.objects.filter(pk__in=[p.pk for p in duplicates if p.published or p.active]).update(
                        published=False, active=False, updated_date=timezone.now()
                    )
        mode = "Applied" if options["apply"] else "Dry run (use --apply to change data)"
        self.stdout.write(f"{mode}: {count} project(s) to deactivate. No records deleted.")
