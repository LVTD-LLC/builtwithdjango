---
id: 9
created: '2024-05-22 06:48:45.298332+00:00'
modified: '2024-05-22 06:48:45.298332+00:00'
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

In this lesson we will create out first "app" where we will store most of our code and will set up a reusable `BaseModel` that we will use for all our models going forward.

You can see all the code that I wrote for this post in [this PR](https://github.com/builtwithdjango/basic-django/pull/3/files).

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

*  Create a `base_models.py` file with a `BaseModel` class:

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

Please note, that `models.Model` class that we are inheriting will create an `id` field automatically. That reason I'm not adding `primary_key=True` to the uuid field. I still want Django to autogenerate `id` field for me. 

And the reason I wanted to create `uuid` field is that I would rather for this to be used for urls and other such things, since `id` field is very easy to guess for potential attackers/hackers. 

This is not something you need to get into right now. It is also not a requirement, just something I like to do now. If you want to know more about this, let me know, I'll do a separate post about this.

> Note: if you don't add the `Meta` class with `abstract = True`, this will bite us in the ass later down the line. This block tells django not to create a table called base_model, but only use that as (you guessed it) an abstract class.

> I once made that mistake in another app, was not able to undo it in prod ever since 😢

* Create a new model in the `core/models.py`. 

Let's say we want to let users create blog posts, the most generic/basic example out there. The usage of the BaseModel will look like this:

```python
from django.db import models
from .base_models import BaseModel

class BlogPost(BaseModel):
  user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
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

* Don't forget to add `core` to `INSTALLED_APPS` in your `settings.py` 
* Run `poetry run python manage.py makemigrations` and then `poetry run python manage.py migrate` to create new tables in your DB.
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

Now you can reuse that BaseModel in all the other models, knowing that all the necessary fields that need to be on each model will be there. 

The main advantage of this approach is that we don't have to write the same boilerplate code every single time, thus our code will be a little more [DRY](https://en.wikipedia.org/wiki/Don't_repeat_yourself).

If you have any questions please let me know by [emailing me](mailto:rasul@builtwithdjango.com) or down in the comments below.