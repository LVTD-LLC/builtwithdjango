from urllib.parse import urlparse

import cloudinary.uploader
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django_q.tasks import async_task

from builtwithdjango.sentry_utils import sentry_count, sentry_distribution, sentry_task_transaction
from builtwithdjango.utils import get_builtwithdjango_logger

from .models import Job

logger = get_builtwithdjango_logger(__name__)


def notify_of_new_job(instance):
    message = f"""
      Someone submitted a new job.
      Instance: {instance}
    """
    send_mail(
        "New Job Submission",
        message,
        "Built with Django <rasul@builtwithdjango.com>",
        ["Built with Django <rasul@builtwithdjango.com>"],
        fail_silently=False,
    )


def queue_sponsorship_request_email(job_instance):
    """
    Queue an email asking the job owner if they want to promote the job.
    """
    email = (job_instance.email or "").strip()
    if not email:
        logger.info(f"No email found for job {job_instance.id}, skipping sponsorship request")
        return None

    return async_task(
        send_sponsorship_request_email,
        job_instance.id,
        task_name=f"send_sponsorship_email_job_{job_instance.id}",
    )


def send_sponsorship_request_email(job_id):
    """
    Send an email to the job poster asking if they want to promote the job posting.
    """
    try:
        job_instance = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:
        logger.warning(f"Job {job_id} does not exist, skipping sponsorship request")
        return False

    email = (job_instance.email or "").strip()
    if not email:
        logger.info(f"No email found for job {job_instance.id}, skipping sponsorship request")
        return False

    subject = "Promote your Django job on Built with Django?"

    # Use SITE_URL from settings (works for local dev and production)
    site_url = settings.SITE_URL.rstrip("/")
    job_url = f"{site_url}{job_instance.get_absolute_url()}"
    sponsor_url = f"{site_url}{reverse('sponsor_job_checkout', kwargs={'pk': job_instance.id})}"
    sponsor_options_url = f"{site_url}{reverse('advertize')}"

    message = f"""Hey there,

I added your Django job to the Built with Django job board:

{job_instance.title}
{job_url}

Would you like to promote this job opening?

Promoted jobs are highlighted on the job board and shared in the Built with Django newsletter.

You can promote this job here:
{sponsor_url}

You can also see the other sponsorship options here:
{sponsor_options_url}

Best,
Rasul"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        logger.info(f"Sponsorship request email sent successfully for job {job_instance.id} to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send sponsorship request email for job {job_instance.id}: {str(e)}")
        return False


def get_latest_jobs_from_tj_alerts():
    sentry_count("jobs.tj_alerts_import.started")
    with sentry_task_transaction("jobs.tasks.get_latest_jobs_from_tj_alerts"):
        try:
            url = settings.TJ_ALERTS_HOST + "/jobs"

            headers = {
                "Authorization": f"Bearer {settings.TJ_ALERTS_API_KEY}",
            }

            params = {"technologies": "Django"}

            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            jobs = data["jobs"]

            count = 0
            for job in jobs:
                try:
                    title = job["title"][0]
                except IndexError:
                    title = "Software Engineer"

                if Job.objects.filter(external_id=job["id"], source="gettjalerts.com").exists():
                    continue

                company_url = job["company_url"]

                # Extract email if available from the job data
                job_email = ""
                emails = job.get("emails", [])
                if emails and len(emails) > 0:
                    try:
                        job_email = emails[0]["email"]
                    except (KeyError, TypeError, IndexError) as e:
                        logger.warning(f"Could not extract email from job {job['id']}: {e}")
                        job_email = ""

                new_job = Job(
                    submitted_datetime=job["submitted_datetime"],
                    created_datetime=job["submitted_datetime"],
                    updated_datetime=job["submitted_datetime"],
                    source="gettjalerts.com",
                    external_id=job["id"],
                    title=title,
                    listing_url=f"https://gettjalerts.com/jobs/{job['id']}",
                    description=job["description"],
                    email=job_email,
                    min_yearly_salary=job["min_salary"],
                    max_yearly_salary=job["max_salary"],
                    remote=job["is_remote"],
                    location=job["locations"],
                    company_name=job["company_name"],
                )

                if company_url:
                    parsed_url = urlparse(company_url)
                    domain_name = parsed_url.netloc

                    try:
                        image_response = cloudinary.uploader.upload(
                            f"https://www.google.com/s2/favicons?domain={domain_name}&sz=128",
                            public_id=f"user-profile-image-{settings.ENVIRONMENT}/{domain_name}",
                        )
                        new_job.company_logo = (
                            f"image/upload/v{image_response['version']}/{image_response['public_id']}"
                        )
                        new_job.approved = True
                    except Exception as e:
                        logger.error("company_logo_upload_failed", domain_name=domain_name, error=str(e))

                new_job.save()

                # Send sponsorship request email if job has an email address
                queue_sponsorship_request_email(new_job)

                count += 1

            sentry_distribution("jobs.tj_alerts_import.created_jobs", count, attributes={"source": "gettjalerts"})
            sentry_count("jobs.tj_alerts_import.completed", attributes={"outcome": "success"})

            try:
                requests.get(f"{settings.HEALTHCHECKS_HOST}/c4d85df8-bc6a-446a-9c15-aff1b0b0667d", timeout=10)
            except requests.RequestException as e:
                logger.error("Ping failed: %s" % e)

            return f"{count} jobs were created."
        except Exception:
            sentry_count("jobs.tj_alerts_import.completed", attributes={"outcome": "failure"})
            raise
