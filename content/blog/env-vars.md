---
id: 11
created: '2024-08-06 08:39:55.810329+00:00'
modified: '2026-10-23 08:45:00+00:00'
title: Setting up Environment Variables in Django
slug: env-vars
status: PB
description: In this tutorial, we are going to add support for environment variables in our app.
unsplashID: Led9c1SSNFo
icon: image/upload/v1722933596/blog-post-icon-prod/gmvwabnxdcbg99nhtrua.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 6
  name: git
  slug: git
- id: 7
  name: Github
  slug: github
author: 1
---
## Keep configuration out of your code

Environment variables let one Django codebase use different settings locally and in production. Here we'll load a local `.env` file with `django-environ`, parse `DEBUG` as a boolean, and require a secret key without putting it in `settings.py`.

**Corrected October 23, 2026:** the earlier version recommended `overwrite=True` for every setup. That makes file values replace existing process environment variables, not merely “refresh” them. A development `.env` could then replace production configuration. Keep the default precedence unless you deliberately want the file to win.

This walkthrough uses Python 3.11, Django 5.2.18 and django-environ 0.14.0. It continues from a working project such as [basic Django setup](/blog/basic-django-setup). The [original tutorial PR](https://github.com/builtwithdjango/basic-django/pull/5/files) is historical; use the corrected steps below.

## 1. Install the reader and exclude local secrets

From the directory containing `manage.py`:

```bash
poetry add django-environ
```

Before creating a real secret file, add these entries to your project's `.gitignore`:

```gitignore
.env
.env.*
!.env.example
```

Keep `.env.example` limited to variable names and harmless placeholders so teammates know what to configure. Check your existing tracking state: `.gitignore` does not remove files already committed. If a credential reached Git or a public log, revoke or rotate it with the relevant provider; deleting the file is not enough. See [setting up version control](/blog/django-version-control) for the repository basics.

## 2. Create a development-only .env

Create `.env` beside `manage.py`:

```env
DEBUG=True
# Placeholder only: replace with a newly generated key before use.
SECRET_KEY=replace-with-a-new-random-development-key
```

Generate a URL-safe random key locally (this avoids django-environ's `$` value-proxy syntax):

```bash
poetry run python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy the result into `SECRET_KEY`, enclosed in single quotes; keep comments on separate lines. Do not share the output or reuse the placeholder. The [Django secret key tool](/tools/django-secret/) also offers development-key generation and production rotation guidance. Existing applications need a rotation plan, not an automatic new key on every restart.

## 3. Read the file without replacing deployment settings

In `settings.py`, keep your existing `BASE_DIR` definition. After it, add the reader and replace the existing `DEBUG` and `SECRET_KEY` assignments:

```python
import environ

# BASE_DIR is already defined above this block.
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY")
```

Django's generated `BASE_DIR` is a `pathlib.Path`. If your older project uses a string, pass `os.path.join(BASE_DIR, ".env")` instead.

With the [documented default precedence](https://django-environ.readthedocs.io/en/stable/api.html#environ.Env.read_env), an existing process variable wins over the same name in `.env`. For example, a platform-provided `DEBUG=False` stays false even if the file says `DEBUG=True`. `env.bool()` parses the value rather than treating the nonempty string `"False"` as true.

If `DEBUG` is absent from both places, it defaults to false. If `SECRET_KEY` is missing, Django raises `ImproperlyConfigured` instead of silently using a shared fallback. A missing `.env` does not stop this setup when the required variables are supplied by the deployment environment.

Only use [explicit file overrides](https://django-environ.readthedocs.io/en/stable/tips.html#overwriting-existing-environment-values-from-env-files) when that is your intended policy. After changing configuration, restart the process that reads it. Editing `.env` does not update an already running server's environment.

## 4. Check the result without printing secrets

From your project root, run:

```bash
poetry run python manage.py check
poetry run python manage.py shell -c "from django.conf import settings; print('DEBUG:', settings.DEBUG); print('SECRET_KEY configured:', bool(settings.SECRET_KEY))"
git check-ignore .env
git ls-files -- .env
```

For the development file above and no process override, expect `DEBUG: True` and `SECRET_KEY configured: True`. `git check-ignore` should report `.env`; `git ls-files` should print nothing. If Git already tracks it, stop and resolve the tracked secret before committing. Do not print the actual key to debug configuration.

You can now use `poetry run python manage.py runserver` locally. In production, supply a distinct secret through your deployment's protected configuration, keep `DEBUG=False`, and set the correct `ALLOWED_HOSTS`. Run `python manage.py check --deploy` using the production settings and address its findings; this tutorial is not a complete production settings file.

A `.env` file is **plain text, not encryption or a security guarantee**. Keep it out of public/static directories and container images, limit who can read it, and avoid exposing secrets through logs or error pages. Continue with Django's [deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) before deploying.
