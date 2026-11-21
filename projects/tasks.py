from django_q.tasks import async_task

from builtwithdjango.notifications import send_admin_notification

from .models import Project


def notify_of_new_project(instance):
    message = f"""
      {instance.logged_in_maker} submitted a project ({instance.title} - {instance.url}).
    """
    return send_admin_notification("New Project Submission", message)


def notify_owner_of_new_comment(instance):
    # Comments are temporarily disabled to mitigate abuse.
    return


def notify_admins_of_comment(instance):
    # Comments are temporarily disabled to mitigate abuse.
    return


def check_all_projects():
    projects = Project.objects.filter(published=True)

    for project in projects:
        async_task(update_project_active_status, project.id, group="Check Project Active Status")


def update_project_active_status(project_id):
    project = Project.objects.get(id=project_id)

    active = project.check_project_is_active()

    if not active:
        project.active = False
        project.save(update_fields=["active"])

    return f"Project {project.title} is active: {active}"
