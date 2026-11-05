"""Abuse controls run before creating records, checkout redirects or queue tasks."""

import ipaddress
import logging
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import salted_hmac

logger = logging.getLogger(__name__)


class SubmissionProtectionUnavailable(Exception):
    pass


def submission_rate_exceeded(request):
    # Only enable this behind a proxy that overwrites X-Real-IP. Never trust
    # caller-controlled X-Forwarded-For or Cloudflare headers at the origin.
    address = request.META.get("REMOTE_ADDR", "")
    if settings.JOB_SUBMISSION_TRUST_PROXY_IP:
        address = request.META.get("HTTP_X_REAL_IP", address)
    try:
        ip = ipaddress.ip_address(address)
        # Group IPv6 privacy addresses so rotating within a /64 cannot bypass.
        identity = str(ipaddress.ip_network(f"{ip}/64", strict=False)) if ip.version == 6 else str(ip)
    except ValueError:
        identity = "unknown"
    key = "jobs:submission:" + salted_hmac("job-submission-ip", identity).hexdigest()
    try:
        if cache.add(key, 1, timeout=settings.JOB_SUBMISSION_WINDOW):
            return False
        try:
            count = cache.incr(key)
        except ValueError:
            # Expiry between add() and incr(): only an atomic add may reset.
            if cache.add(key, 1, timeout=settings.JOB_SUBMISSION_WINDOW):
                return False
            count = cache.incr(key)
        return count > settings.JOB_SUBMISSION_LIMIT
    except Exception:
        logger.warning("Job submission rate-limit storage unavailable")
        raise SubmissionProtectionUnavailable from None


def verify_job_challenge(token):
    if not settings.JOB_TURNSTILE_ENABLED:
        return True
    if not token or len(token) > 2048:
        return False
    if not settings.JOB_TURNSTILE_SITE_KEY or not settings.JOB_TURNSTILE_SECRET_KEY:
        logger.warning("Job submission challenge is not configured")
        return False
    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": settings.JOB_TURNSTILE_SECRET_KEY, "response": token},
            timeout=(3, 5),
        )
        response.raise_for_status()
        result = response.json()
        return (
            isinstance(result, dict)
            and result.get("success") is True
            and result.get("hostname") == urlparse(settings.SITE_URL).hostname
            and result.get("action") == "post-job"
        )
    except (requests.RequestException, ValueError):
        # Do not log tokens, submitted fields, credentials or provider bodies.
        logger.warning("Job submission challenge verification unavailable")
        return False
