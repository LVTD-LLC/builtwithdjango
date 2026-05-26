from allauth.account.signals import email_confirmed, user_signed_up
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from builtwithdjango.analytics import capture, capture_event, get_user_properties
from builtwithdjango.notifications import send_admin_notification
from newsletter.tasks import add_email_to_buttondown


# @receiver(user_signed_up)
def notify_of_new_user(sender, **kwargs):
    message = f"""
      Sender: {sender}
      We have a new user: {kwargs["user"]}
    """
    return send_admin_notification(f"New User: {kwargs['user']}", message)


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    capture(
        request,
        "user signed up",
        distinct_id=str(user.pk),
        properties={
            "$set": get_user_properties(user),
            "signup_method": "allauth",
        },
    )


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    capture(
        request,
        "user logged in",
        distinct_id=str(user.pk),
        properties={
            "$set": get_user_properties(user),
        },
    )


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    if user is None:
        return

    capture(
        request,
        "user logged out",
        distinct_id=str(user.pk),
    )


@receiver(email_confirmed)
def email_confirmation_callback(sender, **kwargs):
    email_address = kwargs["email_address"]
    user = email_address.user
    capture_event(
        "email confirmed",
        distinct_id=str(user.pk),
        properties={
            "$set": get_user_properties(user),
            "email": email_address.email,
        },
    )
    if not settings.DEBUG:
        add_email_to_buttondown(email_address, tag="user")
