# /// script
# requires-python = ">=3.11"
# dependencies = ["Django==5.2.18", "fastmcp==2.14.7"]
# ///
"""Run with `uv run --python 3.13 scripts/check_mcp_guide.py`.

Extract the published tutorial snippets into a temporary Django project and
exercise their combined ASGI application over MCP HTTP. No production data,
credentials, or application dependencies are used.
"""

import json
import re
import sys
import tempfile
from pathlib import Path


def main():
    article = Path(__file__).resolve().parents[1] / "content/blog/build-a-hosted-mcp-server-in-django-with-fastmcp.md"
    blocks = re.findall(r"```python\n(.*?)```", article.read_text(), re.S)

    def snippet(prefix):
        return next(block for block in blocks if block.startswith(prefix))

    with tempfile.TemporaryDirectory(prefix="bwd-mcp-guide-") as directory:
        root = Path(directory)
        app = root / "mcp_server"
        app.mkdir()
        (app / "__init__.py").write_text("")
        for name, prefix in [
            ("models", "import hashlib"),
            ("auth", "from django.db import close_old_connections"),
            ("server", "from asgiref.sync import sync_to_async"),
        ]:
            (app / f"{name}.py").write_text(snippet(prefix))
        (root / "test_urls.py").write_text("urlpatterns = []\n")
        sys.path.insert(0, str(root))

        from django.conf import settings

        settings.configure(
            SECRET_KEY="isolated-example-test-only",
            INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "mcp_server"],
            DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": str(root / "db.sqlite3")}},
            ROOT_URLCONF="test_urls",
            ALLOWED_HOSTS=["testserver"],
            USE_TZ=True,
        )
        import django

        django.setup()
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        from django.db import connections
        from django.utils import timezone
        from mcp_server.models import MCPApiKey
        from starlette.testclient import TestClient

        call_command("migrate", run_syncdb=True, verbosity=0)
        users = get_user_model()
        alice = users.objects.create_user(username="alice", email="alice@example.invalid")
        bob = users.objects.create_user(username="bob", email="bob@example.invalid")
        disabled = users.objects.create_user(username="disabled", is_active=False)
        alice_key, alice_raw = MCPApiKey.create_key(alice)
        _, bob_raw = MCPApiKey.create_key(bob)
        _, disabled_raw = MCPApiKey.create_key(disabled)
        revoked_key, revoked_raw = MCPApiKey.create_key(alice)
        revoked_key.revoked_at = timezone.now()
        revoked_key.save()

        namespace = {}
        exec(snippet("import os\n"), namespace)
        results = []
        with TestClient(namespace["application"]) as client:
            # The exact article uses stateful HTTP: preserve the handshake's
            # session ID and protocol header, rather than bypassing its lifespan.
            headers = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}

            def rpc(method, params, request_id, extra=None):
                response = client.post(
                    "/mcp/",
                    headers={**headers, **(extra or {})},
                    json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
                )
                assert response.status_code == 200, response.status_code
                if response.headers.get("mcp-session-id"):
                    headers["Mcp-Session-Id"] = response.headers["mcp-session-id"]
                if "text/event-stream" in response.headers.get("content-type", ""):
                    return json.loads(
                        next(line[6:] for line in response.text.splitlines() if line.startswith("data: "))
                    )
                return response.json()

            rpc(
                "initialize",
                {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "guide-check", "version": "1"},
                },
                1,
            )
            for number, (label, raw, expected) in enumerate(
                [
                    ("active owner", alice_raw, "alice"),
                    ("second owner", bob_raw, "bob"),
                    ("missing key", None, None),
                    ("invalid key", "not-a-real-key", None),
                    ("revoked key", revoked_raw, None),
                    ("inactive user", disabled_raw, None),
                ],
                2,
            ):
                extra = {"Authorization": "Bearer " + raw} if raw else {}
                payload = rpc("tools/call", {"name": "get_user_info", "arguments": {}}, number, extra)["result"]
                if expected:
                    assert not payload.get("isError"), payload
                    data = json.loads(payload["content"][0]["text"])
                    assert data["username"] == expected, data
                else:
                    assert payload.get("isError") is True, label
                    assert "@example.invalid" not in json.dumps(payload), label
                results.append(label)
            alice_key.refresh_from_db()
            assert alice_key.last_used_at is not None
            redirect = client.post("/mcp", follow_redirects=False)
            assert redirect.status_code == 307 and redirect.headers["location"].endswith("/mcp/")
        # Exercise the reader's actual FastMCP Client snippet against a local
        # Uvicorn socket, including its handshake and result.data contract.
        import contextlib
        import io
        import socket
        import threading
        import time
        from unittest.mock import patch

        import uvicorn

        exec(snippet("import os\n"), namespace)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            server = uvicorn.Server(uvicorn.Config(namespace["application"], log_level="critical"))
            thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
            thread.start()
            try:
                deadline = time.monotonic() + 10
                while not server.started and time.monotonic() < deadline:
                    time.sleep(0.05)
                assert server.started, "Local Uvicorn failed to start"
                code = snippet("import asyncio\n").replace("127.0.0.1:8000", f"127.0.0.1:{port}")
                output = io.StringIO()
                with patch("getpass.getpass", return_value=alice_raw), contextlib.redirect_stdout(output):
                    exec(code, {})
                assert "alice@example.invalid" in output.getvalue()
            finally:
                server.should_exit = True
                thread.join(timeout=10)
                assert not thread.is_alive(), "Local Uvicorn did not stop"
        connections.close_all()
        print(
            f"PASS: {len(results)} tool authorization cases, last_used_at, ASGI lifespan, slash redirect and real Client snippet"
        )
        print(f"Verified with Django {django.get_version()} and FastMCP 2.14.7")


if __name__ == "__main__":
    main()
