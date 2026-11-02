---
id: 6
created: '2022-06-24 21:40:59.227000+00:00'
modified: '2026-11-02 08:45:00+00:00'
title: How to set up Webpack and TailwindCSS in a Django Project
slug: set-up-webpack-and-tailwind
status: PB
description: In this guide, we will set up Webpack and will install TailwindCSS into our Django application.
unsplashID: Nl-SXO4FAHw
icon: image/upload/v1659728521/blog-post-icon-prod/owqe1zfch0pdpknxegtx.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 11
  name: Frontend
  slug: frontend
- id: 12
  name: Webpack
  slug: webpack
- id: 13
  name: TailwindCSS
  slug: tailwindcss
author: 1
---
Webpack builds the JavaScript and CSS; Django loads those bundles through a manifest. This walkthrough keeps those two jobs separate and uses **Tailwind CSS 3**, matching the configuration below.

The original `tailwindcss@latest` command now installs Tailwind 4, which cannot use the old `tailwindcss` PostCSS plugin or `tailwindcss/nesting` path. Do not mix the two setups. For a new Tailwind 4 project, follow the boilerplate's [Tailwind 4 setup](https://python-webpack-boilerplate.readthedocs.io/en/latest/setup_with_django/) instead; this is not a v4 migration guide.

## Before you start

Use a working Django project with a homepage. The [basic Django setup guide](/blog/basic-django-setup) covers that starting point. Authentication is not required for this asset pipeline; keep any existing account apps and settings.

The steps below were checked on Linux with Python 3.11, Django 5.2.18, Node 22.23.4, `python-webpack-boilerplate` 1.0.4 and Tailwind 3.4.17. These are a reproducible compatibility baseline, not a claim that they are the latest releases or a security audit of the generated dependency tree. Run the commands from the project root, beside `manage.py`.

## Generate the Webpack files

Add the Python integration:

```bash
poetry add python-webpack-boilerplate==1.0.4
```

Add `"webpack_boilerplate"` to your existing `INSTALLED_APPS` in `settings.py`. Do not replace the list or add a second copy of Django's staticfiles app.

```bash
poetry run python manage.py webpack_init
```

Choose `frontend` for the project slug, `y` for running npm commands at the root, and **`3` (`scss`) for the style solution**. The default Tailwind choice generates a different, v4 pipeline. Use this generator in a fresh working tree: do not overwrite an existing frontend setup to follow the tutorial.

This creates `frontend/`, `package.json`, a lockfile and configuration files at the root. Review the generated project metadata before committing it.

## Install the Tailwind 3 dependencies

Install the generated dependencies, including the development tools needed to compile assets, then pin the [Tailwind 3 PostCSS integration](https://v3.tailwindcss.com/docs/installation/using-postcss/):

```bash
npm install --include=dev
npm install --include=dev --save-dev --save-exact tailwindcss@3.4.17 postcss-import@16.1.1 autoprefixer@10.4.21
```

Keep the resulting `package-lock.json` in version control. After the first install, use `npm ci --include=dev` to reproduce that lockfile. Do not run an automatic major-version upgrade to fix a compile error.

Replace the root `postcss.config.js` with:

```javascript
module.exports = {
  plugins: [
    require("postcss-import"),
    require("tailwindcss"),
    require("autoprefixer"),
  ],
};
```

This minimal setup does not need the old nesting plugin or the tutorial's historical Autoprefixer warning workaround. If your own styles depend on additional PostCSS plugins, migrate them deliberately rather than discarding their configuration.

Create `tailwind.config.js` beside `postcss.config.js`:

```javascript
module.exports = {
  content: [
    "./templates/**/*.html",
    "./*/templates/**/*.html",
    "./frontend/src/**/*.js",
  ],
  theme: { extend: {} },
  plugins: [],
};
```

Those paths cover the root template directory, one-level Django app template directories and frontend JavaScript. Add a path for any deeper or differently located templates. Write complete class names such as `text-green-800`; constructing partial names dynamically can prevent Tailwind from finding them.

Rename the generated `frontend/src/styles/index.scss` to `index.css`, then replace its contents with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Rename `frontend/src/application/app.js` to `index.js`, then replace its demo content with:

```javascript
import "../styles/index.css";
```

The entry is called **`index`**, matching the later [Stimulus tutorial](/blog/stimulusjs). The template tags below use that entry name. Other generated demo entries are not needed by this homepage; they need not be loaded.

In the generated `.stylelintrc.json`, keep the other rules and replace `scss/at-rule-no-unknown` with this value so development linting recognizes Tailwind's directives:

```json
"scss/at-rule-no-unknown": [true, {
  "ignoreAtRules": ["tailwind", "apply", "layer", "screen", "config"]
}]
```

That is one property inside the existing `rules` object, not a complete JSON file.

## Connect the manifest to Django

In `settings.py`, add the asset settings below. If these settings already exist, merge the paths rather than defining a second conflicting value:

```python
STATICFILES_DIRS = [BASE_DIR / "frontend/build"]
STATIC_ROOT = BASE_DIR / "staticfiles"
WEBPACK_LOADER = {
    "MANIFEST_FILE": BASE_DIR / "frontend/build/manifest.json",
}
```

Keep `STATIC_URL` configured (the generated Django project already has it). `STATIC_ROOT` is the collection destination, not your source directory. Never put it inside `frontend/build` or include it in `STATICFILES_DIRS`.

Make sure the existing `TEMPLATES` setting can find the root template directory, for example `"DIRS": [BASE_DIR / "templates"]`. Preserve its other options.

Use this `templates/base.html`:

```html
{% load webpack_loader %}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Django with Tailwind</title>
  {% stylesheet_pack 'index' %}
  {% javascript_pack 'index' attrs='defer' %}
</head>
<body>{% block content %}{% endblock %}</body>
</html>
```

Then use this `templates/home.html` with your existing homepage view:

```html
{% extends 'base.html' %}
{% block content %}
  <h1 class="text-green-800 text-lg">Django with Tailwind</h1>
{% endblock %}
```

If you do not already have that view, a minimal `basic_django/urls.py` for this example is:

```python
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html")),
]
```

In an existing project, add only the homepage route you need and retain the other URL patterns.

## Check a production-mode build first

```bash
npm run build
poetry run python manage.py check
poetry run python manage.py collectstatic --noinput
poetry run python manage.py runserver
```

Check that `frontend/build/manifest.json` exists and has an `index` entry. Visit the Django homepage at `http://127.0.0.1:8000/` and check the green heading. In browser developer tools, confirm that the emitted CSS and JavaScript requests return 200. A manifest alone does not prove that your template loads the right entry or that the CSS contains your utilities.

Build **before** `collectstatic`; collection copies files but does not compile Tailwind. Django's development server can serve static files with `DEBUG=True`. A production web server or storage/CDN must serve the collected files separately; this walkthrough does not configure TLS, a CDN or production static hosting. See [Django's static deployment guide](https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/).

## Development and reloads

Stop the Django server with Ctrl+C before switching workflows. The generated `npm run watch` recompiles assets on disk without a separate asset server. Run it in one terminal and `poetry run python manage.py runserver` in another. Refresh the browser after a successful rebuild.

For the generated webpack development server, use `npm run start` instead of `watch`. It normally listens on port 9091 and writes a development manifest pointing at that server. Keep it running while Django uses that manifest. Check that ports 8000 and 9091 are free before starting; do not stop another project's service to claim them.

Webpack hot updates and browser reloads are not the same as restarting Django's Python process. Django's `runserver` handles Python autoreload; template-change browser reloads require a [separate watch configuration](https://python-webpack-boilerplate.readthedocs.io/en/latest/live_reload/). The plain `watch` workflow above does not promise automatic browser reloads.

When returning to production, stop the watcher or development server, run `npm run build`, then run `collectstatic` again. Otherwise you can deploy a manifest still pointing at localhost:9091.

## If something is missing

- **PostCSS asks for `@tailwindcss/postcss`, or `tailwindcss/nesting` is not exported:** check `npm ls tailwindcss`. This guide needs 3.4.17, not v4. Choose one version's complete setup.
- **No manifest:** finish a successful build first and check the `MANIFEST_FILE` path.
- **No styling:** check the `index` entry, CSS requests, template scan paths and literal class names before changing package versions.
- **Assets point at port 9091 after deployment:** rebuild in production mode and recollect static files. Do not publish a development manifest.

You now have a version-scoped Webpack/Tailwind pipeline and concrete checks for the handoff to Django. Use the [template formatter](/tools/format-html/) when editing the examples, without pasting private template data into an online tool.
