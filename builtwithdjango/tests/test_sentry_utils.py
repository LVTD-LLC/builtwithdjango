from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from builtwithdjango.sentry_utils import sentry_span, sentry_task_transaction, sentry_template_context
from builtwithdjango.settings import sentry_before_send_log


class FakeSpan:
    def __init__(self):
        self.data = {}

    def set_data(self, key, value):
        self.data[key] = value


class FakeSentryContext:
    def __init__(self, *, exit_error=None):
        self.exit_args = None
        self.exit_error = exit_error
        self.span = FakeSpan()

    def __enter__(self):
        return self.span

    def __exit__(self, exc_type, exc, traceback):
        self.exit_args = (exc_type, exc, traceback)
        if self.exit_error:
            raise self.exit_error


class SentryUtilsTests(SimpleTestCase):
    def test_sentry_span_suppresses_sdk_setup_failure(self):
        with patch(
            "builtwithdjango.sentry_utils.sentry_sdk.start_span",
            side_effect=RuntimeError("sentry unavailable"),
        ):
            with sentry_span("http.client", "test") as span:
                self.assertIsNone(span)

    def test_sentry_span_does_not_swallow_application_errors(self):
        sentry_context = FakeSentryContext(exit_error=RuntimeError("sentry exit failed"))

        with patch("builtwithdjango.sentry_utils.sentry_sdk.start_span", return_value=sentry_context):
            with self.assertRaisesMessage(ValueError, "application failed"):
                with sentry_span("http.client", "test"):
                    raise ValueError("application failed")

        self.assertIs(sentry_context.exit_args[0], ValueError)

    def test_sentry_task_transaction_records_clean_attributes(self):
        sentry_context = FakeSentryContext()

        with patch(
            "builtwithdjango.sentry_utils.sentry_sdk.start_transaction",
            return_value=sentry_context,
        ):
            with sentry_task_transaction(
                "projects.tasks.fetch_page_content",
                attributes={"project.id": 1, "empty": None},
            ):
                pass

        self.assertEqual(sentry_context.span.data, {"project.id": 1})


class SentryLogScrubbingTests(SimpleTestCase):
    def test_scrubs_credential_tokens_without_filtering_ai_token_usage(self):
        log = {
            "attributes": {
                "access_token": "secret-token",
                "input_tokens": 25,
                "output_tokens": 10,
                "token_count": 35,
                "total_tokens": 35,
                "user_email": "user@example.com",
            }
        }

        result = sentry_before_send_log(log, {})

        self.assertEqual(result["attributes"]["access_token"], "[Filtered]")
        self.assertEqual(result["attributes"]["user_email"], "[Filtered]")
        self.assertEqual(result["attributes"]["input_tokens"], 25)
        self.assertEqual(result["attributes"]["output_tokens"], 10)
        self.assertEqual(result["attributes"]["token_count"], 35)
        self.assertEqual(result["attributes"]["total_tokens"], 35)


class SentryTemplateContextTests(SimpleTestCase):
    @override_settings(SENTRY_BROWSER_ENABLED=False, SENTRY_BROWSER_DSN="https://public@example.ingest.sentry.io/1")
    def test_browser_context_is_disabled_when_browser_sentry_is_disabled(self):
        request = SimpleNamespace(user=SimpleNamespace(is_authenticated=False))

        context = sentry_template_context(request)

        self.assertFalse(context["sentry_browser_enabled"])
        self.assertEqual(context["sentry_browser_config"], {})

    @override_settings(
        SENTRY_BROWSER_ENABLED=True,
        SENTRY_BROWSER_DSN="https://public@example.ingest.sentry.io/1",
        ENVIRONMENT="prod",
        SENTRY_RELEASE="abc123",
        SENTRY_DIST=None,
        SENTRY_BROWSER_TRACES_SAMPLE_RATE=0.2,
        SENTRY_BROWSER_TRACE_PROPAGATION_TARGETS=["https://builtwithdjango.com"],
        SENTRY_BROWSER_REPLAY_SESSION_SAMPLE_RATE=0.1,
        SENTRY_BROWSER_REPLAY_ERROR_SAMPLE_RATE=1.0,
        SENTRY_BROWSER_SEND_DEFAULT_PII=False,
        SENTRY_BROWSER_ENABLE_LOGS=True,
    )
    def test_browser_context_exposes_runtime_config_without_user_pii_by_default(self):
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_authenticated=True,
                pk=1,
                email="user@example.com",
                username="user",
            )
        )

        context = sentry_template_context(request)

        self.assertTrue(context["sentry_browser_enabled"])
        config = context["sentry_browser_config"]
        self.assertEqual(config["dsn"], "https://public@example.ingest.sentry.io/1")
        self.assertEqual(config["environment"], "prod")
        self.assertEqual(config["release"], "abc123")
        self.assertEqual(config["tracePropagationTargets"], ["https://builtwithdjango.com"])
        self.assertNotIn("user", config)

    @override_settings(
        SENTRY_BROWSER_ENABLED=True,
        SENTRY_BROWSER_DSN="https://public@example.ingest.sentry.io/1",
        ENVIRONMENT="prod",
        SENTRY_RELEASE=None,
        SENTRY_DIST=None,
        SENTRY_BROWSER_TRACES_SAMPLE_RATE=0.2,
        SENTRY_BROWSER_TRACE_PROPAGATION_TARGETS=[],
        SENTRY_BROWSER_REPLAY_SESSION_SAMPLE_RATE=0.1,
        SENTRY_BROWSER_REPLAY_ERROR_SAMPLE_RATE=1.0,
        SENTRY_BROWSER_SEND_DEFAULT_PII=True,
        SENTRY_BROWSER_ENABLE_LOGS=True,
    )
    def test_browser_context_can_include_user_when_browser_pii_is_enabled(self):
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_authenticated=True,
                pk=1,
                email="user@example.com",
                username="user",
            )
        )

        context = sentry_template_context(request)

        self.assertEqual(
            context["sentry_browser_config"]["user"],
            {
                "id": "1",
                "email": "user@example.com",
                "username": "user",
            },
        )
