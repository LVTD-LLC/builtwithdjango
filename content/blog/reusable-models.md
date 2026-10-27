---
id: 9
created: '2024-05-22 06:48:45.298332+00:00'
modified: '2026-10-27 08:45:00+00:00'
title: How I Use Reusable Models in Django
slug: reusable-models
status: PB
description: Use reusable models for dry up your code.
unsplashID: OTDyDgPoJ_0
icon: image/upload/v1716360525/blog-post-icon-prod/uromsg96jghowymkmra1.png
level: BEGINNER
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
## Introduction

We are going to continue the series of beginner posts which point to this [basic-django repo](https://github.com/builtwithdjango/basic-django). 

In the [previous post](https://builtwithdjango.com/blog/improve-your-code-with-pre-commit) we have setup up pre-commit for automatic code checking and formatting.

An abstract Django model lets several models share fields without creating a table for the base class. Here we'll give a blog post a UUID and creation/update timestamps, then check what actually reaches the database.

The updated examples were checked with Python 3.11, Django 5.2.18 and SQLite. Start with the [basic Django setup](/blog/basic-django-setup); the example works with Django's default user or the custom user you already configured. You do not need to change `AUTH_USER_MODEL` to follow it.

The [original example PR](https://github.com/builtwithdjango/basic-django/pull/3/files) is historical; use the updated snippets below for this walkthrough.

## Caveat

Let's get the discussion of "apps" out of the way (and other small things).

When it comes to structuring your app there are people who like to create a separate app for each part of your application. For example, you have a SaaS that automates Twitter posting for your users. You can have a separate "app" that deals with auth, separate "app" for the blog part of your application, and a separate app for the "core" functionality.

I was one of those people. It felt much nicer semantically, that each part of the application, sits in a separate app. But I was recently converted.

I tried working on codebases that had most logic in a single "core" app, I realized that having all the code in one dir has it's advantages. No need to jump between files, since everything is contained in one location.

There are disadvantages of course... For example, as your project grows, the files will get huge.

As with all things in life there are tradeoffs. And when it comes to programming specifically, there are a gazillion ways of doing one thing.

All of this to say, is that I picked the latter approach for this blog post. If you thing there are better ways, feel free to [email me](mailto:rasul@builtwithdjango.com) or comment down below. I'm open to all suggestions.

With all this out of the way, let's get into it

## Our Core

* Once you are in your repo, run this command in your terminal to create your new app: `poetry run python manage.py startapp core`. 

> Note: If you are wondering about why you have to add `poetry run` to this command, read [this post](https://builtwithdjango.com/blog/basic-django-setup).

This will create the following folder:

```
...
├── core
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   └── views.py
...
```

* Create `core/base_models.py` with a `BaseModel` class. This follows Django 5.2's [abstract base model pattern](https://docs.djangoproject.com/en/5.2/topics/db/models/#abstract-base-classes):

```python
import uuid
from django.db import models

class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

A concrete subclass gets an automatic primary key unless you define one yourself. Here `uuid` is a separate field, not the primary key. Random UUIDs make identifiers harder to enumerate, but **a UUID is not authorization**: a view still needs to check who may access the object. This field also has no database uniqueness constraint; if you use it for unique URL lookups, plan and validate that constraint rather than assuming randomness enforces it.

Keep `abstract = True`. Django copies these fields into each concrete subclass; it does not create a base table. Without it, you get multi-table inheritance instead. Existing production tables need a deliberate migration plan, not a delete-and-rebuild shortcut.

* Create a new model in the `core/models.py`. 

For `core/models.py`, reference the configured user model through `settings.AUTH_USER_MODEL`, as the [Django 5.2 authentication guide](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#referencing-the-user-model) recommends. A hard-coded `users.CustomUser` fails when that app/model is absent:

```python
from django.conf import settings
from django.db import models

from .base_models import BaseModel


class BlogPost(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
```

* Let's add this to the `core/admin.py` so that we can see the effect in the Admin Panel:

```python
from django.contrib import admin
from .models import BlogPost

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "created_at", "updated_at", "title", "content")

admin.site.register(BlogPost, BlogPostAdmin)
```

Note: that we are adding fields that are not directly written on the BlogPost model.

* Add `core` to `INSTALLED_APPS` in your `settings.py`. Keep the existing user model. If you already migrated a project, don't switch it just for this example; see the [custom-user migration alternatives](/blog/custom-user-model-migration-mid-project-django). 
* Run `poetry run python manage.py check`, then `poetry run python manage.py makemigrations core` and `poetry run python manage.py migrate`. Inspect the migration: for this example it creates `BlogPost`, including the inherited fields, not a separate `BaseModel` table.
* Create a local admin account with `poetry run python manage.py createsuperuser` if you don't already have one.
* If everything ran successfully, let's start the server with `poetry run python manage.py runserver` and head over to `http://127.0.0.1:8000/admin/`

You should see this new part:
![new model shows up](https://res.cloudinary.com/built-with-django/image/upload/v1716359667/blog-images/new_model_shows_up_vyuhef.png)

Click on it.

* Now you will see an almost empty page. Let's create a new post by clicking here:
![create new post from admin](https://res.cloudinary.com/built-with-django/image/upload/v1716359779/blog-images/CleanShot_2024-05-12_at_15.15.54_2x_eivenz.png)

* Enter some details and and click save:
![add data to new post from admin panel](https://res.cloudinary.com/built-with-django/image/upload/v1716359779/blog-images/CleanShot_2024-05-12_at_15.17.04_2x_p6njqy.png)

Note: that we are only asked to enter the details that we added on the BlogPost model directly, and the ones from BaseModel are not required. This is because all the fields we have added on BaseModel are assigned automatically. If there was a field that required user input, it would also show up.

* After the post has been created you will see that all the other fields also show up on the new BlogPost instance.
![View new post in admin panel](https://res.cloudinary.com/built-with-django/image/upload/v1716359877/blog-images/new_blog_post_slqqgo.png)

## Check the timestamps, not just the admin form

`auto_now_add` sets the creation time on the first save; `auto_now` sets the update time when that field's save processing runs. Neither is a database trigger. In Django 5.2, `save(update_fields=["title"])` leaves `updated_at` alone. Include it when the timestamp should advance:

```python
post.title = "Revised title"
post.save(update_fields=["title", "updated_at"])
```

A queryset `update()` bypasses model `save()` entirely. Set the timestamp explicitly for that path:

```python
from django.utils import timezone

BlogPost.objects.filter(pk=post.pk).update(
    title="Updated directly", updated_at=timezone.now()
)
```

These are the documented [partial-save rules](https://docs.djangoproject.com/en/5.2/ref/models/instances/#specifying-which-fields-to-save) and [queryset update behavior](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#update), not a bug to fix with a hidden save override.

To make the distinction reproducible, put this Django 5.2 test in `core/tests.py`. It uses a controlled clock rather than sleeps. The test user is fixture data for this example, not a production account:

```python
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from .base_models import BaseModel
from .models import BlogPost


class BaseModelTests(TestCase):
    def test_inherited_fields_and_timestamp_write_paths(self):
        # Adapt fixture fields if your custom user doesn't accept username.
        user = get_user_model().objects.create(username="model-example")
        first = timezone.now()
        later = first + timedelta(minutes=1)
        with patch("django.utils.timezone.now", return_value=first):
            post = BlogPost.objects.create(user=user, title="First", content="Text")

        self.assertTrue(BaseModel._meta.abstract)
        self.assertNotIn(BaseModel._meta.db_table, connection.introspection.table_names())
        self.assertIsNotNone(post.pk)
        self.assertIsNotNone(post.uuid)
        self.assertEqual(post.created_at, first)
        self.assertEqual(post.updated_at, first)

        with patch("django.utils.timezone.now", return_value=later):
            post.title = "Partial save"
            post.save(update_fields=["title"])
            post.refresh_from_db()
            self.assertEqual(post.updated_at, first)

            post.save(update_fields=["updated_at"])
            post.refresh_from_db()
            self.assertEqual(post.updated_at, later)

        BlogPost.objects.filter(pk=post.pk).update(title="Direct update")
        post.refresh_from_db()
        self.assertEqual(post.updated_at, later)
        explicit = later + timedelta(minutes=1)
        BlogPost.objects.filter(pk=post.pk).update(updated_at=explicit)
        post.refresh_from_db()
        self.assertEqual(post.updated_at, explicit)
        self.assertEqual(post.created_at, first)
```

Run `poetry run python manage.py test core`. You should get one passing test. This exercises an isolated SQLite example; it is not an authorization, concurrency or production migration test. For an email-only custom user, adjust the fixture creation to your model's required fields; the model relation itself stays the same.

You can now reuse `BaseModel` where these fields fit, with a test showing which write paths update its timestamps. 

The main advantage of this approach is that we don't have to write the same boilerplate code every single time, thus our code will be a little more [DRY](https://en.wikipedia.org/wiki/Don't_repeat_yourself).

If you have any questions please let me know by [emailing me](mailto:rasul@builtwithdjango.com) or down in the comments below.