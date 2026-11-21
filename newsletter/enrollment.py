"""Enroll a verified account without sending a second opt-in message."""
import re

import requests
from allauth.account.models import EmailAddress
from django.conf import settings


def enroll_verified_account(user_id):
    address = EmailAddress.objects.filter(user_id=user_id, primary=True, verified=True).first()
    if not address:
        return
    endpoint = settings.NEWSLETTER_LISTMONK_URL.rstrip("/") + "/api/subscribers"
    list_id = settings.NEWSLETTER_LIST_ID
    payload = {"lists": [list_id], "preconfirm_subscriptions": True}
    with requests.Session() as client:
        client.auth = (settings.NEWSLETTER_API_USER, settings.NEWSLETTER_API_TOKEN)
        created = client.post(endpoint, json={**payload, "email": address.email}, timeout=10)
        if created.ok:
            return
        # Creation is insert-only. Resolve a duplicate by exact address, never by
        # the first fuzzy search result. Do not change subscriber-wide status.
        page = client.get(endpoint, params={"search": f"^{re.escape(address.email)}$"}, timeout=10)
        page.raise_for_status()
        for sub in page.json()["data"]["results"] or []:
            if sub["email"].casefold() != address.email.casefold():
                continue
            if sub["status"] != "enabled":
                return
            for membership in sub["lists"] or []:
                if membership["id"] == list_id and membership["subscription_status"] in {"confirmed", "unsubscribed"}:
                    return
            # The API user has manage permission only on this list. Listmonk
            # preserves out-of-scope memberships and existing unsubscribe state.
            client.patch(f"{endpoint}/{sub['id']}", json=payload, timeout=10).raise_for_status()
            return
        created.raise_for_status()
