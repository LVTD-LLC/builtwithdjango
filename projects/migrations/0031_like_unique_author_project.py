from django.db import migrations, models


def dedupe_likes(apps, schema_editor):
    Like = apps.get_model("projects", "Like")
    duplicate_groups = (
        Like.objects.values("author_id", "project_id").annotate(count=models.Count("id")).filter(count__gt=1)
    )

    for group in duplicate_groups:
        likes = list(
            Like.objects.filter(author_id=group["author_id"], project_id=group["project_id"]).order_by(
                "-like",
                "-modified",
                "-id",
            )
        )
        Like.objects.filter(id__in=[like.id for like in likes[1:]]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0030_remove_project_audience_analysis_and_more"),
    ]

    operations = [
        migrations.RunPython(dedupe_likes, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="like",
            constraint=models.UniqueConstraint(
                fields=("author", "project"),
                name="unique_like_per_author_project",
            ),
        ),
    ]
