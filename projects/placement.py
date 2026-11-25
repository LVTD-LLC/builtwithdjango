from datetime import timedelta

import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from builtwithdjango.stripe_client import configure_stripe
from .models import FeaturePurchase, Project

PRICE_KEY = "bwd_project_feature_week"


@require_POST
def feature_project(request, slug):
    project = get_object_or_404(Project, slug=slug, active=True, published=True, might_be_spam=False)
    configure_stripe()
    prices = stripe.Price.list(active=True, lookup_keys=[PRICE_KEY], limit=1).data
    if not prices or prices[0].unit_amount != 29900 or prices[0].currency != "usd":
        return HttpResponse("Featured checkout is temporarily unavailable.", status=503)
    detail = settings.SITE_URL.rstrip("/") + project.get_absolute_url()
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[{"price": prices[0].id, "quantity": 1}],
        metadata={"offer": PRICE_KEY, "project_id": str(project.pk)},
        success_url=detail + "?feature=received",
        cancel_url=detail,
    )
    return HttpResponseRedirect(session.url)


@transaction.atomic
def fulfill_feature(session):
    if (session.get("payment_status"), session.get("mode"), session.get("amount_total"), session.get("currency")) != (
        "paid", "payment", 29900, "usd"
    ):
        return
    project = Project.objects.select_for_update().get(pk=session["metadata"]["project_id"])
    _, created = FeaturePurchase.objects.get_or_create(session_id=session["id"], defaults={"project": project})
    if created:
        now = timezone.now()
        project.featured_until = max(now, project.featured_until or now) + timedelta(days=7)
        project.save(update_fields=["featured_until"])
