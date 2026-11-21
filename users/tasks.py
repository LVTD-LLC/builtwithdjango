from allauth.account.signals import email_confirmed, user_signed_up
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.mail import send_mail
from django.db import transaction
from django.dispatch import receiver
from django_q.tasks import async_task

from builtwithdjango.analytics import capture, capture_event, get_user_properties


def queue_newsletter_enrollment(user_id):
    if settings.NEWSLETTER_LIST_ID:
        transaction.on_commit(lambda: async_task("newsletter.enrollment.enroll_verified_account", user_id))



# @receiver(user_signed_up)
def notify_of_new_user(sender, **kwargs):
    message = f"""
      Sender: {sender}
      We have a new user: {kwargs["user"]}
    """
    send_mail(
        f"New User: {kwargs['user']}",
        message,
        "Built with Django <rasul@builtwithdjango.com>",
        ["Built with Django <rasul@builtwithdjango.com>"],
        fail_silently=False,
    )


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    # Social providers may supply a verified address at signup.
    queue_newsletter_enrollment(user.pk)
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
    queue_newsletter_enrollment(user.pk)
