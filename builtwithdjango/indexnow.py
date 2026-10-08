"""IndexNow transport and deploy CLI; only Python's standard library is required."""

import argparse
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree

ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_PATH = "/indexnow-key.txt"
MAX_BYTES = 5_000_000


class IndexNowError(Exception):
    pass


def request(url, payload=None):
    """Bound network waits and retry transient failures, never permanent errors."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "BuiltWithDjango-IndexNow/1.0"},
    )
    for attempt in range(4):
        try:
            with urlopen(req, timeout=20) as response:
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    raise IndexNowError("Response exceeds size limit")
                return response.status, body, response.headers
        except HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise IndexNowError(f"HTTP {error.code}; check the key and submitted URLs") from None
            retry_after = error.headers.get("Retry-After", "")
            # Long rate limits must be retried later, not ignored or shortened.
            if error.code == 429 and (not retry_after.isdigit() or int(retry_after) > 60):
                raise IndexNowError("Rate limited; retry this submission later") from None
            delay = int(retry_after) if retry_after.isdigit() else 2**attempt
        except (URLError, TimeoutError, OSError):
            delay = 2**attempt
        if attempt < 3:
            time.sleep(min(delay, 60))
    raise IndexNowError("Network request failed after four attempts")


def validate_urls(site_url, urls):
    origin = urlsplit(site_url)
    if (
        origin.scheme != "https"
        or not origin.hostname
        or origin.path
        or origin.query
        or origin.fragment
        or origin.username
    ):
        raise IndexNowError("Site URL must be a bare HTTPS origin")
    if not isinstance(urls, list) or any(not isinstance(url, str) for url in urls):
        raise IndexNowError("URL list must contain strings")
    for url in urls:
        parsed = urlsplit(url)
        if (
            parsed.scheme != origin.scheme
            or parsed.netloc != origin.netloc
            or parsed.fragment
            or parsed.query
            or any(char.isspace() or ord(char) < 32 for char in url)
        ):
            raise IndexNowError("Only canonical URLs on the configured origin may be submitted")
    return sorted(set(urls))


def read_sitemap_document(url):
    status, body, _ = request(url)
    if status != 200:
        raise IndexNowError(f"Sitemap returned HTTP {status}")
    try:
        return ElementTree.fromstring(body)
    except ElementTree.ParseError:
        raise IndexNowError("Invalid sitemap XML") from None


def sitemap_state(site_url):
    """Read all pages before computing removals; reject incomplete/foreign maps."""
    validate_urls(site_url, [])
    pending = [f"{site_url}/sitemap.xml"]
    visited = set()
    result = {}
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    while pending:
        url = pending.pop()
        if url in visited:
            raise IndexNowError("Duplicate or cyclic sitemap reference")
        visited.add(url)
        if len(visited) > 500:
            raise IndexNowError("Sitemap document limit exceeded")
        root = read_sitemap_document(url)
        if root.tag == f"{ns}sitemapindex":
            children = [node.text or "" for node in root.findall(f"{ns}sitemap/{ns}loc")]
            if not children:
                raise IndexNowError("Empty sitemap index")
            for child in children:
                parsed = urlsplit(child)
                # Pagination queries are allowed for sitemap documents only.
                validate_urls(site_url, [parsed._replace(query="").geturl()])
            pending.extend(children)
        elif root.tag == f"{ns}urlset":
            for node in root.findall(f"{ns}url"):
                location = node.findtext(f"{ns}loc", default="")
                validate_urls(site_url, [location])
                result[location] = node.findtext(f"{ns}lastmod", default="")
        else:
            raise IndexNowError("Expected sitemap index or URL set")
    if not result:
        raise IndexNowError("Refusing an empty sitemap")
    return result


def sitemap_urls(site_url):
    return sorted(sitemap_state(site_url))


def deployment_key(site_url, expected_revision=""):
    for attempt in range(30 if expected_revision else 1):
        try:
            status, body, headers = request(f"{site_url}{KEY_PATH}")
            key = body.decode("utf-8").strip()
            if status == 200 and re.fullmatch(r"[a-zA-Z0-9-]{8,128}", key):
                if not expected_revision or headers.get("X-Deployment-Revision") == expected_revision:
                    return key
        except (IndexNowError, UnicodeDecodeError):
            if not expected_revision:
                raise
        if attempt < 29 and expected_revision:
            time.sleep(10)
    raise IndexNowError("Live IndexNow key/revision could not be verified")


def submit(site_url, previous_urls=(), expected_revision="", dry_run=False):
    site_url = site_url.rstrip("/")
    validate_urls(site_url, [])
    key = deployment_key(site_url, expected_revision)
    urls = validate_urls(site_url, sitemap_urls(site_url) + list(previous_urls))
    if dry_run:
        return f"Dry run: {len(urls)} public URLs; no submission sent"
    return submit_urls(site_url, key, urls)


def submit_urls(site_url, key, urls):
    urls = validate_urls(site_url, urls)
    if not urls:
        return "No changed public URLs; no submission sent"
    statuses = []
    for start in range(0, len(urls), 10_000):
        payload = {
            "host": urlsplit(site_url).netloc,
            "key": key,
            "keyLocation": f"{site_url}{KEY_PATH}",
            "urlList": urls[start : start + 10_000],
        }
        status, _, _ = request(ENDPOINT, payload)
        if status not in (200, 202):
            raise IndexNowError(f"Unexpected IndexNow response: HTTP {status}")
        statuses.append(status)
    pending = "; key validation pending" if 202 in statuses else ""
    return (
        f"IndexNow received {len(urls)} URLs (HTTP {', '.join(map(str, statuses))}){pending}. "
        "Indexing is not guaranteed."
    )


def submit_changes(site_url, state_path, expected_revision="", dry_run=False, force=False):
    """Advance the checkpoint only after every notification batch succeeds."""
    key = deployment_key(site_url, expected_revision)
    current = sitemap_state(site_url)
    if expected_revision:
        # A failed deploy-wide refresh must also retry on the next hourly run.
        current = {url: f"{expected_revision}:{stamp}" for url, stamp in current.items()}
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    if not isinstance(previous, dict):
        raise IndexNowError("Invalid sitemap checkpoint")
    validate_urls(site_url, list(previous))
    changed = sorted(
        url
        for url in current.keys() | previous.keys()
        if force or url not in current or url not in previous or current[url] != previous[url]
    )
    if dry_run:
        return f"Dry run: {len(changed)} changed public URLs; no submission sent"
    result = submit_urls(site_url, key, changed)
    temporary = state_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(current, sort_keys=True), encoding="utf-8")
    temporary.replace(state_path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-url", required=True)
    parser.add_argument("--snapshot", type=Path, help="Save pre-deployment public URLs, without submitting")
    parser.add_argument("--previous", type=Path, help="Include the pre-deployment URLs, including removed pages")
    parser.add_argument("--expected-revision", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Resubmit all URLs with --state")
    parser.add_argument("--state", type=Path, help="Submit sitemap changes since last success")
    args = parser.parse_args()
    try:
        site_url = args.site_url.rstrip("/")
        validate_urls(site_url, [])
        if args.state:
            print(submit_changes(site_url, args.state, args.expected_revision, args.dry_run, args.force))
        elif args.snapshot:
            urls = sitemap_urls(site_url)
            args.snapshot.write_text(json.dumps(urls), encoding="utf-8")
            print(f"Saved {len(urls)} pre-deployment public URLs")
        else:
            previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else []
            validate_urls(site_url, previous)
            print(submit(site_url, previous, args.expected_revision, args.dry_run))
    except (IndexNowError, ValueError, OSError) as error:
        parser.exit(1, f"IndexNow failed: {error}\n")


if __name__ == "__main__":
    main()
