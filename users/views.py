import stripe
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from djstripe import models, settings as djstripe_settings

from builtwithdjango.utils import get_builtwithdjango_logger
from newsletter.views import NewsletterSignupForm

from .forms import CustomUserUpdateForm
from .models import CustomUser

stripe.api_key = djstripe_settings.djstripe_settings.STRIPE_SECRET_KEY
logger = get_builtwithdjango_logger(__name__)


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

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        models.Customer.get_or_create(subscriber=user)
        return initial

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


def create_checkout_session(request, pk):
    user = request.user
    price_id = models.Price.objects.get(nickname="pro").id
    customer = models.Customer.objects.get(subscriber=user)

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer=customer.id,
        success_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse_lazy("update-profile")) + "?status=failed",
        mode="payment",
        line_items=[
            {
                "quantity": 1,
                "price": price_id,
            }
        ],
        allow_promotion_codes=True,
        automatic_tax={"enabled": True},
        customer_update={
            "address": "auto",
        },
        metadata={"pk": pk, "price_id": price_id},
    )

    return redirect(checkout_session.url, code=303)


def resend_email_confirmation_email(request):
    user = request.user
    adapter = get_adapter(request)
    emailaddress = EmailAddress.objects.get_for_user(user, user.email)
    adapter.send_confirmation_mail(request, emailaddress, signup=False)

    return redirect("update-profile")
