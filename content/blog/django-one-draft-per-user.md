---
id: 158
created: '2026-11-21T10:50:00+00:00'
modified: '2026-11-21T10:50:00+00:00'
title: How to enforce one draft per user in Django
slug: django-one-draft-per-user
status: PB
description: Use a conditional UniqueConstraint to allow many published stories but only one draft per user. Test both new drafts and reopened stories before rollout.
level: INTERMEDIATE
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 2
  name: Models
  slug: models
author: 1
---
Alice has two published stories and one unfinished piece. She opens an old story and clicks **Move back to drafts**. Should that work? If your editor promises each author a single draft, reopening a story has to obey the same rule as creating one. Disabling the **New draft** button covers only one of those paths.

In Django, put a conditional `UniqueConstraint` on the owner, restricted to rows where the status is `"draft"`. On a database that supports it, this allows **zero or one draft per owner** and any number of published stories. Here is how to build it, test the transition a create-only test misses, and check whether your existing data can accept it.

## Decide what uses up the draft slot

The important question is not which fields describe a story. It is which rows should compete with each other. Alice's draft competes with her other drafts, not with Bob's or with her own published work. The key is therefore the owner, and the condition is the draft status. Making `(owner, status)` unique instead would reject Alice's *second published story*, too.

If you're evaluating a [Django project with source code](/projects/), look for these two pieces separately in the model or migration. A collaborative editor might want one working copy **per document**, not per person. In that product, making the author unique would stop an editor from working on two different documents. Decide which behavior your reader or contributor should see before copying a constraint.

Try these three product questions with whoever owns the editor:

- **Can an author write in two publications?** If Alice should have a separate scratchpad in the Sunday edition and the weekday edition, the key is the owner *and* the publication. A per-owner rule would make the weekday editor refuse new work because of a draft Alice cannot even see on that screen.
- **Can a draft change hands?** If a team lead assigns Bob’s draft to Alice while Alice already has one, changing only the owner crosses the uniqueness boundary too. Decide whether to prevent the handoff or let Alice choose which piece to finish first. If transfers are part of your workflow, add that owner change as a separate rejection case.
- **Does a scheduled story still count as a draft?** A story waiting for tomorrow’s publication is neither being written nor publicly visible. If authors can start the next piece as soon as they schedule this one, exclude scheduled stories. If an author can have only one unpublished submission under review, include the appropriate review states in the condition. Name the constraint after the promise you actually make.

## Put the rule on the model

For a new app named `stories`, put this in `stories/models.py`. The [Django constraints reference](https://docs.djangoproject.com/en/5.2/ref/models/constraints/#django.db.models.UniqueConstraint.condition) gives the one-draft pattern; below we use it with a non-null owner and a lower-case stored status.

```python
from django.conf import settings
from django.db import models


class Story(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, default="draft")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner"],
                condition=models.Q(status="draft"),
                name="stories_one_draft_per_owner",
            ),
        ]
```

`settings.AUTH_USER_MODEL` refers to the user model your project actually uses; you needn't copy its class into the stories app. If you're deciding on that model in a new project, see the [Django authentication setup guide](/blog/user-authentication).

If your story inherits [reusable timestamp fields](/blog/reusable-models), keep this constraint on the concrete story model: an author’s draft limit is not a property of every dated record.

Add `stories` to `INSTALLED_APPS`. On a **new development database**, generate the migration, inspect it, and apply it:

```shell
python manage.py makemigrations stories
python manage.py sqlmigrate stories 0001
python manage.py migrate
```

On Django 5.2.14 with SQLite 3.53.1, the generated migration produced this index (line breaks added):

```sql
CREATE UNIQUE INDEX "stories_one_draft_per_owner"
ON "stories_story" ("owner_id")
WHERE "status" = 'draft';
```

Only the rows selected by the `WHERE` clause enter this [SQLite partial index](https://www.sqlite.org/partialindex.html). Publishing a draft removes its row from that set without deleting the story. Reopening a story puts its row back into the set, which is why a plain update can also fail. The rule doesn't validate workflow states: a misspelling such as `"darft"` falls outside the set. If arbitrary status strings must be impossible, enforce the allowed values separately.

## Test the rejected write and the data left behind

Put the following in `stories/tests.py` and run `python manage.py test stories`. The fixture uses Django's default user model; adapt the two user creations if your user manager expects an email address or another identifier.

```python
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Story


class DraftSlotTests(TestCase):
    def test_creating_publishing_and_reopening(self):
        alice = get_user_model().objects.create_user(username="alice")
        bob = get_user_model().objects.create_user(username="bob")

        first = Story.objects.create(owner=alice)
        Story.objects.create(owner=bob)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Story.objects.create(owner=alice)

        first.status = "published"
        first.save(update_fields=["status"])
        current = Story.objects.create(owner=alice)
        Story.objects.create(owner=alice, status="published")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Story.objects.filter(pk=first.pk).update(status="draft")

        first.refresh_from_db()
        self.assertEqual(first.status, "published")
        self.assertEqual(Story.objects.get(owner=alice, status="draft"), current)
        self.assertEqual(Story.objects.filter(owner=alice, status="published").count(), 2)
```

This test passed against the generated migration on the SQLite version above. Alice and Bob could each start a draft. Publishing Alice's first draft freed her slot; reopening it after she'd started another draft raised `IntegrityError`. Reading the rows back confirmed she still had her newer draft **and both** published stories. This is a sequential database test, not a measurement of simultaneous writers.

The two context managers are ordered deliberately. The write fails inside the inner `atomic()` block, which rolls back before `assertRaises` catches the exception. That leaves the surrounding test transaction available for the next query. See Django's [transaction error-handling example](https://docs.djangoproject.com/en/5.2/topics/db/transactions/#controlling-transactions-explicitly).

In the editor, an early “you already have a draft” check can offer a link to the existing story. It cannot reserve the slot: two requests can both check before either has inserted a draft. Keep the database rule, and decide what the losing request should show. For a blank draft, opening the existing one might be fine. For a submitted story with text, preserve the submitted text and explain the conflict rather than silently redirecting the writer. Don't translate *every* integrity error into “draft exists”; unrelated failures need their own handling.

### Two tabs: a duplicate row versus a lost edit

Imagine Alice opens two browser tabs before either tab has a draft ID. She types a different opening paragraph in each, then submits the first. The second request still thinks it is creating a story. A conflict here means **another row already occupies the slot**, not that the first tab contains the same text. Show a link to the occupying draft alongside the unsaved submission, so Alice can copy what she needs or go back. Returning a success message for that second write would tell her both paragraphs were saved when only one was.

Now change one detail: both tabs opened an *existing* draft and submitted edits to that same row. The uniqueness rule has nothing to reject; there is still only one draft. If your editor promises to detect stale edits, test that promise independently. For example, give each edit a revision number, submit the revision the tab originally loaded, and update the row only if that revision still matches. When the conditional update changes no row, offer a comparison rather than overwriting the newer paragraph. A draft-slot test can be green while this part of the editing experience is broken.

## Adding the constraint to a live table

Before adding the constraint, find owners who already occupy more than one slot. In a Django shell against the target data, run this read-only query:

```python
from django.db.models import Count
from stories.models import Story

duplicates = (
    Story.objects.filter(status="draft")
    .values("owner_id")
    .annotate(drafts=Count("pk"))
    .filter(drafts__gt=1)
    .order_by("owner_id")
)
for row in duplicates:
    print(row["owner_id"], row["drafts"])
```

This audit counts stories without joining their comments or tags. If you extend it to report on both, check [how related-table joins can inflate Django annotations](/blog/django-annotate-inflated-sums) before using the numbers to select records.

Each result is an editorial decision. If Alice already has three drafts, which one should open when she clicks **My draft**? Preserve the others through an agreed archive or merge process. Don't publish someone's unfinished writing or discard rows just to make the migration pass.

Read the audit output as *owners*, not stories. For example, a hypothetical line saying owner 42 has three drafts means two stories need a disposition; it does not tell you which two. Open those records with their titles, most recent edits, and references from the editorial workflow. An older draft that already has review comments may be more important to preserve as the working copy than the newest empty draft. Keep a record of the selected story and the disposition of each extra one, so a writer can still find work that moved.

Check the vocabulary in old data too. Group rows by their stored status and review surprising spellings or obsolete states before trusting an empty duplicate report. That report only sees rows matching the literal predicate. If the old editor wrote an uppercase status and the new one uses lowercase, Alice might appear to have a free slot while the old interface still shows an unfinished story. Agree on the mapping first, apply it on the rehearsal copy, and rerun the duplicate query against the normalized values.

Rehearse the migration on a copy of the data using the **production database engine**. Coordinate draft writes during cleanup and index creation: an empty audit result is only a snapshot, and another duplicate can invalidate it before the constraint is installed. Inspect the SQL for the actual migration number and run the transition test against that backend as well.

We also applied the generated migration on a fresh PostgreSQL 15.20 database. The catalog showed a unique index on `owner_id` with the predicate `((status)::text = 'draft'::text)`. The same Django transition test passed there, including the check that the rejected update left the old story published. The [PGSandbox partial-index testing guide](https://pgsandbox.dev/blog/test-postgresql-partial-indexes/) shows how to read it from the catalog and verify the stored rows after a conflicting transition. Use the same checks on your deployed database version; neither run simulated concurrent editing.

This last check matters if you develop on SQLite but deploy elsewhere. Django documents [backend restrictions for conditional indexes](https://docs.djangoproject.com/en/5.2/ref/models/indexes/#condition), and [system check models.W036](https://docs.djangoproject.com/en/5.2/ref/checks/#models) flags databases without conditional unique constraints. MySQL and MariaDB do not provide this guarantee through the model declaration. On such a backend, consider storing the single editable draft in a separate table with a unique owner, with published stories in a history table. In either design, the acceptance test is the same: reject the second draft, keep both published stories, and never let reopening one overwrite someone’s work.
