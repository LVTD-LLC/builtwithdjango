import stripe
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction

PRICE_ID_SETTINGS = {
    "pro": "STRIPE_PRO_PRICE_ID",
    "django_devs": "STRIPE_DJANGO_DEVS_PRICE_ID",
    "job": "STRIPE_JOB_PRICE_ID",
}


def configure_stripe():
    if not settings.STRIPE_SECRET_KEY:
        raise ImproperlyConfigured("STRIPE_SECRET_KEY is empty. Set STRIPE_TEST_SECRET_KEY or STRIPE_LIVE_SECRET_KEY.")

    stripe.api_key = settings.STRIPE_SECRET_KEY


def get_stripe_price_id(nickname):
    setting_name = PRICE_ID_SETTINGS.get(nickname)
    if setting_name is None:
        raise ImproperlyConfigured(f"Unknown Stripe price nickname: {nickname}")

    configure_stripe()
    configured_price_id = getattr(settings, setting_name, "")
    if configured_price_id:
        return configured_price_id

    for price in stripe.Price.list(limit=100).auto_paging_iter():
        if price.get("nickname") == nickname:
            return price.id

    raise ImproperlyConfigured(
        f"Could not find a Stripe Price with nickname '{nickname}'. Set {setting_name} to avoid runtime lookup."
    )


def get_or_create_stripe_customer_id(user):
    configure_stripe()

    if user.stripe_customer_id:
        return user.stripe_customer_id

    with transaction.atomic():
        locked_user = user.__class__.objects.select_for_update().get(pk=user.pk)
        if locked_user.stripe_customer_id:
            user.stripe_customer_id = locked_user.stripe_customer_id
            return locked_user.stripe_customer_id

        customer_kwargs = get_stripe_customer_kwargs(locked_user)

    customer = stripe.Customer.create(
        **customer_kwargs,
        idempotency_key=f"builtwithdjango:user:{user.pk}:stripe-customer",
    )

    updated = user.__class__.objects.filter(pk=user.pk, stripe_customer_id="").update(stripe_customer_id=customer.id)
    if not updated:
        user.refresh_from_db(fields=["stripe_customer_id"])
        return user.stripe_customer_id

    user.stripe_customer_id = customer.id
    return customer.id


def get_stripe_customer_kwargs(user):
    customer_kwargs = {
        "metadata": {"user_id": str(user.pk)},
    }
    if user.email:
        customer_kwargs["email"] = user.email

    name = user.get_full_name() or user.username
    if name:
        customer_kwargs["name"] = name

    return customer_kwargs
