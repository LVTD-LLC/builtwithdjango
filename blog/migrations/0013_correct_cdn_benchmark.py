"""Replace an unsupported benchmark with deployment guidance, without rewriting other copy."""

import hashlib

from django.db import migrations
from django.utils import timezone

POST_ID = 152
SLUG = "5-hidden-django-secrets-senior-developers-use-lightning-fast-code"
OLD_TEXT = "A 2025 study found that Django applications serving assets via CDN with Brotli compression achieved a 40% improvement in first contentful paint (FCP) metrics compared to non-optimized setups [Built with Django](https://builtwithdjango.com/blog/django-cdn-performance-study)."
NEW_TEXT = "Django’s deployment documentation describes serving collected static files from dedicated servers, cloud storage, or a CDN. Use these deployment patterns where they fit your application, and measure FCP before and after changing asset delivery; the documentation does not promise a fixed percentage improvement. See [Django’s static-file deployment guide](https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/)."
OLD_SHA256 = "5c7b44831ac578c4fcae8697470f4afcff6881417a53a5e8cd20c2715ddbdba8"
NEW_SHA256 = "01e6ad1fe70c86a0214e6a94b24bd712d8a043cc5984db54a67d514e1313dee7"


def replace_claim(apps, schema_editor, before, after, expected_hash, resulting_hash):
    Post = apps.get_model("blog", "Post")
    posts = Post.objects.using(schema_editor.connection.alias)
    post = posts.select_for_update().filter(pk=POST_ID).first()
    # Fresh installs and databases without the production article need no data edit.
    if post is None:
        return
    if post.slug != SLUG:
        raise RuntimeError("CDN correction target does not match; reconcile before deploying.")
    digest = hashlib.sha256(post.content.encode()).hexdigest()
    if digest == resulting_hash:
        return
    if digest != expected_hash or post.content.count(before) != 1:
        raise RuntimeError("Article changed since CDN correction was prepared; reconcile before deploying.")
    content = post.content.replace(before, after, 1)
    changed = posts.filter(pk=post.pk, content=post.content).update(content=content, modified=timezone.now())
    if changed != 1:
        raise RuntimeError("Article changed during CDN correction; no content was overwritten.")


def forwards(apps, schema_editor):
    replace_claim(apps, schema_editor, OLD_TEXT, NEW_TEXT, OLD_SHA256, NEW_SHA256)


def backwards(apps, schema_editor):
    replace_claim(apps, schema_editor, NEW_TEXT, OLD_TEXT, NEW_SHA256, OLD_SHA256)


class Migration(migrations.Migration):
    dependencies = [("blog", "0012_alter_post_type")]
    operations = [migrations.RunPython(forwards, backwards)]
