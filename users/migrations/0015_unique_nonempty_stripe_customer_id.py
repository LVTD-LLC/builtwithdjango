from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0014_customuser_stripe_customer_id"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="customuser",
            constraint=models.UniqueConstraint(
                condition=models.Q(("stripe_customer_id", ""), _negated=True),
                fields=("stripe_customer_id",),
                name="unique_nonempty_stripe_customer_id",
            ),
        ),
    ]
