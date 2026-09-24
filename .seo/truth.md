# Public product facts

Verified 2026-09-20 from PRODUCT.md, routes and live pages:

- The site is a Django community showcase and learning hub (homepage).
- Public project discovery uses published, active, non-spam records (projects/views.py and builtwithdjango/sitemaps.py).
- Project submission requires sign-in (projects/views.py, anonymous GET redirects to login preserving next).
- Secret-key generation and HTML formatting have public tool routes (tools/urls.py).

Do not claim verified Django use for every user submission without review. Search visibility, schema presence and conversions are different measurements. Dated private claim observations live in the configured Rowset history store.

- CDN performance guide: the previous internal study link returned 404 and did not substantiate a 40% FCP improvement. Replace it with deployment guidance, not a promised speedup. Source: https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/ (read 2026-09-24). Applies via blog migration 0013; live verification required after deploy.
