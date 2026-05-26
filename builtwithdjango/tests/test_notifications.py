from unittest.mock import patch

import requests
from django.test import SimpleTestCase, override_settings

from builtwithdjango.notifications import AppriseNotificationError, send_admin_notification, send_apprise_notification


class AdminNotificationTests(SimpleTestCase):
    @override_settings(
        APPRISE_API_URL="https://apprise.example.com",
        APPRISE_CONFIG_KEY="builtwithdjango",
        APPRISE_BASIC_AUTH_USER="apprise",
        APPRISE_BASIC_AUTH_PASSWORD="secret",
        APPRISE_NOTIFICATION_FORMAT="markdown",
        APPRISE_REQUEST_TIMEOUT=10,
    )
    @patch("builtwithdjango.notifications.requests.post")
    def test_send_apprise_notification_posts_to_configured_key(self, post):
        post.return_value.raise_for_status.return_value = None

        result = send_apprise_notification("New Project Submission", "Project details")

        self.assertEqual(result, "apprise")
        post.assert_called_once_with(
            "https://apprise.example.com/notify/builtwithdjango",
            json={
                "title": "New Project Submission",
                "body": "Project details",
                "type": "info",
                "format": "markdown",
            },
            auth=("apprise", "secret"),
            timeout=10,
        )

    @override_settings(
        APPRISE_API_URL="https://apprise.example.com",
        APPRISE_CONFIG_KEY="builtwithdjango",
        APPRISE_BASIC_AUTH_USER="",
        APPRISE_BASIC_AUTH_PASSWORD="",
        APPRISE_NOTIFICATION_FORMAT="markdown",
        APPRISE_REQUEST_TIMEOUT=10,
    )
    @patch("builtwithdjango.notifications.requests.post")
    def test_send_apprise_notification_raises_on_request_failure(self, post):
        post.side_effect = requests.RequestException("boom")

        with self.assertRaises(AppriseNotificationError):
            send_apprise_notification("Subject", "Body")

    @override_settings(
        APPRISE_API_URL="",
        APPRISE_CONFIG_KEY="",
        ADMIN_NOTIFICATION_EMAIL_RECIPIENTS=["Built with Django <rasul@builtwithdjango.com>"],
        DEFAULT_FROM_EMAIL="Built with Django <rasul@builtwithdjango.com>",
    )
    @patch("builtwithdjango.notifications.send_mail")
    def test_send_admin_notification_falls_back_to_email_when_apprise_unconfigured(self, send_mail):
        result = send_admin_notification("Subject", "Body")

        self.assertEqual(result, "email")
        send_mail.assert_called_once_with(
            "Subject",
            "Body",
            "Built with Django <rasul@builtwithdjango.com>",
            ["Built with Django <rasul@builtwithdjango.com>"],
            fail_silently=False,
        )

    @override_settings(
        APPRISE_API_URL="https://apprise.example.com",
        APPRISE_CONFIG_KEY="builtwithdjango",
        ADMIN_NOTIFICATION_EMAIL_FALLBACK=False,
    )
    @patch("builtwithdjango.notifications.send_apprise_notification")
    def test_send_admin_notification_can_fail_without_email_fallback(self, send_apprise):
        send_apprise.side_effect = AppriseNotificationError("boom")

        with self.assertRaises(AppriseNotificationError):
            send_admin_notification("Subject", "Body")
