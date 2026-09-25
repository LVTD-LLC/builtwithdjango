---
id: 8
created: '2023-03-31 17:35:13.533963+00:00'
modified: '2023-04-05 12:03:37.685143+00:00'
title: Improve your Django Code with pre-commit
slug: improve-your-code-with-pre-commit
status: PB
description: Get ready to improve your code in no time. Let the machine take care of that!
unsplashID: EXgfRVFJK4M
icon: image/upload/v1680284355/blog-post-icon-prod/n1fms264gudwmmii3m0w.png
level: BEGINNER
type: TUTORIAL
tag_list:
- id: 4
  name: Poetry
  slug: poetry
- id: 16
  name: pre-commit
  slug: pre-commit
- id: 17
  name: pylint
  slug: pylint
- id: 18
  name: flake8
  slug: flake8
- id: 19
  name: black
  slug: black
- id: 20
  name: djlint
  slug: djlint
- id: 21
  name: isort
  slug: isort
author: 1
---
> Update (04/01/2023): A kind reddit user by the name of [lanemik](https://www.reddit.com/user/lanemik/) suggested I give [ruff](https://github.com/charliermarsh/ruff) a go. So i decided to add it to the guide.

In the previous tutorial we have finished styling our Authentication pages. Before we go any further I would like to introduce you to an awesome developer tool that will improve your code, **a lot**!

**Meet [pre-commit](https://pre-commit.com).**

Pre-commit is a tool that allows you to automate the process of checking your code for errors and issues before committing it to your repository, hence the name. 

In simple terms, it will help you catch bugs and errors. Not only that, but it will also be able to sort your imports based on PEP recommendation as well as lint your code for better readability.

In this guide, I will show you how to set it up, and then I will share my favorite hooks that I use in all my projects.

### Table of Contents:

- [TL;DR](#tldr)
- [Follow Along](#follow-along)
- [Pre-Commit](#pre-commit)
    * [1. Install Pre-Commit](#1-install-pre-commit)
    * [2.  Create a `pre-commit` Config File](#2--create-a-pre-commit-config-file)
    * [3.  Install and Run your Hooks for the first time](#3--install-and-run-your-hooks-for-the-first-time)
    * [4.  Use Pre-Commit](#4--use-pre-commit)
- [Good Hooks to Use](#good-hooks-to-use)
    * [Black](#black)
    * [isort](#isort)
    * [flake8](#flake8)
    * [pylint](#pylint)
    * [djlint](#djlint)
    * [poetry export](#poetry-export)
    * [ruff](#ruff)
- [Conclusion](#conclusion)

## TL;DR ([^](#table-of-contents))
- See all the code from this tutorial [here](https://github.com/builtwithdjango/basic-django/pull/2)
- Install pre-commit
- Create `.pre-commit-config.yaml`
- Start adding hooks. Here are the ones I recommend:
	- black
	- isort
	- flake8
	- pylint
	- djlint
	- poetry export

## Follow Along ([^](#table-of-contents))
Before we continue, I would like to mention that you can look at all the code that we wrote in this tutorial by looking into the [pre-commit PR](https://github.com/builtwithdjango/basic-django/pull/2) on the [basic-django repo](https://github.com/builtwithdjango/basic-django).

All the previous tutorials have been applied to that repo too. If you have any questions or concerns, feel free to leave a comment below or on the PR. I'll try to respond as soon as I see the comment.

Finally, last comment before we begin is that you are following the whole series that you should see the same results as I will. However, if you are using a different repo, or you have wrote more code, then the `pre-commit` messages that you will receive might be slightly different.

But don't worry, even if they are different, they should be clear and very actionable.

## Pre-Commit ([^](#table-of-contents))
I am going to go through each step with you, but I encourage you to check out the [official website](https://pre-commit.com). The instructions they have are very useful.

### 1. Install Pre-Commit ([^](#table-of-contents))

You can install it on your whole system (MacOS) with `brew install pre-commit`, but we are also going to add it to our project explicitly with by running `poetry add --group dev pre-commit`. 

>Please note, the `--group dev`, this will add the dependency to the dev section. This is useful because when we install libraries in the production setting those won't be installed, thus using less storage space and increasing installation/deployment steps.

Let's confirm that the library has been installed by running `poetry run pre-commit --version`. If you don't know what this `poetry run` stuff is, I recommend you check my [Poetry guide](https://builtwithdjango.com/blog/basic-django-setup).

### 2.  Create a `pre-commit` Config File ([^](#table-of-contents))
Next, you will need to create a `.pre-commit-config.yaml` file in the root of your repository. This is where the magic happens. Once you create the file add the following text to it.

```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: check-yaml
    -   id: end-of-file-fixer
    -   id: trailing-whitespace
```

This file defines the pre-commit hooks that will be run. For example, in this specific case, we are using 3 hooks provided by pre-commit: `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`.

This is the structure we are going to follow when we want to add new hooks. Under the `repos` array we will specify an object that has the following:

- **repo**: the location of the hook (some libraries provide those hooks, but if one is not provided, we can write our own, we will do that later in that guide)
- **rev**: this is the version/release of the repo you have specified. If you look at the [`pre-commit-hooks`](https://github.com/pre-commit/pre-commit-hooks) library you can see it in the releases section: ![pre-commit repo release](https://res.cloudinary.com/built-with-django/image/upload/v1680282912/blog-images/pre-commit_repo_release_e1sgvz.png)
- **hooks**: now to the actual hooks that will be used from that repo. Again, check the pre-commit-hook repo to see what hooks are available (there are maaany), maybe you'll find them useful.

These specific hooks are pretty self explanatory, so instead of describing each one of those, let's just run this and see what happens.

> Please note, that if you are running it outside of your repo, it is not likely to do anything. You should set this up as part of some repo.

### 3.  Install and Run your Hooks for the first time ([^](#table-of-contents))
Once you have created your config file, you need to install the hooks specified in the file. You can do this by running: `poetry run pre-commit install`

Once this command is done, run `poetry run pre-commit run --all-files` which will run these hooks against your repo. You should see something like this:

![running pre-commit for the first time](https://res.cloudinary.com/built-with-django/image/upload/v1680283035/blog-images/running_pre-commit_for_the_first_time_pn7ccu.png)

So, what happened is that `pre-commit` checked all the files in the library and "fixed" them based on the hooks you have set up.

!!! danger "**!! Warning !!**"
    These first checks are harmless, so there is no worry about running them with --all-file. 
	
    However, later we will start adding hooks that format your code. If you have a large codebase, I don't recommend you run the `pre-commit run --all-files`, since that will affect a lot of the code. 

    Instead, you may want to start testing that the new hooks are working by running on one file at a time like so `pre-commit run --files YOUR_FILENAME`.

    If you would still prefer to "fix" the whole codebase, I will recommend you do it slowly, step, by step, like I do in this tutorial.


### 4.  Use Pre-Commit ([^](#table-of-contents))
In the future you will not be using `poetry run pre-commit run --all-files`, instead pre-commit will automatically on all the files that you are committing to your repo.

Here is the general workflow that will now happen:

1. You work on a feature for your website and have changed a bunch of files.
2. You run `git add --all` (doesn't have to be `--all` you could add files one by one, whatever is your preference)
3. Then, you will run `git commit -m "adding new feature"`. At that stage pre-commit starts. If all the checks have Passed, then the commit will go through and you can then run `git push`. If, on the other hand, at least one check fails commit will not go through.
4. Depending on your set up (which we will discuss later) either of the two things will happen. 
	1. pre-commit have fixed those mistakes automatically (like in the example above we saw pre-commit say that a number of files have been "fixed") 
	2. pre-commit won't fix mistakes, but will point you towards where those foxes are, so that you can fix them yourself.
5. In either case once the fixes are done, you want to re-add the fixed versions of the file with `git add --all` and re-try running the  `git commit -m "adding new feature"`. This time, if all things have been fixed the commit will go through.

I know that this can sound a little tedious or slow. But once you go through this a couple of times, you will realize how quick, easy and useful this is.

## Good Hooks to Use ([^](#table-of-contents))

Now that the setup is done, let go through some of my favorite hooks that I use in almost all my projects. The first three you have already seen, I do use them everywhere.

### Black ([^](#table-of-contents))

[Black](https://github.com/psf/black) is a Python code formatter. This means that when this hook will run, all the files that you want to commit will be checked for any inconsistencies and bad styling ([based on PEP 8 standard](https://pep8.org)). This hook will automatically fix those issues.

Before we add this hook, let's do something first. Add `exclude: ^migrations/` to the top of your `pre-commit` config file. So that it will look like this:

```yaml
# .pre-commit-config.yaml
exclude: .*migrations\/.*
repos:
-   repo: 
...
```

This will make sure that the files that Django migration generates are not touched. You don't have to do that. I, personally, I think it makes sense not to touch files that are autogenerated by Django.

Alright, now that this is out of the way, let's add `black` to pre-commit. All you have to do is add the following lines to the pre-commit config file, right after the first "repo":

```yaml
exclude: .*migrations\/.*
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
...
- repo: https://github.com/psf/black
  rev: 22.12.0
  hooks:
  - id: black
    language_version: python3.9
```

Keep in mind that at the time that you are reading, `black` might have a newer version available. You should go to [the repo](https://github.com/psf/black) and check the latest available version (just like described above).

Another thing to keep in mind is that you should change the language version depending on what you are targeting. For example, when setting up the `basic-django` repo we specified that this project will be version 3.9.

!!! note "Optional"
    If you are using poetry in your project, like I described in [a previous post](https://builtwithdjango.com/blog/basic-django-setup) you can also add another layer of configuration. In you `pyproject.toml` file you can add the following block:

```toml
[tool.black]
line-length = 120
target-version = ['py39']
include = '\.pyi?$'
```

!!! note "Optional, continued"
    Black will you these configurations when being ran by pre-commit. To see the full list of available configurations, check out [the official docs page](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html).

Once you've added it, you can test by running `poetry run pre-commit run --all-files`.

You should see something like this:
![result of running black with pre-commit](https://res.cloudinary.com/built-with-django/image/upload/v1680283107/blog-images/result_of_running_black_with_pre-commit_olm6h1.png)

If you do, congratulations!!! 8 files were formatted to adhere to the PEP-8 standard 🤘

If something went wrong, please comment below, I'll take a look ASAP.

We can move on to other hooks.

### isort ([^](#table-of-contents))

[isort](https://github.com/pycqa/isort) is an awesome tool that will sort imports across your repo.

You know the drill. Let's add this hook to the pre-commit config file. It will look like so:

```yaml
repos:
... pre-commmit stuff
... black stuff
 - repo: https://github.com/pycqa/isort 
   rev: 5.12.0 
   hooks: 
     - id: isort 
       name: isort (python)
```

And optionally, but very much recommended add these configurations to the `pyproject.toml` file:
```toml
[tool.isort]
profile = "django"
combine_as_imports = true
include_trailing_comma = true
line_length = 120
```
Let's go over at what these do.
1. isort has [profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html), which let you choose what type of repo you have. This will slightly change the behaviour of the check.
2. The next too are something that isort recommends for the django profile. `combine_as_imports` will that imports with `as` statement are combined and the `include_trailing_comma` will keep the comma after the last import in a statement that imports multiple items.
3. Next is the line length, which is **important**. I ran into this problem a few times. Make sure that this number is the same as the one configure in black. If that is not the case, often times, these two will conflict with each other, correcting each others behavior.

Let's try running pre-commit again with `poetry run pre-commit run --all-files`. You should see something like this:
![running pre-commit after adding isort](https://res.cloudinary.com/built-with-django/image/upload/v1680283168/blog-images/running_pre-commit_after_adding_isort_202303270922_k39dhy.png)

Please note,that black passed the test, since we habe already run it before, which is cool. Also, interesting to see the `fix end of files` hook being triggered. Probably I added extra line in the pre-commit config file. Finally I can see that 2 files have been fixed by `isort`, awesome. 

Let's move on!

### flake8 ([^](#table-of-contents))

flake8 is yet another awesome tool that will help you check the style and quality of some python code.

This one is going to be a liiiitle bit different. Instead configuring the behaviour in the pyproject.toml file like before we will create a separate file for it. 

But first, let's add to the pre-commit file first. As before check the latest version that is available in the github repo.

```yaml
...
- repo: https://github.com/pycqa/flake8
  rev: 6.0.0
  hooks:
    - id: flake8
```

Note create a `.flake8` file at the root of your repository and add the following to it:
```
[flake8]
max-line-length=120
```

Now, let's try running it with `poetry run pre-commit run --all-files`. Here is what I got:
![running pre-commit with flake8](https://res.cloudinary.com/built-with-django/image/upload/v1680283220/blog-images/running_pre-commit_with_flake8_jmigjv.png)

Awesome. Couple of things to note. 

First, I did not talk about this before, but you can see in the first lines where `pre-commit` is setting up the environment for flake8 (essentially checking if the hooks exist). If something went wrong at this stage, then it is likely that you entered url incorrect or that you added a non-existent version.

Second, is that this plugin doesn't update the file for us. It just tells us what is currently wrong so that I can go and fix it myself before committing the new code, which is fantastic. Let's do exactly that.

First, it doesn't like that the HTML string in the `utils.py` file is too long. Black did not make it smaller, because it doesn't know how to operate on strings. There are two approaches we can take:
1. Fix the line length by breaking up the svg code into multiple lines.
2. Tell flake that this exact case is fine.

I'm going to opt for #2, since I don't care about the readability of the svg tag (no one actually "inspects" those). Plus, would be good to show how to tell packages to ignore some lines.

I'm going to put the following comment `# noqa: E501` on lines 16 and 17. The `E501` comes from the message in the terminal. Same for the lines, flake8 tells me which lines are affected. After adding this comment to both lines, let's rerun the `pre-commit` command.

![flake8  noqa](https://res.cloudinary.com/built-with-django/image/upload/v1680283255/blog-images/flake8_noqa_og3kfh.png)

Et Voila! This specific message is gone. Now let's fix others. Looks like it is about unused imports. That should be easy to fix. Let's remove those import and rerun.

![flake8 passed](https://res.cloudinary.com/built-with-django/image/upload/v1680283283/blog-images/flake8_passed_l7fm3h.png)

Hooray! Let's move on to pylint.

### pylint ([^](#table-of-contents))

pylint is a linter and a static code analyzer just like flake8. It will check your code for any formatting issue as well as any performance issues. The difference is that pylint is a little more thorough and more customizable.

I feel like those two complement each other. You don't have to set both of them up, but I sleep better when I know that two unrelated programs checked my code 🤣

Set up for pylint is a little different. Here is a quote from the [official docs](https://pylint.readthedocs.io/en/latest/user_guide/installation/pre-commit-integration.html):
> Since `pylint` needs to import modules and dependencies to work correctly, the hook only works with a local installation of `pylint` (in your environment).

So, we need to install pylint into our repo with `poetry add --group dev pylint`. 

Once `pylint` was installed we will need to tell `pre-commit` to use that specific version. Again, let's check the [docs for that](https://pylint.readthedocs.io/en/latest/user_guide/installation/pre-commit-integration.html). They recommend we do it that way (I removed a couple of args):

```yaml
...
- repo: local
  hooks:
    - id: pylint
      name: pylint
      entry: poetry run pylint
      language: system
      types: [python]
      args:
        [
          "-rn", # Only display messages
          "-sn", # Don't display the score
        ]
```

Note the change I made on the `entry` line. Instead of running `pylint`, we are telling `pre-commit` to run `poetry run pylint`, since that is the preferred way to invoke packages installed with poetry.

One last thing to do before running the hooks is to create a config file, just like we did with `flake8`. For this you are going to create a `pylintrc` file at the roor of your project and copy the contents of the `pylintrc` file from the `pylint` repo ([here is the link to it](https://github.com/pylint-dev/pylint/blob/main/pylintrc)).

These are the recommended setting for pylint that we can configure in the future if we want.

Let's run `poetry run pre-commit run --all-files` to see what happens.

Here is what I got.
![first pylint errors](https://res.cloudinary.com/built-with-django/image/upload/v1680283319/blog-images/first_pylint_errors_202303290836_xhgnvg.png)

Good, that means it's working. Before going further, I would like to show you another cool feature of pylint. Extensions.

There is a Django extension that we can install and apply to the pylint check. Let's do that.

Install with `poetry add --group dev pylint-django`.  And add the 2 new lines to the args list, like so:
```yaml
...
      args:
        [
          "-rn",
          "-sn",
          "--load-plugins=pylint_django", # new
          "--django-settings-module={NAME OF YOUR REPO}.settings", # new
        ]
```


Let's run `poetry run pre-commit run --all-files` once again, to make sure everything is working correctly.

Looks like pylint found the same 3 errors. I'm not going to go over them one by one, since they are very detailed, and more importantly, you might be seeing something else.

The only note I'll make is that I will add
```
--ignore=manage.py
```
to the list of args, since this was generated by Django, and I don't want to lint that.

So, let's use the magic of reading and see what it looks like after I modified the code to the pylint's liking.

![pylint success](https://res.cloudinary.com/built-with-django/image/upload/v1680283358/blog-images/pylint_success_202303290853_nqfzte.png)

Nice. Another useful check added to the list.

I will tell you this... In my opinion, pylint is the hardest and the most annoying to setup and "please" in the future. However, it doesn't mean that you should do it. I think all (most) the error messages that it is showing are useful.

If you encounter those error, at setup or at commit don't worry. Spend some time trying to fix them, or googling about them. This will make you a better dev for sure.

Comment below, if something is not working for you. I'll try to help. 

### djlint ([^](#table-of-contents))

For Django users, which you presumably are, this will be a God send! Check out [the repo](https://github.com/Riverside-Healthcare/djLint). This is an HTML linter... but for Django templates 🤯

It will look for errors and inconsistencies in your HTML files. The setup for this one is straightforward.

Add this to the pre-commit-config file:
```yaml
- repo: https://github.com/Riverside-Healthcare/djLint
  rev: v1.19.16
  hooks:
    - id: djlint-django
```

Also, I will add the following conf to the `pyproject.toml` file:
```toml
[tool.djlint]
profile="django"
```

For all the conf options, check out the [official docs](https://djlint.com/docs/configuration/)

One thing to note is that I would recommend you put this "repo", before the "local" one. It is preferable to keep the "local" one last. So, in our case we would add this one right after `flake8` one.

And, as before make sure you are using the latest version. Let's give this a run with `poetry run pre-commit run --all-files`.

![djlint first run](https://res.cloudinary.com/built-with-django/image/upload/v1680283396/blog-images/djlint_first_run_202303290901_davtxp.png)

Oof, there is a lot to fix. Thankfully, errors are pretty clear.

I've included the following ignores to my conf file:
```toml
[tool.djlint]
profile="django"
ignore = "H031"
```

Added H031 because keywords meta is no longer used. Everything else, fixed.

![fixed djlint](https://res.cloudinary.com/built-with-django/image/upload/v1680283421/blog-images/fixed_djlint_202303290915_we4usw.png)


### poetry export ([^](#table-of-contents))

Final one that I like to use is the `poetry export` hook. It used to be the case that we needed to add this one to the local repo, but no longer.

This is useful if you don't want to install poetry on your prod server or in your Dockerfile. That is to say very useful.

Instead of dealing with poetry in Docker or prod we will just have a nice and fresh "requirements.txt" file to use for out dependencies. Beautiful.

To make this work add the following to your pre-commit config file. I put it right after the djlint hook.

```yaml
- repo: https://github.com/python-poetry/poetry
  rev: '1.4.1'
  hooks:
    - id: poetry-export
      args: [
        "-f", "requirements.txt",
        "-o", "requirements.txt",
        "--without-hashes"
      ]
```

This one doesn't require any configurations ♥️. To see other poetry hooks, check out [their docs](https://python-poetry.org/docs/master/pre-commit-hooks/).

![final check passed](https://res.cloudinary.com/built-with-django/image/upload/v1680283450/blog-images/final_check_passed_202303290926_vp7la1.png)

### ruff ([^](#table-of-contents))

A kind reddit user by the name of [lanemik](https://www.reddit.com/user/lanemik/) suggested I give [ruff](https://github.com/charliermarsh/ruff) a go. I have heard of this tool before, but never actually gave it a go.

According to the README

> Ruff can be used to replace [Flake8](https://pypi.org/project/flake8/) (plus dozens of plugins), [isort](https://pypi.org/project/isort/), [pydocstyle](https://pypi.org/project/pydocstyle/), [yesqa](https://github.com/asottile/yesqa), [eradicate](https://pypi.org/project/eradicate/), [pyupgrade](https://pypi.org/project/pyupgrade/), and [autoflake](https://pypi.org/project/autoflake/), all while executing tens or hundreds of times faster than any individual tool.

I'm not going to replace isort and Flake8 for the purpose of this tutorial, but I will add ruff above those two to see it's performance.

Let's add the following block to the pre-commit config file:

```yaml
- repo: https://github.com/charliermarsh/ruff-pre-commit
  rev: 'v0.0.260'
  hooks:
    - id: ruff
```

I will also add the following configuration to the `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120
```

, but there are a ton of other things you can configure. Check out the README for that.

Now, let's run the `poetry run pre-commit run --all-files` and see what happens. 

I got the same error as in the flake8 about the long HTML lines in the utils.py. The syntax for ignoring error is the same as in Flake8. The only difference is that here I had to add "# noqa: E501" at the end of a multi-line string, as opposed to the end the line. Once added at the end of the string I can remove `noqa` comments on lines 16 & 17. I personally think that looks nicer. 

That's it. As easy as that.

## Conclusion ([^](#table-of-contents))
 
Aaaah, it's hard to explain the joy I get from seeing all those "Passed" messages.

- First of all, green is a nice color to look at.
- Second, I get to sleep knowing that my code quality is safe 👍 which is useful both for team and individual projects.

In conclusion, here is what we did:
- Install pre-commit as a dev dependency in you poetry project.
- Installed a bunch of pre-commit hooks to the pre-commit config file.
- Configured the behavior of new hooks through `pyproject.toml` configurations or through rc file configurations.

Can't believe it took more than 3000 words to go over these 3 bullet points 🤷‍♂️. If you made it to here, a salute you 🖖, you are an incredible human being with a ton of patience and focus! You will do good in life.

If you have any questions or comments, please them leave below.