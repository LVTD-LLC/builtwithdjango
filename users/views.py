import stripe
from allauth.account.adapter import get_adapter
from allauth.account.internal import flows
from allauth.account.models import EmailAddress
from allauth.account.views import SignupView
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from builtwithdjango.analytics import capture, capture_checkout_return
from builtwithdjango.stripe_client import get_or_create_stripe_customer_id
from builtwithdjango.utils import get_builtwithdjango_logger

from .forms import CustomUserUpdateForm
from .models import CustomUser

# Authentication is handled by Django Allauth
# See ACCOUNT_FORMS in settings.py for custom form configuration

logger = get_builtwithdjango_logger(__name__)

DUPLICATE_SIGNUP_ERRORS = {
    "email": "A user with that email already exists.",
    "username": "A user with that username already exists.",
}


def duplicate_signup_field(error):
    message = str(error).lower()
    if "auth_user_username_key" in message or "auth_user.username" in message:
        return "username"
    if (
        "unique_verified_email" in message
        or "account_emailaddress_email" in message
        or "account_emailaddress.email" in message
    ):
        return "email"
    return None


class CustomSignupView(SignupView):
    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.user, response = form.try_save(self.request)
        except IntegrityError as error:
            field = duplicate_signup_field(error)
            if field is None:
                raise

            form.add_error(field, DUPLICATE_SIGNUP_ERRORS[field])
            logger.warning(f"Rejected duplicate signup {field} after validation: {str(error)}")
            return self.form_invalid(form)

        if response:
            return response

        try:
            redirect_url = self.get_success_url()
            return flows.signup.complete_signup(
                self.request,
                user=self.user,
                redirect_url=redirect_url,
                by_passkey=form.by_passkey,
            )
        except ImmediateHttpResponse as error:
            return error.response


class ProfileUpdateForm(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = "account_login"
    form_class = CustomUserUpdateForm
    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    success_message = "User Profile Updated"
    success_url = reverse_lazy("update-profile")
    template_name = "account/profile-update.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        capture_checkout_return(request, "django_developers")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            get_or_create_stripe_customer_id(self.request.user)
        except (ImproperlyConfigured, stripe.StripeError) as e:
            logger.warning(f"Unable to sync Stripe customer for user {self.request.user.pk}: {str(e)}")

        response = super().form_valid(form)
        capture(
            self.request,
            "profile updated",
            properties={
                "has_profile_image": bool(self.object.profile_image),
                "has_personal_website": bool(self.object.personal_website),
                "has_twitter_handle": bool(self.object.twitter_handle),
                "has_github_handle": bool(self.object.github_handle),
                "has_indiehackers_handle": bool(self.object.indiehackers_handle),
                "make_public": self.object.make_public,
            },
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        emailaddress = EmailAddress.objects.get_for_user(user, user.email)
        email_verified = emailaddress.verified

        context["email_verified"] = email_verified

        return context


class ProfileUpgrade(LoginRequiredMixin, TemplateView):
    login_url = "account_login"
    template_name = "account/upgrade-account.html"


def resend_email_confirmation_email(request):
    user = request.user
    adapter = get_adapter(request)
    emailaddress = EmailAddress.objects.get_for_user(user, user.email)
    adapter.send_confirmation_mail(request, emailaddress, signup=False)
    capture(
        request,
        "email confirmation resent",
        properties={
            "email_verified": emailaddress.verified,
        },
    )

    return redirect("update-profile")
