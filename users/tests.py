from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from jobs.models import Job
from users.webhooks import approve_paid_job, get_checkout_distinct_id, upgrade_user_to_pro


class StripeWebhookTests(TestCase):
    def test_get_checkout_distinct_id_uses_metadata_for_known_checkout_types(self):
        checkout_session = {
            "metadata": {"pk": "10", "user_id": "20"},
        }

        self.assertEqual(
            get_checkout_distinct_id(checkout_session, "price_pro", "price_pro", "price_devs", "price_job"), "10"
        )
        self.assertEqual(
            get_checkout_distinct_id(checkout_session, "price_devs", "price_pro", "price_devs", "price_job"), "20"
        )
        self.assertEqual(
            get_checkout_distinct_id(checkout_session, "price_job", "price_pro", "price_devs", "price_job"),
            "job:10",
        )

    def test_upgrade_user_to_pro_sets_subscription_level(self):
        user = get_user_model().objects.create_user(username="buyer", email="buyer@example.com")
        event = SimpleNamespace(
            id="evt_test",
            data={"object": {"metadata": {"pk": str(user.pk)}, "id": "cs_test", "customer": "cus_test"}},
        )

        with patch("users.webhooks.capture_event") as capture_event:
            upgrade_user_to_pro(event)

        user.refresh_from_db()
        self.assertEqual(user.subscription_level, "PRO")
        capture_event.assert_called_once()

    def test_approve_paid_job_marks_job_paid_and_approved(self):
        job = Job.objects.create(
            title="Django developer",
            listing_url="https://example.com/jobs/django",
            company_name="Example Co",
        )
        event = SimpleNamespace(
            id="evt_test",
            data={"object": {"metadata": {"pk": str(job.pk)}, "id": "cs_test", "customer": "cus_test"}},
        )

        with patch("users.webhooks.capture_event") as capture_event:
            approve_paid_job(event)

        job.refresh_from_db()
        self.assertTrue(job.paid)
        self.assertTrue(job.approved)
        capture_event.assert_called_once()


# Create your tests here.
