import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from builtwithdjango.indexnow import IndexNowError, submit, validate_urls


class Command(BaseCommand):
    help = "Submit the live public sitemap to IndexNow (never private catalogue URLs)."
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--previous", type=Path, help="Pre-deployment sitemap JSON snapshot, for removed URLs")

    def handle(self, *args, **options):
        try:
            previous = json.loads(options["previous"].read_text()) if options["previous"] else []
            validate_urls(settings.SITE_URL.rstrip("/"), previous)
            result = submit(settings.SITE_URL, previous, dry_run=options["dry_run"])
        except (IndexNowError, ValueError, OSError) as error:
            raise CommandError(str(error)) from None
        self.stdout.write(result)
