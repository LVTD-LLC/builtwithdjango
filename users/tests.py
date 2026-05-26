from types import SimpleNamespace
from unittest.mock import patch

import stripe
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.urls import reverse

from builtwithdjango.stripe_client import get_or_create_stripe_customer_id, get_stripe_price_id
from jobs.models import Job
from users.webhooks import handle_stripe_event

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


def stripe_subscription_event(event_type, price_id, customer_id="cus_test"):
    return SimpleNamespace(
        id="evt_subscription",
        type=event_type,
        data={
            "object": {
                "id": "sub_test",
                "object": "subscription",
                "customer": customer_id,
                "items": {"data": [{"price": {"id": price_id}}]},
            },
        },
    )


def stripe_invoice_event(event_type, price_id, customer_id="cus_test"):
    return SimpleNamespace(
        id="evt_invoice",
        type=event_type,
        data={
            "object": {
                "id": "in_test",
                "object": "invoice",
                "customer": customer_id,
                "subscription": "sub_test",
                "lines": {"data": [{"price": {"id": price_id}}]},
            },
        },
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
            idempotency_key=f"builtwithdjango:user:{user.pk}:stripe-customer",
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
        self.assertEqual(get_stripe_price_id("job"), "price_configured_job")


class StripeWebhookTests(TestCase):
    def handle_event(self, event):
        with (
            patch("users.webhooks.get_stripe_price_id", side_effect=lambda nickname: PRICE_IDS[nickname]),
            patch("users.webhooks.capture_event"),
            patch("users.webhooks.transaction.on_commit", side_effect=lambda callback: callback()),
        ):
            handle_stripe_event(event)

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

    def test_checkout_session_completed_routes_known_price_when_other_price_is_unconfigured(self):
        user = get_user_model().objects.create_user(username="partial-config-user", email="partial@example.com")
        event = stripe_event(
            "price_devs",
            metadata={"user_id": str(user.pk)},
            customer_id="cus_devs",
            subscription_id="sub_devs",
        )

        def get_price_id(nickname):
            if nickname == "pro":
                raise ImproperlyConfigured("missing pro price")
            return PRICE_IDS[nickname]

        with (
            patch("users.webhooks.get_stripe_price_id", side_effect=get_price_id),
            patch("users.webhooks.capture_event"),
            patch("users.webhooks.transaction.on_commit", side_effect=lambda callback: callback()),
        ):
            handle_stripe_event(event)

        user.refresh_from_db()
        self.assertTrue(user.has_active_django_devs_subscription)
        self.assertEqual(user.stripe_customer_id, "cus_devs")

    def test_checkout_session_completed_ignores_unconfigured_prices_without_raising(self):
        event = stripe_event("price_unknown", metadata={"pk": "1"}, customer_id="cus_unknown")

        with (
            patch(
                "users.webhooks.get_stripe_price_id",
                side_effect=ImproperlyConfigured("missing price"),
            ),
            patch("users.webhooks.capture_event"),
            patch("users.webhooks.transaction.on_commit") as on_commit,
        ):
            handle_stripe_event(event)

        on_commit.assert_not_called()

    def test_checkout_session_completed_ignores_price_lookup_api_failure_without_raising(self):
        event = stripe_event(
            "price_devs", metadata={"user_id": "1"}, customer_id="cus_devs", subscription_id="sub_devs"
        )

        with (
            patch("users.webhooks.get_stripe_price_id", side_effect=stripe.StripeError("stripe api down")),
            patch("users.webhooks.capture_event"),
            patch("users.webhooks.transaction.on_commit") as on_commit,
        ):
            handle_stripe_event(event)

        on_commit.assert_not_called()

    def test_checkout_session_completed_ignores_missing_required_metadata_without_raising(self):
        for price_id in ["price_pro", "price_devs", "price_job"]:
            with self.subTest(price_id=price_id):
                self.handle_event(stripe_event(price_id, metadata={}))

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

    def test_subscription_deleted_deactivates_django_devs_subscription(self):
        user = get_user_model().objects.create_user(
            username="inactive-devs-user",
            email="inactive-devs@example.com",
            stripe_customer_id="cus_devs",
            has_active_django_devs_subscription=True,
        )
        event = stripe_subscription_event("customer.subscription.deleted", "price_devs", customer_id="cus_devs")

        self.handle_event(event)

        user.refresh_from_db()
        self.assertFalse(user.has_active_django_devs_subscription)

    def test_invoice_payment_failed_deactivates_django_devs_subscription(self):
        user = get_user_model().objects.create_user(
            username="failed-devs-user",
            email="failed-devs@example.com",
            stripe_customer_id="cus_devs",
            has_active_django_devs_subscription=True,
        )
        event = stripe_invoice_event("invoice.payment_failed", "price_devs", customer_id="cus_devs")

        self.handle_event(event)

        user.refresh_from_db()
        self.assertFalse(user.has_active_django_devs_subscription)

    def test_invoice_payment_failed_ignores_missing_django_devs_price_config(self):
        user = get_user_model().objects.create_user(
            username="missing-price-devs-user",
            email="missing-price-devs@example.com",
            stripe_customer_id="cus_devs",
            has_active_django_devs_subscription=True,
        )
        event = stripe_invoice_event("invoice.payment_failed", "price_devs", customer_id="cus_devs")

        with (
            patch(
                "users.webhooks.get_stripe_price_id",
                side_effect=ImproperlyConfigured("missing django_devs price"),
            ),
            patch("users.webhooks.capture_event"),
            patch("users.webhooks.transaction.on_commit") as on_commit,
        ):
            handle_stripe_event(event)

        on_commit.assert_not_called()
        user.refresh_from_db()
        self.assertTrue(user.has_active_django_devs_subscription)

    def test_invoice_payment_failed_ignores_stripe_price_lookup_api_failure(self):
        user = get_user_model().objects.create_user(
            username="price-api-failure-devs-user",
            email="price-api-failure-devs@example.com",
            stripe_customer_id="cus_devs",
            has_active_django_devs_subscription=True,
        )
        event = stripe_invoice_event("invoice.payment_failed", "price_devs", customer_id="cus_devs")

        with (
            patch("users.webhooks.get_stripe_price_id", side_effect=stripe.StripeError("stripe api down")),
            patch("users.webhooks.capture_event"),
            patch("users.webhooks.transaction.on_commit") as on_commit,
        ):
            handle_stripe_event(event)

        on_commit.assert_not_called()
        user.refresh_from_db()
        self.assertTrue(user.has_active_django_devs_subscription)

    def test_subscription_lifecycle_ignores_other_prices(self):
        user = get_user_model().objects.create_user(
            username="other-price-user",
            email="other-price@example.com",
            stripe_customer_id="cus_devs",
            has_active_django_devs_subscription=True,
        )
        event = stripe_subscription_event("customer.subscription.deleted", "price_other", customer_id="cus_devs")

        self.handle_event(event)

        user.refresh_from_db()
        self.assertTrue(user.has_active_django_devs_subscription)

    def test_invoice_payment_action_required_does_not_deactivate_subscription(self):
        user = get_user_model().objects.create_user(
            username="auth-required-devs-user",
            email="auth-required-devs@example.com",
            stripe_customer_id="cus_devs",
            has_active_django_devs_subscription=True,
        )
        event = stripe_invoice_event("invoice.payment_action_required", "price_devs", customer_id="cus_devs")

        self.handle_event(event)

        user.refresh_from_db()
        self.assertTrue(user.has_active_django_devs_subscription)


class ProfileUpdateTests(TestCase):
    def test_profile_update_continues_when_stripe_customer_sync_is_unconfigured(self):
        user = get_user_model().objects.create_user(
            username="profile-user",
            email="profile@example.com",
            password="test-password",
        )
        self.client.force_login(user)

        with (
            patch(
                "users.views.get_or_create_stripe_customer_id",
                side_effect=ImproperlyConfigured("missing stripe key"),
            ),
            patch("users.views.capture"),
        ):
            response = self.client.post(
                reverse("update-profile"),
                {
                    "first_name": "Updated",
                    "last_name": "Profile",
                    "personal_website": "https://example.com",
                    "referred_by": "",
                    "twitter_handle": "",
                    "github_handle": "",
                    "indiehackers_handle": "",
                    "email": user.email,
                    "make_public": "on",
                },
            )

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "Profile")
