from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Job
from .tasks import get_latest_jobs_from_tj_alerts
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
        price = SimpleNamespace(id="price_job")
        checkout_session = SimpleNamespace(id="cs_test", url="https://checkout.stripe.test/session")

        with (
            patch("jobs.views.models.Price.objects.get", return_value=price) as get_price,
            patch("jobs.views.stripe.checkout.Session.create", return_value=checkout_session) as create_session,
            patch("jobs.views.capture") as capture,
        ):
            response = self.client.get(reverse("stripe_checkout_session", kwargs={"pk": job.pk}))

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response["Location"], checkout_session.url)
        get_price.assert_called_once_with(nickname="job")
        create_session.assert_called_once()
        self.assertEqual(create_session.call_args.kwargs["metadata"], {"pk": job.pk, "price_id": "price_job"})
        capture.assert_called_once()

    def test_sponsor_job_checkout_session_redirects_to_stripe_checkout(self):
        job = Job.objects.create(
            title="Sponsored Django developer",
            listing_url="https://example.com/jobs/sponsored-django",
            company_name="Example Co",
        )
        price = SimpleNamespace(id="price_job")
        checkout_session = SimpleNamespace(id="cs_sponsor_test", url="https://checkout.stripe.test/sponsor")

        with (
            patch("jobs.views.models.Price.objects.get", return_value=price) as get_price,
            patch("jobs.views.stripe.checkout.Session.create", return_value=checkout_session) as create_session,
            patch("jobs.views.capture") as capture,
        ):
            response = self.client.get(reverse("sponsor_job_checkout", kwargs={"pk": job.pk}))

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response["Location"], checkout_session.url)
        get_price.assert_called_once_with(nickname="job")
        create_session.assert_called_once()
        self.assertEqual(create_session.call_args.kwargs["metadata"], {"pk": job.pk, "price_id": "price_job"})
        capture.assert_called_once()


class JobImportTaskTests(TestCase):
    def test_get_latest_jobs_from_tj_alerts_imports_new_jobs_and_skips_duplicates(self):
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
        ):
            result = get_latest_jobs_from_tj_alerts()

        self.assertEqual(result, "1 jobs were created.")
        self.assertEqual(Job.objects.filter(source="gettjalerts.com").count(), 2)
        new_job = Job.objects.get(external_id="new")
        self.assertEqual(new_job.email, "new@example.com")
        self.assertTrue(new_job.approved)
        self.assertEqual(get.call_args_list[0].kwargs["timeout"], 30)
        upload.assert_called_once()
