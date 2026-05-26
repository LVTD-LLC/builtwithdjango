from unittest.mock import patch

from django.test import SimpleTestCase

from builtwithdjango.sentry_utils import sentry_span, sentry_task_transaction


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
