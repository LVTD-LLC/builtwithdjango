---
id: 3
created: '2022-04-27 01:51:55.365000+00:00'
modified: '2026-11-01 08:50:00+00:00'
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
Keep your Django code, migrations and dependency lockfiles in Git. Keep local credentials, databases and uploads out. Before the first commit, check what Git has actually staged: a `.gitignore` file only affects untracked files, not files already in the index or earlier commits.

This walkthrough continues the [basic Django setup](/blog/basic-django-setup). It uses local Git commands; you need a GitHub account only for the final push. The ignore and staging checks were reproduced with disposable files on Linux in November 2026, not against a production repository.

## Why?

A repository should let another developer recreate your application without copying your laptop's secrets or database. Commit application code, templates, tests and migration files together. Commit `pyproject.toml` and `poetry.lock` for the Poetry setup used in this series; if you use npm, keep `package.json` and `package-lock.json` too.

[Django's migration documentation](https://docs.djangoproject.com/en/5.2/topics/migrations/) explicitly treats migration files as part of the codebase. Do not ignore the whole `migrations/` directory. Your local SQLite database is different: it can contain account data and should not become a shared development fixture by accident.

Ignoring a file is not encryption or access control. Move real credentials out of tracked settings before staging; see the [environment-variable walkthrough](/blog/env-vars) for the Django configuration step. A generated development `SECRET_KEY` in `settings.py` is still tracked code unless you change that configuration. Do not use an example or publicly committed key in production.

## Beginning of History

From your project root, initialize Git if this is a new, unversioned project:

```bash
git init
git status --short
```

For an existing repository, skip initialization and inspect its current state. Do not reset or replace someone else's history. Git works without GitHub; creating a remote repository comes after the local checks below.

## Ignoring secrets

Create `.gitignore` at the project root before adding files. This is a starting point for a typical local Django project, not a list of every possible credential filename:

```gitignore
# Local credentials; keep only a harmless template
.env
.env.*
!.env.example

# Local Python environment and caches
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/

# Local databases, including SQLite sidecar files
*.sqlite3
*.sqlite3-journal
*.sqlite3-wal
*.sqlite3-shm

# Dependencies, uploaded files and collected static output
node_modules/
/media/
/staticfiles/
```

Use `.env.example` for variable names and dummy values only. The exception above deliberately allows it into Git, so it must never contain a working credential. The `/staticfiles/` rule assumes that is your `STATIC_ROOT`; change it to your actual generated-output directory. Keep source static assets under version control. Do not ignore a directory that mixes source files with generated output.

These are Git ignore patterns, not regular expressions. `*` matches within a path component, a trailing `/` selects directories, and `!` makes an exception. See the [Git ignore reference](https://git-scm.com/docs/gitignore) for precedence and nested rules.

### Check the rules before staging

Once a local `.env` exists, ask Git which rule matches it:

```bash
git check-ignore -v .env
```

For an untracked `.env`, expect a matching rule and filename, not the file's contents. No output can mean the file is already tracked or no ignore rule applies. Check tracking separately:

```bash
git ls-files -- .env
```

A printed `.env` path means it is already in Git's index. Adding an ignore rule will not untrack it. The same applies to nested files: substitute their actual paths, such as `config/.env`.

### If a file is already tracked

First inspect `git status` and preserve any local work. To stop tracking an existing `.env` while keeping its local contents, use this path-specific command, then review the staged change:

```bash
git rm --cached -- .env
git diff --cached --name-status
```

Do not add `--force` to silence a refusal: Git may be protecting differences between the staged file, working copy and last commit. Resolve those differences deliberately. Avoid a blanket index removal when only one file needs attention.

This removes the path from the next committed snapshot; it does **not** erase older commits, copies or logs. If a real credential was committed, revoke or rotate it first. Then assess cleanup with collaborators using [GitHub's sensitive-data guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository). Deleting a file or making a repository private is not a substitute for rotation. Do not rewrite shared history as a casual follow-up command.

## Final Steps

Only after you have checked your ignore rules and removed credentials from tracked code, stage the project:

```bash
git add --all
git status --short
git diff --cached --name-only
git diff --cached
```

Review both the filenames and the diff locally before committing. `git add --all` also stages modifications to already-tracked files, even if a new ignore rule matches them. It does not scan for secrets. Do not paste a potentially sensitive diff into a public issue or chat.

Confirm that your intended source, migrations and lockfiles are present. Confirm that local credentials, database files and uploads are absent. If the review reveals a secret, stop and fix the staged state before continuing.

For a new repository, make the initial commit once that review is complete:

```bash
git commit -m "Initial Django project"
git branch -M main
```

Create an **empty** repository on [GitHub](https://github.com/new), without an initial README, license or `.gitignore`, so its history does not conflict with this first local commit. Choose public or private deliberately; both need the same credential checks.

Use the actual remote URL GitHub provides. For example, replace `YOUR_USERNAME` and `YOUR_REPOSITORY` in the SSH form below; SSH authentication must already be configured. GitHub also offers HTTPS URLs:

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If `origin` already exists or the remote already has commits, inspect it rather than force-pushing over it. This new-repository sequence is not a recipe for replacing an existing team's project.

## Conclusion

You now have a reviewable first Django commit, not just an ignore file. Next, follow the [environment-variable setup](/blog/env-vars) to wire local configuration into Django, and use the [pre-commit guide](/blog/improve-your-code-with-pre-commit) for repeatable checks. Hooks are useful safeguards, but they do not replace inspecting what you commit.
