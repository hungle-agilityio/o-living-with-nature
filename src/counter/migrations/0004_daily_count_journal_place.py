from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("counter", "0003_daily_count_message_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dailycount",
            name="place",
            field=models.CharField(
                blank=True,
                choices=[
                    ("bar", "Phone bar"),
                    ("rent", "Rent chapter"),
                    ("faq", "FAQ chapter"),
                    ("contact", "Contact chapter"),
                    ("journal", "Journal notes"),
                ],
                max_length=7,
            ),
        ),
    ]
