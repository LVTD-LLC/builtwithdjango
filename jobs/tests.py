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

        with patch("jobs.views.timezone.now", return_value=now):
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
