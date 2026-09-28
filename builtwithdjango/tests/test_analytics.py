from django.test import RequestFactory, TestCase, override_settings

from builtwithdjango.analytics import posthog_request_filter


class PostHogRequestFilterTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(POSTHOG_ENABLED=True)
    def test_filters_like_api_list_requests_no_trailing_slash(self):
        request = self.factory.get("/api/v1/like?project=1")

        self.assertFalse(posthog_request_filter(request))

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


class AnalyticsReliabilityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(POSTHOG_API_KEY="phc_test")
    def test_browser_cookie_joins_server_identity_and_session(self):
        import json
        from urllib.parse import quote
        from builtwithdjango.analytics import get_request_distinct_id, get_request_session_id

        request = self.factory.get("/projects/")
        request.COOKIES["ph_phc_test_posthog"] = quote(
            json.dumps({"distinct_id": "browser-anonymous-id", "$sesid": [123, "browser-session-id", 100]})
        )
        self.assertEqual(get_request_distinct_id(request), "browser-anonymous-id")
        self.assertEqual(get_request_session_id(request), "browser-session-id")

    @override_settings(POSTHOG_API_KEY="phc_test")
    def test_bad_cookie_cannot_break_request(self):
        from builtwithdjango.analytics import get_request_distinct_id

        for value in ("not-json", "[]", '{"distinct_id":42}', "x" * 10000):
            request = self.factory.get("/")
            request.COOKIES["ph_phc_test_posthog"] = value
            self.assertTrue(get_request_distinct_id(request))

    def test_no_ip_fingerprinting(self):
        from builtwithdjango.analytics import get_request_distinct_id

        first, second = self.factory.get("/"), self.factory.get("/")
        self.assertEqual(get_request_distinct_id(first), get_request_distinct_id(first))
        self.assertNotEqual(get_request_distinct_id(first), get_request_distinct_id(second))

    @override_settings(POSTHOG_ENABLED=True)
    def test_stripe_retries_use_same_event_uuid_but_not_other_events(self):
        from unittest.mock import patch
        from builtwithdjango.analytics import capture_event

        with patch("builtwithdjango.analytics.posthog.capture") as mocked:
            capture_event("stripe checkout completed", {"stripe_event_id": "evt_123"}, "42")
            capture_event("stripe checkout completed", {"stripe_event_id": "evt_123"}, "42")
            capture_event("subscription activated", {"stripe_event_id": "evt_123"}, "42")
        ids = [call.kwargs["uuid"] for call in mocked.call_args_list]
        self.assertEqual(ids[0], ids[1])
        self.assertNotEqual(ids[0], ids[2])

    def test_urls_drop_fragments_credentials_and_private_paths(self):
        from builtwithdjango.analytics import redact_url

        value = redact_url(
            "https://user:secret@example.com/accounts/password/reset/key/private-token/?token=secret#secret"
        )
        self.assertNotIn("secret", value)
        self.assertNotIn("private-token", value)
        self.assertNotIn("user:", value)

    @override_settings(POSTHOG_ENABLED=True)
    def test_form_errors_capture_codes_not_values(self):
        from unittest.mock import patch
        from django import forms
        from django.template.response import TemplateResponse
        from builtwithdjango.analytics import AnalyticsRequestMiddleware

        class Form(forms.Form):
            email = forms.EmailField()

        form = Form({"email": "private-invalid-value"})
        request = self.factory.post("/newsletter/", {"email": "private-invalid-value"})
        response = TemplateResponse(request, "unused.html", {"form": form})
        with patch("builtwithdjango.analytics.capture") as mocked:
            AnalyticsRequestMiddleware(lambda request: response).process_template_response(request, response)
        self.assertEqual(mocked.call_args.args[1], "form validation failed")
        self.assertNotIn("private-invalid-value", str(mocked.call_args))
        self.assertEqual(mocked.call_args.kwargs["properties"]["error_codes"], {"email": ["invalid"]})

    def test_middleware_paths_are_scrubbed_recursively(self):
        from builtwithdjango.analytics import posthog_before_send

        result = posthog_before_send(
            {
                "properties": {
                    "$request_path": "/accounts/reset/private-token/",
                    "$set_once": {"$initial_current_url": "https://example.com/?token=secret#secret"},
                }
            }
        )
        self.assertNotIn("private-token", str(result))
        self.assertNotIn("secret", str(result))
