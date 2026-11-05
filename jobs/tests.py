from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Job
from .tasks import get_latest_jobs_from_tj_alerts, queue_sponsorship_request_email, send_sponsorship_request_email
from .views import JobListView


class JobItemTemplateTests(TestCase):
    def test_job_item_omits_empty_submitted_datetime(self):
        job = Job.objects.create(
            title="Django developer",
            listing_url="https://example.com/jobs/django-developer",
            company_name="Example Co",
            approved=True,
        )

        html = render_to_string("components/job-item.html", {"job": job})

        self.assertIn("Django developer", html)
        self.assertNotIn("la-clock", html)
        self.assertNotIn(" ago", html)


class JobListViewTests(TestCase):
    def test_job_list_queryset_uses_current_time_each_request(self):
        now = timezone.now()
        recent_job = Job.objects.create(
            title="Recent Django role",
            listing_url="https://example.com/recent",
            company_name="Recent Co",
            approved=True,
            paid=True,
            created_datetime=now - timedelta(days=2),
        )
        Job.objects.create(
            title="Old Django role",
            listing_url="https://example.com/old",
            company_name="Old Co",
            approved=True,
            created_datetime=now - timedelta(days=61),
        )
        Job.objects.create(
            title="Draft Django role",
            listing_url="https://example.com/draft",
            company_name="Draft Co",
            approved=False,
            created_datetime=now,
        )

        request = RequestFactory().get(reverse("jobs"))
        view = JobListView()
        view.setup(request)

        with patch("jobs.models.timezone.now", return_value=now):
            jobs = list(view.get_queryset())

        self.assertEqual(jobs, [recent_job])


class JobCheckoutTests(TestCase):
    def test_create_checkout_session_redirects_to_stripe_checkout(self):
        job = Job.objects.create(
            title="Django developer",
            listing_url="https://example.com/jobs/django",
            company_name="Example Co",
        )
        price_id = "price_job"
        checkout_session = SimpleNamespace(id="cs_test", url="https://checkout.stripe.test/session")

        with (
            patch("jobs.views.get_stripe_price_id", return_value=price_id) as get_price,
            patch("jobs.views.stripe.checkout.Session.create", return_value=checkout_session) as create_session,
            patch("jobs.views.capture") as capture,
        ):
            response = self.client.get(reverse("stripe_checkout_session", kwargs={"pk": job.pk}))

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response["Location"], checkout_session.url)
        get_price.assert_called_once_with("job")
        create_session.assert_called_once()
        self.assertEqual(create_session.call_args.kwargs["metadata"], {"pk": str(job.pk), "price_id": price_id})
        capture.assert_called_once()

    def test_sponsor_job_checkout_session_redirects_to_stripe_checkout(self):
        job = Job.objects.create(
            title="Sponsored Django developer",
            listing_url="https://example.com/jobs/sponsored-django",
            company_name="Example Co",
        )
        price_id = "price_job"
        checkout_session = SimpleNamespace(id="cs_sponsor_test", url="https://checkout.stripe.test/sponsor")

        with (
            patch("jobs.views.get_stripe_price_id", return_value=price_id) as get_price,
            patch("jobs.views.stripe.checkout.Session.create", return_value=checkout_session) as create_session,
            patch("jobs.views.capture") as capture,
        ):
            response = self.client.get(reverse("sponsor_job_checkout", kwargs={"pk": job.pk}))

        expected_success_url = f"http://testserver{reverse('job_thank_you')}?session_id={{CHECKOUT_SESSION_ID}}"
        expected_cancel_url = f"http://testserver{job.get_absolute_url()}?status=failed"

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response["Location"], checkout_session.url)
        get_price.assert_called_once_with("job")
        create_session.assert_called_once_with(
            success_url=expected_success_url,
            cancel_url=expected_cancel_url,
            mode="payment",
            line_items=[
                {
                    "quantity": 1,
                    "price": price_id,
                }
            ],
            allow_promotion_codes=True,
            automatic_tax={"enabled": True},
            metadata={"pk": str(job.pk), "price_id": price_id},
        )
        capture.assert_called_once()


class JobSponsorshipEmailTaskTests(TestCase):
    @override_settings(
        SITE_URL="https://builtwithdjango.com",
        DEFAULT_FROM_EMAIL="Built with Django <rasul@builtwithdjango.com>",
    )
    @patch("jobs.tasks.send_mail")
    def test_send_sponsorship_request_email_sends_promotion_email(self, send_mail):
        job = Job.objects.create(
            title="Senior Django Developer",
            listing_url="https://example.com/jobs/senior-django-developer",
            company_name="Example Co",
            email="hiring@example.com",
        )

        sent = send_sponsorship_request_email(job.id)

        self.assertTrue(sent)
        send_mail.assert_called_once()
        subject, message, from_email, recipients = send_mail.call_args.args
        self.assertEqual(subject, "Promote your Django job on Built with Django?")
        self.assertEqual(from_email, "Built with Django <rasul@builtwithdjango.com>")
        self.assertEqual(recipients, ["hiring@example.com"])
        self.assertIn("I added your Django job to the Built with Django job board", message)
        self.assertIn(f"https://builtwithdjango.com{job.get_absolute_url()}", message)
        expected_sponsor_path = reverse("sponsor_job_checkout", kwargs={"pk": job.id})
        self.assertIn(f"https://builtwithdjango.com{expected_sponsor_path}", message)
        self.assertIn("shared in the Built with Django newsletter", message)
        self.assertEqual(send_mail.call_args.kwargs, {"fail_silently": False})

    @patch("jobs.tasks.send_mail")
    def test_send_sponsorship_request_email_skips_jobs_without_email(self, send_mail):
        job = Job.objects.create(
            title="Django Developer",
            listing_url="https://example.com/jobs/django-developer",
            company_name="Example Co",
        )

        sent = send_sponsorship_request_email(job.id)

        self.assertFalse(sent)
        send_mail.assert_not_called()

    @patch("jobs.tasks.async_task")
    def test_queue_sponsorship_request_email_queues_job_id(self, async_task):
        async_task.return_value = "task-id"
        job = Job.objects.create(
            title="Django Developer",
            listing_url="https://example.com/jobs/django-developer",
            company_name="Example Co",
            email="hiring@example.com",
        )

        task_id = queue_sponsorship_request_email(job)

        self.assertEqual(task_id, "task-id")
        task_function, job_id = async_task.call_args.args
        self.assertIs(task_function, send_sponsorship_request_email)
        self.assertEqual(job_id, job.id)
        self.assertEqual(async_task.call_args.kwargs, {"task_name": f"send_sponsorship_email_job_{job.id}"})

    @patch("jobs.tasks.async_task")
    def test_queue_sponsorship_request_email_skips_jobs_without_email(self, async_task):
        job = Job.objects.create(
            title="Django Developer",
            listing_url="https://example.com/jobs/django-developer",
            company_name="Example Co",
        )

        task_id = queue_sponsorship_request_email(job)

        self.assertIsNone(task_id)
        async_task.assert_not_called()


class JobImportTaskTests(TestCase):
    def test_get_latest_jobs_from_tj_alerts_imports_new_jobs_skips_duplicates_and_queues_email(self):
        submitted_at = timezone.now()
        Job.objects.create(
            title="Existing Django role",
            listing_url="https://gettjalerts.com/jobs/existing",
            company_name="Existing Co",
            external_id="existing",
            source="gettjalerts.com",
        )
        jobs_response = Mock()
        jobs_response.json.return_value = {
            "jobs": [
                {
                    "id": "existing",
                    "title": ["Existing Django role"],
                    "company_url": "https://existing.example.com",
                    "submitted_datetime": submitted_at,
                    "description": "Already imported.",
                    "emails": [{"email": "existing@example.com"}],
                    "min_salary": 100000,
                    "max_salary": 120000,
                    "is_remote": True,
                    "locations": "Remote",
                    "company_name": "Existing Co",
                },
                {
                    "id": "new",
                    "title": ["New Django role"],
                    "company_url": "https://new.example.com",
                    "submitted_datetime": submitted_at,
                    "description": "A new role.",
                    "emails": [{"email": "new@example.com"}],
                    "min_salary": 110000,
                    "max_salary": 130000,
                    "is_remote": True,
                    "locations": "Remote",
                    "company_name": "New Co",
                },
            ]
        }
        healthcheck_response = Mock()

        with (
            patch("jobs.tasks.requests.get", side_effect=[jobs_response, healthcheck_response]) as get,
            patch(
                "jobs.tasks.cloudinary.uploader.upload",
                return_value={"version": "1", "public_id": "logos/new"},
            ) as upload,
            patch("jobs.tasks.queue_sponsorship_request_email") as queue_sponsorship_email,
        ):
            result = get_latest_jobs_from_tj_alerts()

        self.assertEqual(result, "1 jobs were created.")
        self.assertEqual(Job.objects.filter(source="gettjalerts.com").count(), 2)
        new_job = Job.objects.get(external_id="new")
        self.assertEqual(new_job.email, "new@example.com")
        self.assertTrue(new_job.approved)
        self.assertEqual(get.call_args_list[0].kwargs["timeout"], 30)
        upload.assert_called_once()
        queue_sponsorship_email.assert_called_once_with(new_job)

    @patch("jobs.tasks.queue_sponsorship_request_email")
    @patch("jobs.tasks.requests.get")
    def test_get_latest_jobs_from_tj_alerts_delegates_sponsorship_email_skip_without_email(
        self, requests_get, queue_sponsorship_request_email
    ):
        job_response = Mock()
        job_response.json.return_value = {
            "jobs": [
                {
                    "id": "tj-2",
                    "title": ["Django Developer"],
                    "company_url": "",
                    "emails": [],
                    "submitted_datetime": timezone.now(),
                    "description": "Build Django apps.",
                    "min_salary": None,
                    "max_salary": None,
                    "is_remote": True,
                    "locations": "Remote",
                    "company_name": "Example Co",
                }
            ]
        }
        healthcheck_response = Mock()
        requests_get.side_effect = [job_response, healthcheck_response]

        result = get_latest_jobs_from_tj_alerts()

        self.assertEqual(result, "1 jobs were created.")
        job = Job.objects.get(external_id="tj-2", source="gettjalerts.com")
        self.assertEqual(job.email, "")
        queue_sponsorship_request_email.assert_called_once_with(job)


class JobSubmissionProtectionTests(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.payload = {
            "title": "Django Engineer",
            "company_name": "Example",
            "listing_url": "https://example.com/jobs/engineer",
            "email": "hiring@example.com",
        }

    @override_settings(JOB_TURNSTILE_ENABLED=True, JOB_TURNSTILE_SITE_KEY="site", JOB_TURNSTILE_SECRET_KEY="secret")
    def test_missing_challenge_never_saves_or_queues(self):
        with patch("jobs.views.async_task") as queue, patch("jobs.abuse.requests.post") as verify:
            response = self.client.post(reverse("post_job"), self.payload)
        self.assertContains(response, "complete the verification")
        self.assertFalse(Job.objects.exists())
        queue.assert_not_called()
        verify.assert_not_called()

    @override_settings(
        JOB_TURNSTILE_ENABLED=True,
        JOB_TURNSTILE_SITE_KEY="site",
        JOB_TURNSTILE_SECRET_KEY="secret",
        SITE_URL="https://builtwithdjango.com",
    )
    def test_verified_submission_is_unapproved_and_queues_id(self):
        payload = {**self.payload, "cf-turnstile-response": "valid-token"}
        with patch("jobs.views.async_task") as queue, patch("jobs.abuse.requests.post") as verify:
            verify.return_value.json.return_value = {
                "success": True,
                "hostname": "builtwithdjango.com",
                "action": "post-job",
            }
            response = self.client.post(reverse("post_job"), payload)
        self.assertEqual(response.status_code, 302)
        job = Job.objects.get()
        self.assertFalse(job.approved)
        self.assertFalse(job.paid)
        self.assertEqual(queue.call_args.args[1], job.pk)
        self.assertEqual(verify.call_args.kwargs["timeout"], (3, 5))

    @override_settings(
        JOB_TURNSTILE_ENABLED=True,
        JOB_TURNSTILE_SITE_KEY="site",
        JOB_TURNSTILE_SECRET_KEY="secret",
        SITE_URL="https://builtwithdjango.com",
    )
    def test_failed_challenge_hostname_action_and_outage_fail_closed(self):
        import requests

        payload = {**self.payload, "cf-turnstile-response": "token"}
        results = [
            {"success": False},
            {"success": True, "hostname": "other.example", "action": "post-job"},
            {"success": True, "hostname": "builtwithdjango.com", "action": "login"},
            [],
        ]
        with patch("jobs.views.async_task") as queue, patch("jobs.abuse.requests.post") as verify:
            for result in results:
                verify.return_value.json.return_value = result
                self.assertEqual(self.client.post(reverse("post_job"), payload).status_code, 200)
            verify.side_effect = requests.Timeout()
            self.assertEqual(self.client.post(reverse("post_job"), payload).status_code, 200)
        self.assertFalse(Job.objects.exists())
        queue.assert_not_called()

    @override_settings(JOB_SUBMISSION_LIMIT=2, JOB_SUBMISSION_TRUST_PROXY_IP=True)
    def test_invalid_attempts_are_limited_and_forwarded_for_cannot_bypass(self):
        with patch("jobs.views.async_task") as queue:
            for spoofed in ["1.1.1.1", "2.2.2.2"]:
                response = self.client.post(
                    reverse("post_job"), {}, HTTP_X_REAL_IP="198.51.100.2", HTTP_X_FORWARDED_FOR=spoofed
                )
                self.assertEqual(response.status_code, 200)
            response = self.client.post(
                reverse("post_job"), {}, HTTP_X_REAL_IP="198.51.100.2", HTTP_X_FORWARDED_FOR="3.3.3.3"
            )
            self.assertEqual(response.status_code, 429)
            self.assertIn("Retry-After", response)
            self.assertEqual(self.client.post(reverse("post_job"), {}, HTTP_X_REAL_IP="198.51.100.3").status_code, 200)
        queue.assert_not_called()

    def test_cache_outage_does_not_save_or_queue(self):
        with patch("jobs.abuse.cache.add", side_effect=ConnectionError()), patch("jobs.views.async_task") as queue:
            response = self.client.post(reverse("post_job"), self.payload)
        self.assertEqual(response.status_code, 503)
        self.assertFalse(Job.objects.exists())
        queue.assert_not_called()

    def test_honeypot_blocks_submission(self):
        with patch("jobs.views.async_task") as queue:
            self.client.post(reverse("post_job"), {**self.payload, "website": "https://spam.example"})
        self.assertFalse(Job.objects.exists())
        queue.assert_not_called()

    @override_settings(JOB_TURNSTILE_ENABLED=True, JOB_TURNSTILE_SITE_KEY="", JOB_TURNSTILE_SECRET_KEY="")
    def test_unconfigured_challenge_blocks_and_oversized_token_never_calls_provider(self):
        with patch("jobs.abuse.requests.post") as verify, patch("jobs.views.async_task") as queue:
            self.client.post(reverse("post_job"), {**self.payload, "cf-turnstile-response": "token"})
            self.client.post(reverse("post_job"), {**self.payload, "cf-turnstile-response": "x" * 2049})
        self.assertFalse(Job.objects.exists())
        verify.assert_not_called()
        queue.assert_not_called()

    @override_settings(JOB_SUBMISSION_LIMIT=1, JOB_SUBMISSION_TRUST_PROXY_IP=False)
    def test_untrusted_proxy_headers_do_not_change_identity(self):
        self.client.post(reverse("post_job"), {}, HTTP_X_REAL_IP="198.51.100.1")
        self.assertEqual(self.client.post(reverse("post_job"), {}, HTTP_X_REAL_IP="198.51.100.2").status_code, 429)

    @override_settings(JOB_SUBMISSION_LIMIT=1, JOB_SUBMISSION_TRUST_PROXY_IP=True)
    def test_ipv6_privacy_addresses_share_a_limit(self):
        self.client.post(reverse("post_job"), {}, HTTP_X_REAL_IP="2001:db8::1")
        self.assertEqual(self.client.post(reverse("post_job"), {}, HTTP_X_REAL_IP="2001:db8::2").status_code, 429)

    def test_expiring_counter_race_and_storage_failure_are_handled(self):
        from .abuse import SubmissionProtectionUnavailable, submission_rate_exceeded

        request = RequestFactory().post(reverse("post_job"))
        with patch("jobs.abuse.cache.add", side_effect=[False, True]), patch(
            "jobs.abuse.cache.incr", side_effect=ValueError()
        ):
            self.assertFalse(submission_rate_exceeded(request))
        with patch("jobs.abuse.cache.add", side_effect=[False, ConnectionError()]), patch(
            "jobs.abuse.cache.incr", side_effect=ValueError()
        ):
            with self.assertRaises(SubmissionProtectionUnavailable):
                submission_rate_exceeded(request)

    def test_sql_probe_is_stored_as_literal_text_not_executed(self):
        probe = "x' OR 1=(SELECT 1 FROM PG_SLEEP(15))--"
        with patch("jobs.views.async_task"):
            response = self.client.post(reverse("post_job"), {**self.payload, "company_name": probe})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.get().company_name, probe)
        self.assertFalse(Job.objects.get().approved)

    def test_submission_still_requires_csrf(self):
        from django.test import Client

        response = Client(enforce_csrf_checks=True).post(reverse("post_job"), self.payload)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Job.objects.exists())

    @override_settings(JOB_TURNSTILE_ENABLED=True, JOB_TURNSTILE_SITE_KEY="site")
    def test_form_renders_widget_and_uses_full_page_navigation(self):
        response = self.client.get(reverse("post_job"))
        self.assertContains(response, 'data-action="post-job"')
        self.assertContains(response, 'data-size="flexible"')
        self.assertContains(response, 'data-turbo="false"')
        self.assertContains(response, 'name="turbo-visit-control" content="reload"')


class JobSubmissionDigestTests(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def test_burst_schedules_one_digest_without_sending_payloads(self):
        from .tasks import notify_of_new_job

        job = Job.objects.create(title="Engineer", company_name="sql-probe'", listing_url="https://example.com/job")
        with patch("jobs.tasks.send_admin_notification") as send:
            notify_of_new_job(job.pk)
            notify_of_new_job(job.pk)
        from django_q.models import Schedule

        self.assertEqual(Schedule.objects.filter(func="jobs.tasks.send_job_submission_digest").count(), 1)
        send.assert_not_called()

    def test_digest_counts_records_and_excludes_imports_without_raw_payload(self):
        from .tasks import send_job_submission_digest

        now = timezone.now()
        Job.objects.create(title="Engineer", company_name="sql-probe'", listing_url="https://example.com/job")
        Job.objects.create(title="Imported", source="gettjalerts.com", listing_url="https://example.com/import")
        with patch("jobs.tasks.send_admin_notification") as send:
            send_job_submission_digest(
                (now - timedelta(minutes=1)).isoformat(), (now + timedelta(minutes=1)).isoformat()
            )
        self.assertIn("1 job submission", send.call_args.args[1])
        self.assertNotIn("sql-probe", send.call_args.args[1])
