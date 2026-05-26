from django.conf import settings
from django.db import migrations, models


def copy_djstripe_customer_ids(apps, schema_editor):
    user_model = apps.get_model("users", "CustomUser")
    connection = schema_editor.connection

    if "djstripe_customer" not in connection.introspection.table_names():
        return

    with connection.cursor() as cursor:
        columns = {
            column.name
            for column in connection.introspection.get_table_description(cursor, "djstripe_customer")
        }
        if not {"id", "subscriber_id"}.issubset(columns):
            return

        query = """
            SELECT id, subscriber_id
              FROM djstripe_customer
             WHERE subscriber_id IS NOT NULL
        """
        params = []

        if "livemode" in columns:
            query += " AND livemode = %s"
            params.append(settings.STRIPE_LIVE_MODE)

        cursor.execute(query, params)
        rows = cursor.fetchall()

    for stripe_customer_id, user_id in rows:
        user_model.objects.filter(pk=user_id, stripe_customer_id="").update(stripe_customer_id=stripe_customer_id)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0013_customuser_has_active_django_devs_subscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="stripe_customer_id",
            field=models.CharField(blank=True, db_index=True, default="", max_length=255),
        ),
        migrations.RunPython(copy_djstripe_customer_ids, migrations.RunPython.noop),
    ]
