---
id: 1
created: '2021-08-29 03:51:12.344000+00:00'
modified: '2026-10-22 08:45:00+00:00'
title: Migrating to a Custom User Model mid-project in Django
slug: custom-user-model-migration-mid-project-django
status: PB
description: In this post will go through the process of migrating to a Custom User Model in the middle of the project.
unsplashID: V72Hk6LjjjI
icon: image/upload/v1659728552/blog-post-icon-prod/wjbpttmewkslzlwmftlu.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 2
  name: Models
  slug: models
- id: 3
  name: Custom User Model
  slug: custom-user-model
author: 1
---
Changing `AUTH_USER_MODEL` after a Django project has database tables is not a routine settings change. It affects the migration graph, user relationships and authentication behavior. There is no universal, data-preserving command sequence for every existing project.

> Correction, October 22, 2026: the earlier version of this guide recommended deleting migration files, clearing migration history and fake-applying replacements. That is not a safe general procedure for an existing database. Those instructions have been removed. Keep your migrations and rehearse any user-model change on a restored copy before touching production.

## First, decide whether you need to replace the user model

If you only need extra information such as a timezone or biography, a separate profile model can avoid changing the authentication model. If you need different login identifiers or fundamental authentication behavior, evaluate a custom user model against your authentication packages and existing schema.

For a brand-new project, make the custom-user decision **before the first migration**, following the [Django authentication walkthrough](/blog/user-authentication). Start with the [basic Django setup](/blog/basic-django-setup) if you do not yet have a project. Neither fresh-project walkthrough is a migration plan for a database that already contains users.

Django's [custom-user documentation](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#changing-to-a-custom-user-model-mid-project) explains the dependency constraints and why a mid-project switch needs manual work.

## An additive alternative: keep existing users and add a profile

This example keeps `AUTH_USER_MODEL` unchanged. In an existing application named `profiles`, add:

```python
# profiles/models.py
from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    timezone = models.CharField(max_length=64, blank=True)
```

If that application does not exist, create it with `python manage.py startapp profiles` and add `"profiles"` to `INSTALLED_APPS` first. Keep its existing models if it already contains code. Then generate and inspect the additive migration:

```bash
python manage.py makemigrations profiles
python manage.py sqlmigrate profiles 0001
python manage.py migrate --plan
```

`0001` assumes this is the application's first migration; use the actual generated migration name otherwise. Review the operations against your database and follow your normal backup and deployment process before applying:

```bash
python manage.py migrate
```

A profile row is not created automatically for every user. Create or retrieve one explicitly in application code, for example in a Django shell:

```python
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()
user = User.objects.get(username="alice")  # An existing test account.
profile, created = Profile.objects.get_or_create(user=user)
profile.timezone = "Europe/Istanbul"
profile.save(update_fields=["timezone"])
```

The lookup assumes a username-based user model and an account named `alice`; adapt it to your actual user identifier. Handle missing profiles in views, and plan a separate backfill if every existing account needs one. A profile does not change how users log in or make email addresses unique.

The additive example was checked with Python 3.11 and Django 5.2.18 on SQLite: an existing user's password, group membership and related record remained usable after the profile migration. That is a bounded example, not validation of your production database or third-party authentication stack.

## If replacing the user model is necessary

Treat the switch as a project-specific migration with explicit acceptance checks, not a reset:

1. **Inventory the dependencies.** Record the current user model, applied migrations, foreign keys, many-to-many tables, admin history and authentication integrations. Include code that imports the built-in `User` directly.
2. **Restore a backup into an isolated environment.** Keep real personal data out of public repositories and logs. Confirm that the restored application works before changing it, and verify that you can restore again.
3. **Design the schema and migration-state transition together.** A table-name override alone does not reconcile migration history, content types or permissions. The replacement model must be created in its application's first migration to satisfy Django's swappable dependency rules; an existing graph may require restructuring and a carefully designed transition.
4. **Plan identity preservation.** Define what happens to user primary keys, password hashes, groups, permissions and every related record. Decide whether active sessions should survive or users should sign in again. Rehearse the transition and rollback with the database engine and versions you actually deploy.
5. **Test both upgrade and fresh installation.** Verify login, password reset, admin access, inactive-user rejection, object ownership and all authentication packages. Compare expected relationships as well as row counts. Confirm that a new empty database can still migrate successfully.
6. **Schedule the cutover.** Decide how to prevent conflicting writes, take the final backup, run the reviewed migration and check the application before reopening traffic. Document recovery steps before starting.

Do not clear the migration recorder to hide a dependency error. A fake migration records operations as applied without executing their database changes; it is not a schema repair. Use migration-state tools only when your reviewed plan establishes that database and state agree.

## If you already followed the old recipe

Stop further migration changes and preserve the current database and code for diagnosis. Compare them with the last known-good backup and version-controlled migration files in an isolated environment. Do not blindly rerun migrations or copy old migration-history rows into the live database. Choose restoration or a forward repair only after identifying what changed.

The [original video](https://www.youtube.com/watch?v=k0GwrwC5uuo) is historical context, not a production migration procedure. Use the corrected guidance above rather than its reset steps.
