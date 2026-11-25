from datetime import timedelta

from django.utils.crypto import constant_time_compare, salted_hmac
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import FeaturePurchase, Project

PRICE_KEY = "bwd_project_feature_week"


PAYMENT_LINK = "https://buy.stripe.com/7sY00k2IG0a7b2bcYX8g002"


@require_POST
def feature_project(request, slug):
    project = get_object_or_404(Project, slug=slug, active=True, published=True, might_be_spam=False)
    reference = project_reference(project.pk)
    return HttpResponseRedirect(f"{PAYMENT_LINK}?client_reference_id={reference}")


def project_reference(project_id):
    signature = salted_hmac(PRICE_KEY, str(project_id), algorithm="sha256").hexdigest()
    return f"{project_id}_{signature}"


@transaction.atomic
def fulfill_feature(session):
    if (session.get("payment_status"), session.get("mode"), session.get("amount_total"), session.get("currency")) != (
        "paid", "payment", 29900, "usd"
    ):
        return
    reference = session.get("client_reference_id") or ""
    project_id = reference.partition("_")[0]
    if not project_id.isdecimal() or not constant_time_compare(reference, project_reference(project_id)):
        FeaturePurchase.objects.get_or_create(session_id=session["id"])
        return
    project = Project.objects.select_for_update().filter(pk=project_id).first()
    if project is None:
        FeaturePurchase.objects.get_or_create(session_id=session["id"])
        return
    _, created = FeaturePurchase.objects.get_or_create(session_id=session["id"], defaults={"project": project})
    if created:
        now = timezone.now()
        project.featured_until = max(now, project.featured_until or now) + timedelta(days=7)
        project.save(update_fields=["featured_until"])
