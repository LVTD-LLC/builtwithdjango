from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import FeaturePurchase, Project
from .placement import PAYMENT_LINK, fulfill_feature, project_reference
from .querysets import with_like_metadata


class PlacementTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Example", url="https://example.org", published=True)
        self.session = {
            "id": "cs_one", "client_reference_id": project_reference(self.project.pk),
            "mode": "payment", "payment_status": "paid", "amount_total": 29900, "currency": "usd",
        }

    def test_only_paid_checkouts_extend_once(self):
        fulfill_feature(dict(self.session, payment_status="unpaid"))
        self.assertFalse(FeaturePurchase.objects.exists())
        fulfill_feature(self.session)
        self.project.refresh_from_db()
        first_end = self.project.featured_until
        fulfill_feature(self.session)
        fulfill_feature(dict(self.session, id="cs_two"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.featured_until, first_end + timedelta(days=7))
        self.assertEqual(FeaturePurchase.objects.filter(newsletter_feature_sent=False).count(), 2)
        listings = with_like_metadata(Project.objects.all(), None)
        self.assertTrue(listings.get().is_featured)
        Project.objects.update(featured_until=timezone.now() - timedelta(seconds=1))
        self.assertFalse(listings.get().is_featured)

    def test_checkout_is_bound_to_public_project(self):
        url = reverse("feature_project", args=[self.project.slug])
        expected = f"{PAYMENT_LINK}?client_reference_id={project_reference(self.project.pk)}"
        self.assertRedirects(self.client.post(url), expected, fetch_redirect_response=False)
        Project.objects.update(published=False)
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_unattributed_payment_is_queued_for_reconciliation(self):
        fulfill_feature(dict(self.session, client_reference_id="1_tampered"))
        self.assertIsNone(FeaturePurchase.objects.get().project_id)
        self.project.refresh_from_db()
        self.assertIsNone(self.project.featured_until)
