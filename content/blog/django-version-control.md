---
id: 3
created: '2022-04-27 01:51:55.365000+00:00'
modified: '2022-08-05 19:34:47.734000+00:00'
title: How to Version Control your Django project
slug: django-version-control
status: PB
description: In this post, we will be talking about version control and the best practices when it comes to Django
  projects.
unsplashID: HK8IoD-5zpg
icon: image/upload/v1659728648/blog-post-icon-prod/uodmzn0vi18wjawqk38w.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 6
  name: git
  slug: git
- id: 7
  name: Github
  slug: github
author: 1
---
In the previous post, we have gone through the process of [setting up a basic Django project](https://builtwithdjango.com/blog/basic-django-setup). In this post, we will be talking about version control and the best practices when it comes to Django projects.

TL;DR use the [following .gitignore](https://gist.github.com/rasulkireev/1412ab0c3585ab8ffa50764e68f2d6d7).

I'm not going to be teaching you git in this post. I'm going to assume that you have git installed on your computer and you have a Github account. If you haven't worked with git before I recommend you check out [this post](https://phoenixnap.com/kb/how-to-use-git), it helped me when I was learning, but really there are a [ton of other awesome posts](https://duckduckgo.com/?q=how+to+git&ia=web).

However, that said, this post is aimed toward beginners when it comes to version controlling Django projects.

## Why?

Why is it important to dedicate an entire post on how to version control your Django project?

When I was starting out I was just doing stuff and not using tutorials. I was silly, unlike you! I ended up putting secret information to the public. For example, I was using AWS to host images, and accidentally put my secret key on Github. I was contacted by the Amazon team and was told to delete it and immediately create a new one so that some bad actors would use it maliciously. I almost sh\*t my pants. I don't want this to happen to you!

Another important point is that eventually (in the next post) we are going to be creating a SQLite database and storing user information on it. We don't want to expose that either.

So, now that you understand the importance of good practices when it comes to version control we can begin.

The good news is that it actually is not so hard.

## Beginning of History

After you finished the previous post, you should have a functional code. Make sure everything works by running `poetry run python manage.py runserver`.

Let's start by creating a repo for your project on [Github](https://github.com). If you head over to https://github.com/new you will be prompted for some info.

Give your repo a name and press "Create repository". No need to change anything else. 

> Tip: use kebab case for the name: something-like-that.

Once you've done that you will see a convenient list of instructions on Github:
![New repo github instructions](https://res.cloudinary.com/built-with-django/image/upload/v1651024342/blog-images/new_repo_github_instructions_20220426204620_cscxm4.png)

We don't need the first line, since we already have some files.

We do however need to run `git init`  in our terminal (hopefully in an integrated VS Code terminal) to start the version control history. Once you run `git init` you should see a couple of changes.

First is the terminal itself will show the branch you are on:
![Terminal after running git init](https://res.cloudinary.com/built-with-django/image/upload/v1651024342/blog-images/terminal_after_running_git_init_20220426205310_xkhzjh.png)

Second is the File Explorer, all files should have turned green meaning that they are new files in our repo, they haven't appeared before in our history. If files had existed but were changed, they would have turned yellow.
![File Explorer after git init](https://res.cloudinary.com/built-with-django/image/upload/v1651024342/blog-images/file_explorer_after_git_init_20220426205435_exi43i.png)

## Ignoring secrets

Awesome! Now, before adding all our files to our repo history let's create a `.gitignore` file in which we will list all the files and folders that we don't want to end up in the history.

So, create `.gitignore` file at the root of your project. Copy the content from the [following gist](https://gist.github.com/rasulkireev/1412ab0c3585ab8ffa50764e68f2d6d7) and paste it into the `.gitignore` file. Now files and folders that match the Regex in `.gitignore`, will not be version controlled. 

You should care about most of them. Here are the important ones:

- `.env`. We will be storing our secrets in this file, so we don't want them to end up on Github.

- `*.sqlite3`. We don't want any database to end up on Github either.

- `node_modules/` this is where all Javascript packages will be stored, once we get there. `node_modules/` are notoriously large directories, so we don't want them to be on Github as they will slow up all actions immensely.

- `media/` when we are going to work locally, some images that we will upload into our database will end up in the media folder. Since Github has some rules regarding how much space you can take, we don't want any images to end up there, as they tend to be heavy.

- other than that you shouldn't worry too much about other things, at least for now.

## Final Steps

Now we can run other commands provided by Github. In your terminal run:

1. `git add --all` to add all the files (except the ones in `.gitignore`) to version control history.
2. `git commit -m "first commit"`, to "commit" the changes.
3. `git branch -M main` to rename the main branch. New standard.
4. `git remote add origin git@github.com:{your username}/{your project name}.git`. Use the command provided by Github.
5. Finally, run `git push -u origin main`

If you didn't run into any issues, then you can try reloading the Github page and seeing if the files have been added to the repo.

If all is good, then congratulations.

## Conclusion

In this post, we have created a repo and committed our files to it. This will help us keep track of our code in future posts.