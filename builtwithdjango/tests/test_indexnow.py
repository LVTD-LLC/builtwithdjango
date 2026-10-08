import io
import json
import re
from urllib.error import HTTPError, URLError

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse

from builtwithdjango import indexnow

SITE = "https://example.com"
KEY = "a" * 64


class Response(io.BytesIO):
    def __init__(self, body=b"", status=200, headers=None):
        super().__init__(body)
        self.status = status
        self.headers = headers or {}


def transport(monkeypatch, urls, statuses=(200,), revisions=("new",)):
    posts = []
    codes = iter(statuses)
    deployed = iter(revisions)
    xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += "".join(f"<url><loc>{url}</loc></url>" for url in urls) + "</urlset>"

    def send(req, timeout):
        assert timeout > 0
        if req.full_url == SITE + indexnow.KEY_PATH:
            return Response(KEY.encode(), headers={"X-Deployment-Revision": next(deployed)})
        if req.full_url == SITE + "/sitemap.xml":
            return Response(xml.encode())
        assert req.full_url == indexnow.ENDPOINT
        posts.append(json.loads(req.data))
        code = next(codes)
        if code >= 400:
            raise HTTPError(req.full_url, code, "failure", {}, None)
        return Response(status=code)

    monkeypatch.setattr(indexnow, "urlopen", send)
    monkeypatch.setattr(indexnow.time, "sleep", lambda _: None)
    return posts


@override_settings(SITE_URL=SITE, SECRET_KEY="test-only", DEPLOYMENT_REVISION="new")
def test_public_key_route_is_stable_across_settings_changes(client, settings):
    response = client.get(reverse("indexnow_key"))
    assert response.status_code == 200
    assert re.fullmatch(rb"[a-f0-9]{64}", response.content)
    assert response["Content-Type"] == "text/plain; charset=utf-8"
    assert response["Cache-Control"] == "no-store"
    assert response["X-Deployment-Revision"] == "new"
    assert client.get(reverse("indexnow_key")).content == response.content
    assert response.content.decode() == settings.INDEXNOW_KEY
    settings.SECRET_KEY = "rotated-test-only"
    settings.SITE_URL = "https://another.example.com"
    assert client.get(reverse("indexnow_key")).content == response.content


@pytest.mark.parametrize("status", [200, 202])
@override_settings(SITE_URL=SITE)
def test_command_submits_current_and_removed_urls(monkeypatch, tmp_path, status):
    posts = transport(monkeypatch, [SITE + "/", SITE + "/docs/new/"], statuses=(status,))
    previous = tmp_path / "before.json"
    previous.write_text(json.dumps([SITE + "/", SITE + "/docs/removed/"]))
    output = io.StringIO()
    call_command("submit_indexnow", previous=previous, stdout=output)
    assert posts == [
        {
            "host": "example.com",
            "key": KEY,
            "keyLocation": SITE + indexnow.KEY_PATH,
            "urlList": [SITE + "/", SITE + "/docs/new/", SITE + "/docs/removed/"],
        }
    ]
    assert ("validation pending" in output.getvalue()) == (status == 202)


def test_revision_wait_dry_run_and_protocol_batch_limit(monkeypatch):
    urls = [f"{SITE}/docs/{i}/" for i in range(10_001)]
    posts = transport(monkeypatch, urls, statuses=(200, 202), revisions=("old", "new", "new"))
    assert "Dry run" in indexnow.submit(SITE, expected_revision="new", dry_run=True)
    assert not posts
    indexnow.submit(SITE, expected_revision="new")
    assert [len(post["urlList"]) for post in posts] == [10_000, 1]


@pytest.mark.parametrize(
    "url",
    [
        "https://other.test/",
        SITE + "/?token=private",
        SITE + "/#part",
        "http://example.com/",
        SITE + "/bad\npath",
    ],
)
def test_invalid_sitemap_never_submits(monkeypatch, url):
    posts = transport(monkeypatch, [url])
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit(SITE)
    assert not posts


@pytest.mark.parametrize("status", [400, 403, 422, 429])
def test_permanent_or_unspecified_rate_limit_stops(monkeypatch, status):
    posts = transport(monkeypatch, [SITE + "/"], statuses=(status,))
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit(SITE)
    assert len(posts) == 1


def test_transient_failure_retries_and_exhaustion_is_visible(monkeypatch):
    posts = transport(monkeypatch, [SITE + "/"], statuses=(503, 200))
    assert "HTTP 200" in indexnow.submit(SITE)
    assert len(posts) == 2
    attempts = []

    def unavailable(req, timeout):
        attempts.append(req)
        raise URLError("offline")

    monkeypatch.setattr(indexnow, "urlopen", unavailable)
    with pytest.raises(indexnow.IndexNowError, match="four attempts"):
        indexnow.submit(SITE)
    assert len(attempts) == 4


def test_snapshot_cli_is_read_only(monkeypatch, tmp_path):
    posts = transport(monkeypatch, [SITE + "/"])
    snapshot = tmp_path / "before.json"
    monkeypatch.setattr("sys.argv", ["indexnow", "--site-url", SITE, "--snapshot", str(snapshot)])
    indexnow.main()
    assert json.loads(snapshot.read_text()) == [SITE + "/"]
    assert not posts


def test_unfinished_rollout_never_submits(monkeypatch):
    posts = transport(monkeypatch, [SITE + "/"], revisions=("old",) * 30)
    with pytest.raises(indexnow.IndexNowError, match="revision"):
        indexnow.submit(SITE, expected_revision="new")
    assert not posts


def test_short_rate_limit_respects_retry_after(monkeypatch):
    responses = iter([HTTPError(indexnow.ENDPOINT, 429, "rate limit", {"Retry-After": "12"}, None), Response()])
    delays = []

    def send(req, timeout):
        result = next(responses)
        if isinstance(result, HTTPError):
            raise result
        return result

    monkeypatch.setattr(indexnow, "urlopen", send)
    monkeypatch.setattr(indexnow.time, "sleep", delays.append)
    assert indexnow.request(indexnow.ENDPOINT, {"urlList": [SITE + "/"]})[0] == 200
    assert delays == [12]


def test_incremental_checkpoint_new_removed_changed_and_unchanged(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({SITE + "/old/": "1", SITE + "/edit/": "1", SITE + "/": "1"}))
    posts = transport(monkeypatch, [SITE + "/"], revisions=("new", "new"))
    current = {SITE + "/new/": "2", SITE + "/edit/": "2", SITE + "/": "1"}
    monkeypatch.setattr(indexnow, "sitemap_state", lambda _: current)
    assert "HTTP 200" in indexnow.submit_changes(SITE, state)
    assert posts[0]["urlList"] == [SITE + "/edit/", SITE + "/new/", SITE + "/old/"]
    assert json.loads(state.read_text()) == current
    assert "No changed" in indexnow.submit_changes(SITE, state)
    assert len(posts) == 1


def test_incremental_failure_and_dry_run_preserve_checkpoint(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text("{}")
    posts = transport(monkeypatch, [SITE + "/"], statuses=(403,), revisions=("new", "new"))
    assert "Dry run" in indexnow.submit_changes(SITE, state, dry_run=True)
    assert state.read_text() == "{}"
    assert not posts
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit_changes(SITE, state)
    assert state.read_text() == "{}"


def test_incremental_missing_checkpoint_submits_baseline(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    posts = transport(monkeypatch, [SITE + "/"])
    indexnow.submit_changes(SITE, state)
    assert posts[0]["urlList"] == [SITE + "/"]
    assert json.loads(state.read_text()) == {SITE + "/": ""}


def test_paginated_sitemap_index_and_empty_optional_section(monkeypatch):
    namespace = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
    documents = {
        SITE
        + "/sitemap.xml": (
            f"<sitemapindex {namespace}><sitemap><loc>{SITE}/repos.xml</loc></sitemap>"
            f"<sitemap><loc>{SITE}/repos.xml?p=2</loc></sitemap>"
            f"<sitemap><loc>{SITE}/empty.xml</loc></sitemap></sitemapindex>"
        ),
        SITE
        + "/repos.xml": (
            f"<urlset {namespace}><url><loc>{SITE}/first/</loc>"
            "<lastmod>2026-10-08T09:30:00+00:00</lastmod></url></urlset>"
        ),
        SITE + "/repos.xml?p=2": (f"<urlset {namespace}><url><loc>{SITE}/second/</loc></url></urlset>"),
        SITE + "/empty.xml": f"<urlset {namespace}></urlset>",
    }
    monkeypatch.setattr(indexnow, "request", lambda url: (200, documents[url].encode(), {}))
    assert indexnow.sitemap_state(SITE) == {
        SITE + "/first/": "2026-10-08T09:30:00+00:00",
        SITE + "/second/": "",
    }


@pytest.mark.parametrize("child", ["https://foreign.test/sitemap.xml", SITE + "/sitemap.xml"])
def test_foreign_or_cyclic_sitemap_fails_closed(monkeypatch, child):
    body = (
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<sitemap><loc>{child}</loc></sitemap></sitemapindex>"
    ).encode()
    calls = []

    def request(url):
        calls.append(url)
        return 200, body, {}

    monkeypatch.setattr(indexnow, "request", request)
    with pytest.raises(indexnow.IndexNowError):
        indexnow.sitemap_state(SITE)
    assert calls == [SITE + "/sitemap.xml"]


def test_failed_child_sitemap_preserves_checkpoint(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({SITE + "/old/": "1"}))
    original = state.read_text()
    posts = transport(monkeypatch, [SITE + "/"])
    body = (
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<sitemap><loc>{SITE}/broken.xml</loc></sitemap></sitemapindex>"
    ).encode()
    monkeypatch.setattr(indexnow, "deployment_key", lambda *args: KEY)

    def request(url):
        if url.endswith("/sitemap.xml"):
            return 200, body, {}
        raise indexnow.IndexNowError("Sitemap unavailable")

    monkeypatch.setattr(indexnow, "request", request)
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit_changes(SITE, state)
    assert state.read_text() == original
    assert not posts


def test_deployment_force_resubmits_unchanged_urls(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({SITE + "/": ""}))
    posts = transport(monkeypatch, [SITE + "/"])
    indexnow.submit_changes(SITE, state, force=True)
    assert posts[0]["urlList"] == [SITE + "/"]


def test_sitemap_serializes_full_timestamps():
    from datetime import UTC, datetime

    from django.template.loader import render_to_string

    content = render_to_string(
        "sitemap.xml",
        {"urlset": [{"location": SITE + "/", "lastmod": datetime(2026, 10, 8, 9, 30, tzinfo=UTC)}]},
    )
    assert "<lastmod>2026-10-08T09:30:00+00:00</lastmod>" in content


def test_partial_batch_failure_preserves_checkpoint(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text("{}")
    urls = [f"{SITE}/repo/{i}/" for i in range(10_001)]
    posts = transport(monkeypatch, urls, statuses=(200, 403))
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit_changes(SITE, state)
    assert [len(post["urlList"]) for post in posts] == [10_000, 1]
    assert state.read_text() == "{}"


def test_hourly_run_retries_failed_deployment_revision(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({SITE + "/": "old:"}))
    posts = transport(monkeypatch, [SITE + "/"], statuses=(403, 200), revisions=("new", "new", "new"))
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit_changes(SITE, state, expected_revision="new", force=True)
    assert json.loads(state.read_text()) == {SITE + "/": "old:"}
    indexnow.submit_changes(SITE, state, expected_revision="new")
    assert len(posts) == 2
    assert json.loads(state.read_text()) == {SITE + "/": "new:"}
    assert "No changed" in indexnow.submit_changes(SITE, state, expected_revision="new")


@pytest.mark.django_db
def test_public_project_edit_advances_sitemap_timestamp(client):
    from datetime import timedelta
    from xml.etree import ElementTree

    from django.utils import timezone

    from projects.models import Project

    project = Project.objects.create(
        title="IndexNow sample",
        slug="indexnow-sample",
        url="https://example.com",
        published=True,
        active=True,
        might_be_spam=False,
    )
    earlier = timezone.now() - timedelta(hours=1)
    Project.objects.filter(pk=project.pk).update(updated_date=earlier)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def lastmod():
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        tree = ElementTree.fromstring(response.content)
        for node in tree.findall("s:url", ns):
            if node.findtext("s:loc", namespaces=ns).endswith(project.get_absolute_url()):
                return node.findtext("s:lastmod", namespaces=ns)
        return None

    before = lastmod()
    project.description = "Updated public description"
    project.save()
    after = lastmod()
    assert before != after
    assert "T" in after
    project.published = False
    project.save()
    assert lastmod() is None
