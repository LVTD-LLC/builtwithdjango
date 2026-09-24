---
id: 1
created: '2021-08-29 03:51:12.344000+00:00'
modified: '2025-04-01 10:26:27.761551+00:00'
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
Update: Thanks to ajit for pointing out an error I made, where I imported User model from user.models file instead of CustomUser. Fixed. Thanks ajit!

Whenever you are building a site with [Django](https://www.djangoproject.com) that will have user authentication, it is recommended to create a [Custom User Model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/) before the first migration. Sometimes you forget to do that. In this case, you have to follow a strict procedure, which I'll show you in the post.

This was [Issue was discussed at length](https://code.djangoproject.com/ticket/25313) by the Django community. There is now a consensus about the best and the least painful way to do that. I'd like to take that discussion and summarize it into a set of actionable steps.

### 1. Create the `users` app

Make sure you are inside your project directory.
```bash
python manage.py startapp users
```

Then, add the following to the models.py:
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Meta:
        db_table = 'auth_user'

```

If you don't specify the name, you'll receive an error:
> django.db.utils.OperationalError: no such table: users_customuser

Then, register the new Model in the admin panel:

```python
# In users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

admin.site.register(CustomUser, CustomUserAdmin)
```

### 2. Update `settings.py` file
* In `settings.py` add to `INSTALLED_APPS` (`"users.apps.UsersConfig",`)
* Add a `AUTH_USER_MODEL = 'users.CustomUser'` line to the bottom of the `setting.py` file.

### 3. Replace User imports
In your project code, replace all imports of the Django User model:
```python
from django.contrib.auth.models import User
```
with the new, custom one:
```
from users.models import CustomUser
```

### 4. Delete Old Migrations
Run the following two commands in your terminal, from the root of your project:

1. `find . -path "*/migrations/*.py" -not -name "__init__.py" -delete`
2. `find . -path "*/migrations/*.pyc" -delete`

### 5. Create New Migrations
```
python manage.py makemigrations
```

### 6. Truncate (delete) contents of the migrations table

You will need to do this manually by going inside your database (Postgres, sqlite3, MySQL, etc.).

I was using sqlite3 at the time, so I had to do the following:
```
# login into the sqlite database
sqlite3 db.sqlite
# Then run the following
> DELETE FROM django_migrations;
> .quit
```

If you are using Postgres, you will have to first login into your database and then run:

```
TRUNCATE TABLE django_migrations;
```

### 7. Fake apply new migrations
```bash
python manage.py migrate --fake
```

### 8. Test
```bash
python manage.py runserver
```

This should be it. If you went through each step sequentially, your app should be using a Custom User Model. Congrats!

## Bonus Video

If you prefer a more visual approach, I've made a video that shows how to migrate to a Custom User Model mid-project.

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/k0GwrwC5uuo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

If you have any feedback, please let me know on [Twitter](https://twitter.com/rasulkireev/status/1329393168840871936). Your likes, retweets, and replies will show up here.