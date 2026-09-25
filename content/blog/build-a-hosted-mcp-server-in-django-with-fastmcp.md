---
id: 157
created: '2026-06-19 20:12:21.788869+00:00'
modified: '2026-06-19 20:15:36.736275+00:00'
title: Build a Hosted MCP Server in Django With FastMCP
slug: build-a-hosted-mcp-server-in-django-with-fastmcp
status: PB
description: Add a beginner-friendly hosted MCP endpoint to a Django app with FastMCP, API key auth, and a simple
  user info tool.
unsplashID: ''
icon: ''
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 209
  name: MCP
  slug: mcp
- id: 210
  name: FastMCP
  slug: fastmcp
- id: 211
  name: AI
  slug: ai
author: 1
---
MCP servers are most useful when they let an AI assistant work with real app data safely.

A good example is [OpenBudget](https://www.openbudget.sh/). It connects financial data to AI tools so a user can ask useful questions about their own spending, balances, and transactions. That is the kind of MCP use case that makes sense: the app already has the data, the user already has an account, and the AI assistant needs a safe way to ask for structured information.

Django is a strong fit for this. Most [Django apps](https://builtwithdjango.com/projects/) already have users, permissions, database models, admin tools, and production deployment habits. You do not need to build a separate backend for AI agents. You can add a small hosted MCP server inside the Django app you already have.

This post shows the beginner-friendly version: a hosted MCP endpoint at `/mcp`, built with the standalone `fastmcp` package, using an API key to identify the current user when a tool is called, and exposing one simple tool: `get_user_info`.

## What we are building

The final shape looks like this:

```text
AI client -> https://example.com/mcp -> FastMCP -> Django User/database
```

The MCP server will:

* live in its own Django app called `mcp_server`
* run as a hosted HTTP endpoint at `/mcp`
* use an API key to identify the current user
* expose a `get_user_info` tool
* return safe account data for that user

This guide does not assume your project has a separate API app or Django REST Framework. It assumes a normal Django project with a normal user model. If you are starting from scratch, start with the [basic Django project setup guide](https://builtwithdjango.com/blog/basic-django-setup) first.

## Step 1: Install FastMCP

Add [FastMCP](https://gofastmcp.com/getting-started/welcome) to your Django project:

```bash
uv add fastmcp
```

If you are not using `uv`, use your normal dependency manager:

```bash
pip install fastmcp
```

This guide uses the standalone `fastmcp` package and imports it like this:

```python
from fastmcp import FastMCP
```

A hosted MCP server uses [MCP Streamable HTTP](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), so it should be deployed through [Django's ASGI entrypoint](https://docs.djangoproject.com/en/stable/howto/deployment/asgi/). If your project currently uses WSGI, keep reading. There is a short deployment section below.

## Step 2: Create a Django app for MCP

Create a new Django app:

```bash
python manage.py startapp mcp_server
```

Add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "mcp_server",
]
```

The exact folder layout does not matter. For a beginner guide, a root-level `mcp_server` app is easiest to understand. If your project uses a different layout, keep the imports consistent with your own project.

A simple layout:

```text
my_project/
  asgi.py
  settings.py
  urls.py
mcp_server/
  __init__.py
  admin.py
  apps.py
  auth.py
  models.py
  server.py
manage.py
```

## Step 3: Add a simple API key model

If your app already has API keys, you can reuse them. But many beginner Django apps do not.

The simplest safe setup is a small API key model linked to Django's user model. Store a hash of the key, not the raw key.

In `mcp_server/models.py`:

```python
import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class MCPApiKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="MCP key")
    prefix = models.CharField(max_length=16, db_index=True)
    key_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} for {self.user}"

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def create_key(cls, user, name="MCP key"):
        raw_key = "mcp_" + secrets.token_urlsafe(32)
        key = cls.objects.create(
            user=user,
            name=name,
            prefix=raw_key[:16],
            key_hash=cls.hash_key(raw_key),
        )
        return key, raw_key

    def mark_used(self):
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])
```

Create and run the migration:

```bash
python manage.py makemigrations mcp_server
python manage.py migrate
```

You now need a way to create a key for a user. For a first version, a Django shell command is enough:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from mcp_server.models import MCPApiKey

User = get_user_model()
user = User.objects.get(email="you@example.com")
key, raw_key = MCPApiKey.create_key(user, name="Claude")
print(raw_key)
```

Show the raw key only once. After that, only the hash is stored.

## Step 4: Authenticate MCP requests with the API key

Create `mcp_server/auth.py`:

```python
from django.db import close_old_connections
from django.utils import timezone
from starlette.datastructures import Headers

from mcp_server.models import MCPApiKey


def get_bearer_token(headers: Headers) -> str:
    authorization = headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token.strip():
        return token.strip()
    return ""


def authenticate_mcp_headers(headers: Headers):
    """Return the authenticated Django user, or None."""
    close_old_connections()
    try:
        raw_key = get_bearer_token(headers)
        if not raw_key:
            return None

        key_hash = MCPApiKey.hash_key(raw_key)
        api_key = (
            MCPApiKey.objects.select_related("user")
            .filter(key_hash=key_hash, revoked_at__isnull=True)
            .first()
        )
        if api_key is None:
            return None

        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=["last_used_at"])
        return api_key.user
    finally:
        close_old_connections()
```

The important rule: do not let the model pass `user_id` as a tool argument. The server should figure out the user from the API key.

Bad:

```python
@mcp.tool()
def get_user_info(user_id: int) -> dict:
    ...
```

Good:

```python
@mcp.tool()
def get_user_info() -> dict:
    user = authenticate_current_request()
    ...
```

The AI client can ask for data. Django decides which user's data it is allowed to see.

## Step 5: Create the FastMCP server

Create `mcp_server/server.py`:

```python
from django.db import close_old_connections
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request

from mcp_server.auth import authenticate_mcp_headers

mcp = FastMCP(
    name="My Django App",
    instructions=(
        "Use this MCP server to access safe account information for the "
        "authenticated user. Authenticate with Authorization: Bearer <api_key>."
    ),
)


def get_request_user():
    request = get_http_request()
    return authenticate_mcp_headers(request.headers)


def require_user():
    user = get_request_user()
    if user is None:
        raise PermissionError(
            "Missing or invalid MCP API key. "
            "Send Authorization: Bearer <api_key>."
        )
    return user


@mcp.tool(
    name="get_user_info",
    description="Return safe account details for the authenticated Django user.",
)
def get_user_info() -> dict:
    close_old_connections()
    try:
        user = require_user()
        return {
            "id": user.id,
            "username": user.get_username(),
            "email": user.email,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        }
    finally:
        close_old_connections()
```

This is intentionally small. The MCP tool authenticates the request, gets the current Django user, and returns a structured payload.

Only return fields you are comfortable exposing to an AI client. If you do not want to expose `email`, remove it.

## Step 6: Mount the MCP server at `/mcp`

Now wire FastMCP into your Django ASGI app. FastMCP's [HTTP deployment docs](https://gofastmcp.com/deployment/http) show the same `http_app()` pattern for hosted servers.

In `my_project/asgi.py`:

```python
import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")

django_application = get_asgi_application()

from mcp_server.server import mcp  # noqa: E402

raw_mcp_application = mcp.http_app(path="/")


def redirect_mcp(request: Request) -> RedirectResponse:
    return RedirectResponse(str(request.url.replace(path="/mcp/")), status_code=307)


application = Starlette(
    routes=[
        Route("/mcp", endpoint=redirect_mcp, methods=["GET", "POST", "DELETE"]),
        Mount("/mcp", app=raw_mcp_application),
        Mount("/", app=django_application),
    ],
    lifespan=raw_mcp_application.lifespan,
)
```

Replace `my_project.settings` with your actual settings module.

A few details matter here:

* `/mcp` redirects to `/mcp/` so clients do not fail on a missing trailing slash.
* Django still handles the rest of the site.
* FastMCP handles the MCP endpoint.
* The FastMCP lifespan is passed to Starlette. Do not skip that.

Small security note: this example checks the API key inside the tool. Django session middleware, login decorators, and CSRF middleware do not protect the mounted FastMCP app. In production, use HTTPS, keep checking permissions inside every tool, and follow the MCP transport guidance to [validate allowed `Origin` headers](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#security-warning) if browsers can reach the endpoint.

## Step 7: Run it locally

Run the Django app through an ASGI server:

```bash
uv add uvicorn
uv run uvicorn my_project.asgi:application --reload
```

Or with `pip`:

```bash
pip install uvicorn
uvicorn my_project.asgi:application --reload
```

Your MCP endpoint should now be available at:

```text
http://127.0.0.1:8000/mcp
```

Use your MCP client with:

```text
Endpoint: http://127.0.0.1:8000/mcp
Header: Authorization: Bearer YOUR_MCP_API_KEY
```

The exact setup screen depends on the client, but the two important pieces are the endpoint and the `Authorization` header.

A successful `get_user_info` call should return JSON for the user who owns the API key. If the key is missing or wrong, the tool should return an authentication error.

## If your deployment uses WSGI

Many beginner Django apps are deployed with WSGI. A common command looks like this:

```bash
gunicorn my_project.wsgi:application
```

For a hosted MCP server, ASGI is the better fit because FastMCP exposes an ASGI HTTP app. You usually do not need to rewrite your Django app. You mostly need to change the server entrypoint from `wsgi` to `asgi` and use [Uvicorn workers](https://uvicorn.dev/).

Install the ASGI server dependencies:

```bash
uv add uvicorn gunicorn uvicorn-worker
```

If you use `pip`:

```bash
pip install uvicorn gunicorn uvicorn-worker
```

Then change the process command to:

```bash
gunicorn my_project.asgi:application -k uvicorn_worker.UvicornWorker
```

If you use a `Procfile`, it may change from:

```text
web: gunicorn my_project.wsgi:application
```

to:

```text
web: gunicorn my_project.asgi:application -k uvicorn_worker.UvicornWorker
```

If you use Docker, update the container command the same way.

If you later run multiple web workers or multiple app instances, make the MCP app stateless:

```python
raw_mcp_application = mcp.http_app(path="/", stateless_http=True)
```

That avoids tying an MCP session to one in-memory worker.

That is the short version. Real deployments can have extra details around static files, reverse proxies, timeouts, and platform-specific settings. If you want a deeper guide for your setup, email me at [Rasul@builtwithdjango.com](mailto:Rasul@builtwithdjango.com).