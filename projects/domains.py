"""Project URL identity; paths, schemes, ports and www do not make new sites."""

import ipaddress
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

DUPLICATE_DOMAIN_MESSAGE = (
    "A project with this domain has already been submitted. "
    "Please link directly to your project's own website, not a portfolio or advertising page."
)


def project_domain(url):
    URLValidator(schemes=["http", "https"])(url)
    hostname = urlsplit(url).hostname
    if not hostname:
        raise ValidationError("Enter a valid website URL.")
    hostname = hostname.rstrip(".").encode("idna").decode("ascii").lower()
    try:
        return ipaddress.ip_address(hostname).compressed
    except ValueError:
        # Keep genuine subdomains separate (including hosted app subdomains).
        return hostname.removeprefix("www.")
