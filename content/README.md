# Blog publishing

`blog/<slug>.md` is the source of truth for all blog posts. Public views, homepage
cards, RSS, sitemap, and the token-authenticated read API load these files, never
the legacy Post table. Edit through a branch and PR; merging/deploying publishes
the change. No database migration or API write is needed for content edits.

Each file has YAML front matter between `---` lines, followed immediately by the
Markdown body. Copy an existing post as a starting point. Required metadata:

- `id`: stable positive integer, unique across files; use a new unused ID for new posts.
- `author`: existing author ID, retained for API compatibility (not an account export).
- `slug`: must match the filename; keep existing slugs to preserve URLs.
- `title`, `description`, `tag_list` (list of `{id, name, slug}` mappings).
- `status`: `PB` (published) or `DR` (hidden from all public surfaces).
- `type`: `TUTORIAL`, `ARTICLE`, `INTERVIEW`, or `UPDATE`.
- `level`: `BEGINNER`, `INTERMEDIATE`, `ADVANCED`, or an empty string.
- `created`, `modified`: timezone-aware ISO timestamps. Preserve `created` when
  editing; update `modified` only for substantive changes.
- Optional `icon` and `unsplashID`: preserve existing image references.

This repository is public: **do not commit confidential drafts**. `DR` only hides
content on the website, not in Git. Content is trusted editorial Markdown and
uses the same HTML, code-block rendering, and Markdown extensions as before.

Run `python manage.py check --settings=builtwithdjango.test_settings` and `pytest`
in the documented test environment before merging. The Django system check
rejects malformed metadata, duplicate IDs, missing directories, and empty inventories.
The Docker image copies `content/` along with application code.

## Cutover and rollback

All 28 published production posts were exported on 2026-09-24, including original
body bytes, publication/modification timestamps, tags and 15 Cloudinary icons.
No unpublished records existed in this export. Before merging, compare a fresh
read-only database export with the committed snapshot to catch intervening edits.

The legacy Post/Tag/Comment models and tables are retained, unchanged, as an
archive for rollback and existing comment foreign keys. Their admin is read-only.
`/api/v1/posts/` and `/api/v1/posts/<id>/` retain superuser-token read access,
including status/type/level list filtering; POST/PUT/PATCH/DELETE now return 405.
Update publishing automations to edit these Markdown files via PR, not the API or
content data migrations. No automated database deletion or backfill occurs.

Rollback by reverting the cutover commit and deploying the prior version. Changes
made to Markdown after cutover are not copied back into the archive automatically;
reconcile those changes before rolling back. Remove archive tables only as a
separate, explicitly approved data-retention task.
