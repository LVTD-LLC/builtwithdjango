# Public product facts

Verified 2026-09-20 from PRODUCT.md, routes and live pages:

- The site is a Django community showcase and learning hub (homepage).
- Public project discovery uses published, active, non-spam records (projects/views.py and builtwithdjango/sitemaps.py).
- Project submission requires sign-in (projects/views.py, anonymous GET redirects to login preserving next).
- Secret-key generation and HTML formatting have public tool routes (tools/urls.py).

Do not claim verified Django use for every user submission without review. Search visibility, schema presence and conversions are different measurements. Dated private claim observations live in the configured Rowset history store.

- CDN performance guide: the previous internal study link returned 404 and did not substantiate a 40% FCP improvement. Replace it with deployment guidance, not a promised speedup. Source: https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/ (rechecked 2026-09-25). Applies in content/blog/5-hidden-django-secrets-senior-developers-use-lightning-fast-code.md; live verification required after deploy.

- Power-features article (verified 2026-09-29): the cited JetBrains URL is unavailable and GitHub's Django topic directory is not a benchmark supporting the article's four percentages. Do not promise quantified improvements. Django 5.2 documents signal debugging trade-offs, custom command behavior, and generic-relation query/index limitations. Sources: https://docs.djangoproject.com/en/5.2/topics/signals/, https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/, https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/.

- Frontend comparison (verified 2026-09-30): Built with Django renders Django templates with Stimulus, Turbo, and Alpine.js, not a React SPA (TECH.md, package.json, templates/base.html, frontend/src). Next.js authentication requires implementation/integration; its guide recommends an auth library (https://nextjs.org/docs/app/guides/authentication). Cookiecutter Django's DRF and asset-pipeline options do not supply a generated React/Vue app (https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/project-generation-options.html). React can enhance part of an existing page (https://react.dev/learn/add-react-to-an-existing-project).

- Cursor guide (verified 2026-10-04): Django 5.2 `connection.cursor()` takes no named-cursor argument (installed Django 5.2.14 signature and reproduction). `QuerySet.iterator()` avoids the QuerySet cache; PostgreSQL server-side streaming depends on backend/pool settings. Django supports ORM `Window` expressions. No verified benchmark supports the former 80% import-speed claim. Sources: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#iterator, https://docs.djangoproject.com/en/5.2/ref/models/expressions/#window-functions, https://docs.djangoproject.com/en/5.2/topics/db/optimization/.

- Overlooked-features article (verified 2026-10-06): generic object IDs must accept the target primary-key types; generic relations lack a database constraint to the target. Signals are not universally preferable to explicit calls; receivers must be registered and respect swappable users/raw loads. F-based increments avoid a Python lost-update pattern, while Q builds predicates and update() skips save signals. Sources: https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/, https://docs.djangoproject.com/en/5.2/topics/signals/, https://docs.djangoproject.com/en/5.2/ref/models/querysets/#update. Examples are verified separately; no performance guarantee.
