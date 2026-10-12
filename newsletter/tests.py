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


from django.core.cache import cache
from django.test import Client, override_settings

from newsletter.models import Emails


@override_settings(NEWSLETTER_LISTMONK_URL="http://listmonk:9000", NEWSLETTER_LIST_UUID="public-list")
class ListmonkSignupTests(TestCase):
    def setUp(self):
        cache.clear()
        # Python CI has no asset build; frontend CI and browser checks cover assets.
        patch("webpack_boilerplate.utils.get_as_tags", return_value=[]).start()
        self.provider = patch("newsletter.views.requests.post").start()
        self.addCleanup(patch.stopall)
        self.provider.return_value = Mock(status_code=200)
        self.provider.return_value.json.return_value = {"data": {"has_optin": True}}

    def test_signup_requests_optin_without_saving_email_or_queuing_buttondown(self):
        with patch("newsletter.views.capture") as capture:
            response = self.client.post("/newsletter/", {"user_email": "reader@example.com"})
        self.assertRedirects(response, "/newsletter/email-signup-thanks/", fetch_redirect_response=False)
        self.assertEqual(Emails.objects.count(), 0)
        self.assertEqual(
            self.provider.call_args.kwargs["json"], {"email": "reader@example.com", "list_uuids": ["public-list"]}
        )
        self.assertFalse(self.provider.call_args.kwargs["allow_redirects"])
        self.assertEqual(capture.call_args.args[1], "newsletter confirmation requested")
        self.assertNotIn("email_hash", capture.call_args.kwargs["properties"])

    def test_invalid_email_and_honeypot_never_reach_provider(self):
        self.assertEqual(self.client.post("/newsletter/", {"user_email": "bad"}).status_code, 400)
        self.assertEqual(
            self.client.post("/newsletter/", {"user_email": "r@example.com", "company": "bot"}).status_code, 302
        )
        self.provider.assert_not_called()

    def test_failure_retains_form_and_does_not_claim_success(self):
        for payload in [None, {"data": True}, {"data": {}}, {"data": {"has_optin": False}}]:
            self.provider.return_value.json.return_value = payload
            response = self.client.post("/newsletter/", {"user_email": "reader@example.com"})
            self.assertEqual(response.status_code, 503)
            self.assertContains(response, "reader@example.com", status_code=503)
        self.provider.side_effect = __import__("requests").Timeout()
        self.assertEqual(self.client.post("/newsletter/", {"user_email": "reader@example.com"}).status_code, 503)

    @override_settings(NEWSLETTER_LIST_UUID="")
    def test_unconfigured_is_unavailable(self):
        self.assertEqual(self.client.post("/newsletter/", {"user_email": "r@example.com"}).status_code, 503)
        self.provider.assert_not_called()

    def test_rate_limit_is_shared_and_forwarded_header_cannot_bypass_default(self):
        for i in range(10):
            self.client.post("/newsletter/", {"user_email": "r@example.com"}, HTTP_X_FORWARDED_FOR=str(i))
        response = self.client.post("/newsletter/", {"user_email": "r@example.com"}, HTTP_X_FORWARDED_FOR="other")
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Retry-After"], "3600")
        self.assertEqual(self.provider.call_count, 10)

    def test_csrf_is_required(self):
        self.assertEqual(
            Client(enforce_csrf_checks=True).post("/newsletter/", {"user_email": "r@example.com"}).status_code, 403
        )
        self.provider.assert_not_called()

    def test_thanks_explains_confirmation(self):
        self.assertContains(self.client.get("/newsletter/email-signup-thanks/"), "Check your inbox")

    def test_cache_failure_never_sends(self):
        with patch("newsletter.views.cache.add", side_effect=ConnectionError):
            self.assertEqual(self.client.post("/newsletter/", {"user_email": "r@example.com"}).status_code, 503)
        self.provider.assert_not_called()

    def test_http_error_never_claims_success(self):
        self.provider.return_value.status_code = 500
        self.assertEqual(self.client.post("/newsletter/", {"user_email": "r@example.com"}).status_code, 503)

    @override_settings(NEWSLETTER_TRUST_PROXY=True)
    def test_trusted_proxy_uses_appended_address_not_spoofed_leftmost(self):
        for i in range(10):
            self.client.post(
                "/newsletter/", {"user_email": "r@example.com"}, HTTP_X_FORWARDED_FOR=f"spoof{i}, 192.0.2.1"
            )
        self.assertEqual(
            self.client.post(
                "/newsletter/", {"user_email": "r@example.com"}, HTTP_X_FORWARDED_FOR="different, 192.0.2.1"
            ).status_code,
            429,
        )
        self.assertEqual(
            self.client.post(
                "/newsletter/", {"user_email": "r@example.com"}, HTTP_X_FORWARDED_FOR="spoof, 192.0.2.2"
            ).status_code,
            302,
        )
