# Technical Guide

## Stack

- Backend: Django 5.2, Python 3.11+, Django REST Framework.
- Authentication: django-allauth sessions and DRF token authentication.
- Data: PostgreSQL 17, Redis 7, Django Q2 background workers.
- Frontend: Django templates, Tailwind CSS 3, Webpack 5, Turbo, Stimulus, and
  small Alpine.js template state.
- Media: django-storages with S3-compatible storage; local Compose includes
  MinIO.
- Email and payments: django-anymail/Mailgun, local Mailhog, and Stripe.
- Observability and analytics: Sentry, structlog, Logfire, PostHog, and
  Plausible.
- AI/content enrichment: Pydantic AI/OpenRouter and Jina Reader integrations.
- Deployment: Docker images deployed to CapRover from `master`; server and
  worker images share `deployment/Dockerfile`.

Python CI covers 3.11 and 3.13. Production and frontend image builds use Node
22; frontend CI and the current Compose frontend service use Node 18.

## Local runtime

`docker-compose.yml` defines:

- `backend` - Django development server.
- `workers` - Django Q2 cluster.
- `db` - PostgreSQL.
- `redis` - queue and cache.
- `frontend` - Webpack development server.
- `mailhog` - local email capture.
- `minio` and `createbuckets` - local S3-compatible media storage.
- `stripe` - webhook forwarding.
- `mjml` - email template rendering.

Configuration comes from `.env.example` plus the optional
`builtwithdjango/.env`. Keep secrets only in environment files or deployment
configuration; never commit them.

Before starting the stack, check its host ports. If a preferred port is taken,
preserve the existing service and bind the conflicting Built with Django
service to a free port. The browser-facing `SITE_URL` and storage endpoint must
match the ports/hostnames the browser can reach.

## Architecture

- `builtwithdjango/settings.py` wires Django apps, storage, cache, queue,
  observability, analytics, email, payments, and integrations.
- `builtwithdjango/test_settings.py` provides isolated test defaults and is the
  settings module configured by `pytest.ini`.
- Domain apps own their models, forms, views, URLs, tasks, and tests.
- Root `templates/` contains server-rendered pages and shared components.
- `frontend/src` contains browser controllers, JavaScript entry points, and the
  Tailwind design system.
- `frontend/webpack` builds development and production asset manifests consumed
  through `python-webpack-boilerplate`.
- `deployment/` owns production images, entrypoint behavior, Gunicorn, and the
  production shell helper.

## Project submission lifecycle

1. `ProjectCreateView` requires authentication and sets
   `Project.logged_in_maker`.
2. Submission enqueues screenshot capture, admin notification, and page-content
   fetching through Django Q2.
3. `save_screenshot` stores `homepage_screenshot` and marks the project
   published after a successful capture/upload.
4. Public list/search queries require `published=True`, `active=True`, and
   `might_be_spam=False`.
5. The linked submitter or linked legacy maker user can view and update their
   listing; anonymous and unrelated users cannot.

This means a successful form response does not by itself prove public
publication. Diagnose queue, worker, external screenshot response, object
storage, and database state separately.

## API boundaries

- Project search and read-oriented like endpoints are public.
- Like mutations require an authenticated user and are scoped to that user.
- Blog posts live in `content/blog/*.md` (see `content/README.md`). The read-only
  `/api/v1/posts/` API uses DRF token authentication restricted to superusers.
  Legacy ORM tables are a read-only rollback archive, not a publishing surface.
- Keep serializers and permission checks explicit when extending API behavior.

## Frontend rules

- Templates live in root `templates/<app>/`; shared fragments belong in
  `templates/components/`.
- Reusable browser behavior belongs in `frontend/src/controllers` or the
  existing application entry points.
- Executable design tokens and shared components live in
  `frontend/src/styles/tailwind.css`; do not fork their values in individual
  templates.
- Webpack output lives under `frontend/build` and should be regenerated with
  `npm run build` when source assets change.

## Testing and checks

- `make test` is the normal full Docker-backed test path.
- Pass focused pytest arguments with `make test ARGS="projects/tests.py -q"`.
- `pytest.ini` uses `builtwithdjango.test_settings`, disables migrations for
  tests, and discovers each app's `tests.py`.
- CI additionally runs Django system checks, migration-drift checks, Python
  compilation, coverage, and a clean frontend build.
- Use `make test-pgsandbox` only with an explicit sandbox `DATABASE_URL`.

## Job submission abuse controls

- `/jobs/new` limits all CSRF-valid POST attempts to 10 per 600 seconds using
  the shared Redis cache. Keys contain an HMAC of the client address, not raw
  addresses; IPv6 addresses are grouped by /64. Cache outages return 503.
- Production requires `JOB_TURNSTILE_ENABLED=True`, `JOB_TURNSTILE_SITE_KEY`
  and `JOB_TURNSTILE_SECRET_KEY`. Use a managed widget restricted to the site
  hostname. Tokens are validated server-side with exact hostname and
  `post-job` action checks before saving or enqueueing. Missing/expired/
  replayed tokens, bad provider responses and verification outages reject
  submissions without side effects. Development/tests may explicitly disable
  the integration; do not use test keys or disable it in production.
- Set `JOB_SUBMISSION_TRUST_PROXY_IP=True` only when the origin is reached
  through a trusted proxy that **overwrites** `X-Real-IP`. The inspected
  CapRover nginx config does so. Never trust incoming `X-Forwarded-For` or
  `CF-Connecting-IP` without a verified proxy boundary. Keep direct application
  ports private. No Cloudflare zone/DNS migration is required for Turnstile.
- A hidden honeypot rejects basic form fillers. SQL keyword blacklists are
  intentionally not used: database safety depends on parameterized ORM
  queries, not recognizing attack strings.
- Accepted submissions remain unapproved/unpaid and enqueue a stable job ID.
  Django Q schedules at most one digest per UTC 10-minute window, executed
  after the window closes. The digest queries saved, non-imported submissions
  and contains only counts, never submitted text. Positive ONCE repeats keep
  the completed schedule as a deduplication marker. Keep the Q scheduler on.
- Job-form visits force a normal page load, and POSTs opt out of Turbo so the
  challenge widget resets correctly after invalid forms. The widget is
  flexible-width for small screens; visitors need JavaScript for verification.

Rollback: revert the protection PR and redeploy the previous web/worker images.
Keep widget credentials in deployment configuration, not Git. Preserve incident
records and private access-log evidence before any separately approved cleanup.
