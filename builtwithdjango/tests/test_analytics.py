from django.test import RequestFactory, TestCase, override_settings

from builtwithdjango.analytics import posthog_request_filter


class PostHogRequestFilterTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(POSTHOG_ENABLED=True)
    def test_filters_like_api_list_requests(self):
        request = self.factory.get("/api/v1/like/?project=1")

        self.assertFalse(posthog_request_filter(request))

    @override_settings(POSTHOG_ENABLED=True)
    def test_filters_like_api_detail_requests(self):
        request = self.factory.patch("/api/v1/like/12/")

        self.assertFalse(posthog_request_filter(request))

    @override_settings(POSTHOG_ENABLED=True)
    def test_keeps_other_api_requests(self):
        request = self.factory.get("/api/v1/search-projects/?q=django")

        self.assertTrue(posthog_request_filter(request))
