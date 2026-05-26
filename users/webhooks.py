"""
Stripe webhook handling for Built with Django.

This module verifies incoming Stripe webhook signatures and processes the
checkout.session.completed events that update local user and job state.
"""

from functools import partial

import stripe
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from builtwithdjango.analytics import capture_event, get_user_properties
from builtwithdjango.stripe_client import configure_stripe, get_stripe_price_id
from builtwithdjango.utils import get_builtwithdjango_logger
from users.models import CustomUser

logger = get_builtwithdjango_logger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request, webhook_uuid=None):
    configure_stripe()

    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET is not configured")
        return HttpResponse(status=500)

    signature = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(request.body, signature, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        logger.warning("Received invalid Stripe webhook payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Received Stripe webhook with invalid signature")
        return HttpResponse(status=400)

    handle_stripe_event(event)

    return HttpResponse(status=200)


def handle_stripe_event(event):
    if event.type == "checkout.session.completed":
        handle_checkout_session_completed(event)
    elif event.type in {
        "customer.subscription.deleted",
        "invoice.payment_failed",
    }:
        process_django_devs_subscription_inactive(event)
    else:
        logger.info(f"Ignoring unhandled Stripe event type: {event.type}")


def handle_checkout_session_completed(event):
    """
    Route successful checkout sessions based on the price_id in metadata.
    """
    checkout_session = event.data["object"]
    event_price_id = (checkout_session.get("metadata") or {}).get("price_id")
    price_nickname = get_checkout_price_nickname(event_price_id)
    checkout_distinct_id = get_checkout_distinct_id(checkout_session, price_nickname)
    logger.info(f"Received checkout.session.completed event for Price ID: {event_price_id}")
    capture_event(
        "stripe checkout completed",
        distinct_id=checkout_distinct_id,
        properties={
            "price_id": event_price_id,
            "stripe_event_id": event.id,
            "stripe_checkout_session_id": checkout_session.get("id"),
            "stripe_customer_id": checkout_session.get("customer"),
            "checkout_mode": checkout_session.get("mode"),
            "amount_total": checkout_session.get("amount_total"),
            "currency": checkout_session.get("currency"),
        },
    )

    if price_nickname == "pro":
        logger.info("Processing PRO user purchase")
        process_pro_user_upgrade(event)
    elif price_nickname == "django_devs":
        logger.info("Processing Django Devs subscription purchase")
        process_django_devs_subscription(event)
    elif price_nickname == "job":
        logger.info("Processing Job Board purchase")
        process_job_board_payment(event)
    else:
        logger.warning(f"Unrecognized price_id in checkout.session.completed: {event_price_id}")


def get_checkout_price_nickname(price_id):
    if not price_id:
        return None

    for nickname in ["pro", "django_devs", "job"]:
        try:
            if price_id == get_stripe_price_id(nickname):
                return nickname
        except ImproperlyConfigured as e:
            logger.error(f"Unable to resolve Stripe price '{nickname}' while routing checkout webhook: {str(e)}")

    return None


def get_checkout_distinct_id(checkout_session, price_nickname):
    metadata = checkout_session.get("metadata") or {}

    if price_nickname == "pro" and metadata.get("pk"):
        return str(metadata["pk"])

    if price_nickname == "django_devs" and metadata.get("user_id"):
        return str(metadata["user_id"])

    if price_nickname == "job" and metadata.get("pk"):
        return f"job:{metadata['pk']}"

    return None


def process_pro_user_upgrade(event):
    if event.type != "checkout.session.completed":
        return

    customer_id = event.data["object"].get("customer")
    logger.info(f"Upgrading Customer: {customer_id}")
    transaction.on_commit(partial(upgrade_user_to_pro, event))


def upgrade_user_to_pro(event):
    user_id = event.data["object"]["metadata"]["pk"]
    logger.info(f"Upgrading user {user_id} to PRO subscription level")

    try:
        user = CustomUser.objects.get(pk=user_id)
        update_user_stripe_customer_id(user, event.data["object"].get("customer"))
        user.subscription_level = "PRO"
        user.save(update_fields=["subscription_level"])
        capture_event(
            "profile upgraded",
            distinct_id=str(user.pk),
            properties={
                "$set": get_user_properties(user),
                "stripe_event_id": event.id,
                "stripe_checkout_session_id": event.data["object"].get("id"),
                "stripe_customer_id": event.data["object"].get("customer"),
            },
        )
        logger.info(f"Successfully upgraded user {user_id} to PRO")
    except CustomUser.DoesNotExist:
        logger.error(f"User {user_id} not found for PRO upgrade")
    except Exception as e:
        logger.error(f"Error upgrading user {user_id} to PRO: {str(e)}")


def process_django_devs_subscription(event):
    if event.type != "checkout.session.completed":
        return

    subscription_id = event.data["object"].get("subscription")
    logger.info(f"Processing Django Devs subscription: {subscription_id}")
    transaction.on_commit(partial(activate_django_devs_subscription, event))


def activate_django_devs_subscription(event):
    user_id = event.data["object"]["metadata"]["user_id"]
    logger.info(f"Activating Django Devs subscription for user {user_id}")

    try:
        user = CustomUser.objects.get(id=user_id)
        update_user_stripe_customer_id(user, event.data["object"].get("customer"))
        user.has_active_django_devs_subscription = True
        user.save(update_fields=["has_active_django_devs_subscription"])
        capture_event(
            "django developers subscription activated",
            distinct_id=str(user.pk),
            properties={
                "$set": get_user_properties(user),
                "stripe_event_id": event.id,
                "stripe_checkout_session_id": event.data["object"].get("id"),
                "stripe_customer_id": event.data["object"].get("customer"),
                "stripe_subscription_id": event.data["object"].get("subscription"),
            },
        )
        logger.info(f"Successfully activated Django Devs subscription for user {user_id}")
    except CustomUser.DoesNotExist:
        logger.error(f"User {user_id} not found for Django Devs subscription activation")
    except Exception as e:
        logger.error(f"Error activating Django Devs subscription for user {user_id}: {str(e)}")


def process_django_devs_subscription_inactive(event):
    stripe_object = event.data["object"]
    try:
        devs_price_id = get_stripe_price_id("django_devs")
    except ImproperlyConfigured as e:
        logger.error(f"Unable to resolve Django Devs Stripe price while processing {event.type}: {str(e)}")
        return

    if not stripe_object_has_price_id(stripe_object, devs_price_id):
        logger.info(f"Ignoring {event.type} for non-Django Devs price")
        return

    customer_id = stripe_object.get("customer")
    if not customer_id:
        logger.warning(f"Ignoring {event.type} without a customer ID")
        return

    logger.info(f"Deactivating Django Devs subscription for customer {customer_id} after {event.type}")
    transaction.on_commit(partial(deactivate_django_devs_subscription, event))


def deactivate_django_devs_subscription(event):
    stripe_object = event.data["object"]
    customer_id = stripe_object.get("customer")

    try:
        user = CustomUser.objects.get(stripe_customer_id=customer_id)
        user.has_active_django_devs_subscription = False
        user.save(update_fields=["has_active_django_devs_subscription"])
        capture_event(
            "django developers subscription deactivated",
            distinct_id=str(user.pk),
            properties={
                "$set": get_user_properties(user),
                "stripe_event_id": event.id,
                "stripe_event_type": event.type,
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": get_stripe_object_subscription_id(stripe_object),
            },
        )
        logger.info(f"Successfully deactivated Django Devs subscription for customer {customer_id}")
    except CustomUser.DoesNotExist:
        logger.error(f"User with Stripe customer {customer_id} not found for Django Devs subscription deactivation")
    except Exception as e:
        logger.error(f"Error deactivating Django Devs subscription for customer {customer_id}: {str(e)}")


def process_job_board_payment(event):
    if event.type != "checkout.session.completed":
        return

    job_id = event.data["object"]["metadata"]["pk"]
    logger.info(f"Processing Job Board payment for job {job_id}")
    transaction.on_commit(partial(approve_paid_job, event))


def approve_paid_job(event):
    from jobs.models import Job

    job_id = event.data["object"]["metadata"]["pk"]
    logger.info(f"Approving paid job {job_id}")

    try:
        job = Job.objects.get(pk=job_id)
        job.paid = True
        job.approved = True
        job.save(update_fields=["paid", "approved"])
        capture_event(
            "job payment completed",
            distinct_id=f"job:{job.id}",
            properties={
                "job_id": job.id,
                "job_title": job.title,
                "job_company_name": job.company.name if job.company else job.company_name,
                "stripe_event_id": event.id,
                "stripe_checkout_session_id": event.data["object"].get("id"),
                "stripe_customer_id": event.data["object"].get("customer"),
            },
            groups={"job": str(job.id)},
        )
        logger.info(f"Successfully approved paid job {job_id}")
    except Job.DoesNotExist:
        logger.error(f"Job {job_id} not found for approval")
    except Exception as e:
        logger.error(f"Error approving job {job_id}: {str(e)}")


def update_user_stripe_customer_id(user, customer_id):
    if not customer_id:
        return

    if user.stripe_customer_id == customer_id:
        return

    if user.stripe_customer_id:
        logger.warning(
            f"User {user.pk} already has Stripe customer {user.stripe_customer_id}; checkout used {customer_id}"
        )
        return

    user.stripe_customer_id = customer_id
    user.save(update_fields=["stripe_customer_id"])


def stripe_object_has_price_id(stripe_object, price_id):
    if get_price_id(stripe_object) == price_id:
        return True

    for collection_name in ["items", "lines"]:
        collection = stripe_object.get(collection_name) or {}
        for item in collection.get("data") or []:
            if get_price_id(item) == price_id:
                return True

    return False


def get_price_id(stripe_object):
    price = stripe_object.get("price")
    if isinstance(price, str):
        return price
    if price:
        return price.get("id")

    pricing = stripe_object.get("pricing") or {}
    price_details = pricing.get("price_details") or {}
    return price_details.get("price")


def get_stripe_object_subscription_id(stripe_object):
    subscription = stripe_object.get("subscription")
    if isinstance(subscription, str):
        return subscription
    if subscription:
        return subscription.get("id")

    return stripe_object.get("id") if stripe_object.get("object") == "subscription" else None
