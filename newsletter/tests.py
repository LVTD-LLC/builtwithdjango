from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone

from jobs.models import Job
from makers.models import Maker
from newsletter.tasks import add_email_to_buttondown, send_buttondown_newsletter
from newsletter.utils import get_jobs_block, get_projects_block
from projects.models import Project


class NewsletterContentTests(TestCase):
    def test_projects_block_uses_resolved_project_and_maker_urls(self):
        maker = Maker.objects.create(first_name="Ada", last_name="Lovelace", slug="ada")
        project = Project.objects.create(
            title="Django CMS",
            url="https://cms.example.com",
            short_description="A CMS built with Django.",
            published=True,
            active=True,
            maker=maker,
        )

        block = get_projects_block(days_back=7)

        self.assertIn(f"https://builtwithdjango.com{project.get_absolute_url()}", block)
        self.assertIn(f"https://builtwithdjango.com{maker.get_absolute_url()}", block)
        self.assertNotIn("bound method", block)
        self.assertNotIn("by by", block)

    def test_jobs_block_uses_resolved_job_urls_and_marks_paid_jobs(self):
        job = Job.objects.create(
            title="Django developer",
            listing_url="https://example.com/jobs/django",
            company_name="Example Co",
            approved=True,
            paid=True,
            created_datetime=timezone.now(),
        )

        block = get_jobs_block(days_back=7)

        self.assertIn(f"https://builtwithdjango.com{job.get_absolute_url()}", block)
        self.assertIn("⭐⭐⭐", block)
        self.assertNotIn("bound method", block)


class ButtondownTaskTests(TestCase):
    def test_add_email_to_buttondown_posts_payload_with_timeout_and_returns_success(self):
        response = Mock(status_code=201, text='{"id": "subscriber"}')
        response.json.return_value = {"id": "subscriber"}

        with patch("newsletter.tasks.requests.post", return_value=response) as post:
            result = add_email_to_buttondown("reader@example.com", tag="newsletter", ip_address="127.0.0.1")

        self.assertEqual(result, {"success": True, "data": {"id": "subscriber"}})
        self.assertEqual(post.call_args.kwargs["timeout"], 30)
        self.assertEqual(post.call_args.kwargs["json"]["email_address"], "reader@example.com")
        self.assertEqual(post.call_args.kwargs["json"]["ip_address"], "127.0.0.1")

    def test_send_buttondown_newsletter_creates_draft_and_checks_response_status(self):
        response = Mock()

        with (
            patch("newsletter.tasks.prepare_newsletter", return_value="Newsletter body") as prepare,
            patch("newsletter.tasks.generate_buttondown_newsletter_subject", return_value="Subject") as subject,
            patch("newsletter.tasks.requests.post", return_value=response) as post,
        ):
            result = send_buttondown_newsletter(days_back=14)

        self.assertEqual(result, "Success")
        prepare.assert_called_once_with(days_back=14)
        subject.assert_called_once_with("Newsletter body")
        response.raise_for_status.assert_called_once()
        self.assertEqual(post.call_args.kwargs["timeout"], 30)
        self.assertEqual(
            post.call_args.kwargs["json"], {"subject": "Subject", "body": "Newsletter body", "status": "draft"}
        )


# Create your tests here.
