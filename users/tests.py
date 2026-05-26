from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from builtwithdjango.stripe_client import get_or_create_stripe_customer_id, get_stripe_price_id
from jobs.models import Job
from users.webhooks import handle_checkout_session_completed

PRICE_IDS = {
    "pro": "price_pro",
    "django_devs": "price_devs",
    "job": "price_job",
}


def stripe_event(price_id, metadata, customer_id="cus_test", subscription_id=None):
    checkout_session = {
        "id": "cs_test",
        "customer": customer_id,
        "metadata": {**metadata, "price_id": price_id},
        "mode": "subscription" if subscription_id else "payment",
        "amount_total": 1000,
        "currency": "usd",
    }
    if subscription_id:
        checkout_session["subscription"] = subscription_id

    return SimpleNamespace(
        id="evt_test",
        type="checkout.session.completed",
        data={"object": checkout_session},
    )


class StripeCustomerTests(TestCase):
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")
    def test_get_or_create_stripe_customer_id_creates_and_stores_customer(self):
        user = get_user_model().objects.create_user(
            username="stripe-user",
            email="stripe@example.com",
            first_name="Stripe",
            last_name="User",
        )

        with patch(
            "builtwithdjango.stripe_client.stripe.Customer.create",
            return_value=SimpleNamespace(id="cus_created"),
        ) as create_customer:
            customer_id = get_or_create_stripe_customer_id(user)

        self.assertEqual(customer_id, "cus_created")
        user.refresh_from_db()
        self.assertEqual(user.stripe_customer_id, "cus_created")
        create_customer.assert_called_once_with(
            metadata={"user_id": str(user.pk)},
            email="stripe@example.com",
            name="Stripe User",
        )

    @override_settings(STRIPE_SECRET_KEY="sk_test_123")
    def test_get_or_create_stripe_customer_id_reuses_existing_customer(self):
        user = get_user_model().objects.create_user(
            username="existing-stripe-user",
            email="existing@example.com",
            stripe_customer_id="cus_existing",
        )

        with patch("builtwithdjango.stripe_client.stripe.Customer.create") as create_customer:
            customer_id = get_or_create_stripe_customer_id(user)

        self.assertEqual(customer_id, "cus_existing")
        create_customer.assert_not_called()

    @override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_JOB_PRICE_ID="price_configured_job")
    def test_get_stripe_price_id_uses_configured_price_id(self):
        get_stripe_price_id.cache_clear()
        try:
            self.assertEqual(get_stripe_price_id("job"), "price_configured_job")
        finally:
            get_stripe_price_id.cache_clear()


class StripeWebhookTests(TestCase):
    def handle_event(self, event):
        with (
            patch("users.webhooks.get_stripe_price_id", side_effect=lambda nickname: PRICE_IDS[nickname]),
            patch("users.webhooks.capture_event"),
            patch("users.webhooks.transaction.on_commit", side_effect=lambda callback: callback()),
        ):
            handle_checkout_session_completed(event)

    def test_checkout_session_completed_activates_django_devs_subscription(self):
        user = get_user_model().objects.create_user(username="devs-user", email="devs@example.com")
        event = stripe_event(
            "price_devs",
            metadata={"user_id": str(user.pk)},
            customer_id="cus_devs",
            subscription_id="sub_devs",
        )

        self.handle_event(event)

        user.refresh_from_db()
        self.assertTrue(user.has_active_django_devs_subscription)
        self.assertEqual(user.stripe_customer_id, "cus_devs")

    def test_checkout_session_completed_upgrades_user_to_pro(self):
        user = get_user_model().objects.create_user(username="pro-user", email="pro@example.com")
        event = stripe_event("price_pro", metadata={"pk": str(user.pk)}, customer_id="cus_pro")

        self.handle_event(event)

        user.refresh_from_db()
        self.assertEqual(user.subscription_level, "PRO")
        self.assertEqual(user.stripe_customer_id, "cus_pro")

    def test_checkout_session_completed_approves_paid_job(self):
        job = Job.objects.create(
            title="Django developer",
            listing_url="https://example.com/jobs/django-developer",
            company_name="Example Co",
            approved=False,
            paid=False,
        )
        event = stripe_event("price_job", metadata={"pk": str(job.pk)}, customer_id="cus_job")

        self.handle_event(event)

        job.refresh_from_db()
        self.assertTrue(job.approved)
        self.assertTrue(job.paid)
