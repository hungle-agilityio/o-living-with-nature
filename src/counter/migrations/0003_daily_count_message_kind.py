from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("counter", "0002_daily_count_faq_place"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dailycount",
            name="kind",
            field=models.CharField(
                choices=[("view", "View"), ("click", "Click"), ("message", "Message")],
                max_length=7,
            ),
        ),
    ]
