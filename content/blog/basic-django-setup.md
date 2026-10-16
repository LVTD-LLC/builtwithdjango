---
id: 2
created: '2022-01-27 19:00:02.487000+00:00'
modified: '2026-10-16 08:50:00+00:00'
title: Setting up a basic Django project with Poetry
slug: basic-django-setup
status: PB
description: In this tutorial, we will go through the process of setting up the most basic Django project with Poetry.
  We will use that as a setup up for other posts and tutorials.
unsplashID: OVbeSXRk_9E
icon: image/upload/v1659728681/blog-post-icon-prod/f6xe0hgl4vijlur6xp9w.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 4
  name: Poetry
  slug: poetry
- id: 5
  name: Pyenv
  slug: pyenv
author: 1
---

A basic Django project needs an isolated Python environment, a dependency file, and a URL that reaches a view. Here we will use Poetry to install Django, then build a template-backed homepage you can check in your browser.

This walkthrough was checked on Linux with Python 3.11, Poetry 2.2.1, and Django 5.2.18. Those are the tested versions, not a claim that they are the latest releases. The project deliberately stays on Django 5.2; this is a local learning setup, not a production deployment recipe.

## Prerequisites

### Python and Pyenv

Install Python 3.11 before starting. You can use your operating system's Python installer or [Pyenv's installation instructions](https://github.com/pyenv/pyenv#installation) if you already manage multiple Python versions. Pyenv is optional: Poetry can use an installed interpreter directly.

The shell commands below use `python3.11`. If your installation exposes Python as `python` or `py -3.11`, check its version and use the full path to that interpreter in the `poetry env use` step. Native Windows installation and PowerShell commands were not tested for this walkthrough; follow the platform-specific instructions linked below rather than running the macOS Homebrew commands on Windows.

```bash
python3.11 --version
```

### Poetry

Follow the current [official Poetry installation instructions](https://python-poetry.org/docs/#installation), including their PATH setup for your operating system. Keep Poetry in its own environment rather than adding it as a dependency of this Django project. If you already have it installed, check:

```bash
poetry --version
```

Use Poetry 2.x for the configuration below. We tested 2.2.1. You do not need the optional shell plugin: every project command here uses `poetry run` explicitly.

## Setting up the Environment

Create a new, empty directory and enter it:

```bash
mkdir basic_django
cd basic_django
```

In that directory, create `pyproject.toml` with this complete configuration. It uses Poetry's documented [non-package mode](https://python-poetry.org/docs/basic-usage/#operating-modes): we want dependency management for a website, not a package to publish on PyPI.

```toml
[tool.poetry]
package-mode = false

[tool.poetry.dependencies]
python = ">=3.11,<3.12"
django = ">=5.2.18,<5.3"
```

The Python range deliberately matches our tested interpreter series. The Django range allows later 5.2 patch releases, while avoiding an automatic jump to a different feature release. If you choose another Python series, check [Django's supported Python versions](https://docs.djangoproject.com/en/5.2/faq/install/#what-python-version-can-i-use-with-django) and adjust the range as well as your selected interpreter.

Select the interpreter and install the dependencies:

```bash
poetry env use python3.11
poetry install
poetry run python -m django --version
```

Poetry creates `poetry.lock` during the first successful installation. Keep both `pyproject.toml` and `poetry.lock` in version control. The former declares permitted versions; the latter records the resolved dependencies. On a second checkout, `poetry install` uses the existing lock file. Use `poetry update django` when you intentionally want to resolve a newer permitted Django version, then check your app before committing the updated lock.

Now generate the Django project using the [documented startproject command](https://docs.djangoproject.com/en/5.2/ref/django-admin/#startproject):

```bash
poetry run django-admin startproject basic_django .
poetry run python manage.py check
```

The trailing dot places `manage.py` in the directory you already created. `basic_django/` inside it is the Python package containing settings and the root URL configuration. Run subsequent commands from the outer directory, alongside `manage.py`.

You should now have:

```text
basic_django/
├── basic_django/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── poetry.lock
└── pyproject.toml
```

### Decide on your user model before migrating

This tutorial does not create database-backed pages or run migrations. If you will follow our [custom user and authentication tutorial](/blog/user-authentication), do that before your first `migrate`: Django requires the custom user model to be configured at the start of the project. See [Django's custom-user guidance](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project).

If you deliberately choose Django's default user instead, you can run `poetry run python manage.py migrate` to create its initial database tables. Do not switch user models later by simply changing a setting on a populated database.

## Adding Static Pages

We will add a `pages` app and a homepage rendered by `TemplateView`. Here, “static page” means a page without a database query, not a static file served outside Django. The example follows Django's [URL/view/template workflow](https://docs.djangoproject.com/en/5.2/intro/tutorial03/) and [TemplateView documentation](https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/#templateview).

```bash
poetry run python manage.py startapp pages
```

In `basic_django/settings.py`, add `"pages"` to the existing `INSTALLED_APPS` list. Keep the generated Django apps. In the existing `TEMPLATES` setting, change only its `DIRS` entry:

```python
"DIRS": [BASE_DIR / "templates"],
```

Keep `APP_DIRS`, the backend, and the generated context processors unchanged. `DIRS` adds a project-level template search location; it does not disable app-level template discovery.

Create the directories `templates/` and `templates/pages/` in your editor. Then save this as `templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Basic Django Project</title>
</head>
<body>
  {% block content %}{% endblock content %}
</body>
</html>
```

Save the child template as `templates/pages/home.html`:

```html
{% extends "base.html" %}

{% block content %}
  <h1>Hello, Django!</h1>
{% endblock content %}
```

Replace `pages/views.py` with:

```python
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"
```

Create `pages/urls.py`:

```python
from django.urls import path

from .views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
```

Replace `basic_django/urls.py` with:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
]
```

The empty prefix delegates the root path to `pages.urls`. It does not create a URL namespace. A request for `/` now reaches `HomeView`, which renders the child template inside `base.html`.

### Verify the homepage

Add this test to `pages/tests.py`:

```python
from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_homepage(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, Django!")
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertTemplateUsed(response, "base.html")
```

`SimpleTestCase` is enough because this page does not query the database. Run the check and test before starting the development server:

```bash
poetry run python manage.py check
poetry run python manage.py test pages
poetry run python manage.py runserver
```

Open `http://127.0.0.1:8000/`. You should see **Hello, Django!**, not Django's initial welcome screen. Stop the server with Ctrl+C. If port 8000 is already in use, choose another port, for example `poetry run python manage.py runserver 8001`, and open that port instead. Do not stop another project's server to free it.

An unapplied-migrations warning is expected if you have deferred database setup for a custom user. The homepage test can still pass; admin and other database-backed features need their migrations before use. Django's development server is for local work, not production hosting.

### If a step fails

- **Poetry cannot find Python:** run `poetry env use` with the full path to your installed Python 3.11 interpreter. Check `poetry run python --version` before installing dependencies.
- **Poetry tries to install the website as a package:** check that `package-mode = false` is under `[tool.poetry]`, not `[tool.poetry.dependencies]`.
- **Django cannot import `pages.urls`:** confirm that you created `pages/urls.py`; `startapp` does not generate that file.
- **`TemplateDoesNotExist`:** check the file path is `templates/pages/home.html`, and that the existing `TEMPLATES` configuration includes `BASE_DIR / "templates"` in `DIRS`.
- **The welcome page still appears:** check the root `basic_django/urls.py` includes `pages.urls` and that you are visiting the server for this project.

## Conclusion

You now have a Poetry-managed Django project, a lock file, and a tested homepage. Keep using `poetry run` so commands resolve against this project's dependencies. No globally installed Django or activated shell is required.

Next, configure [user authentication](/blog/user-authentication) before your first migration if you want a custom user, put [environment-specific settings outside your code](/blog/env-vars), or add [pre-commit checks](/blog/improve-your-code-with-pre-commit). For template indentation, the [Django HTML formatter](/tools/format-html/) offers an example and a local djLint command; use the local option for private templates.
