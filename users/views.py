from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from builtwithdjango.analytics import capture
from builtwithdjango.stripe_client import get_or_create_stripe_customer_id

from .forms import CustomUserUpdateForm
from .models import CustomUser

# Authentication is handled by Django Allauth
# See ACCOUNT_FORMS in settings.py for custom form configuration


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

    def form_valid(self, form):
        get_or_create_stripe_customer_id(self.request.user)
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
