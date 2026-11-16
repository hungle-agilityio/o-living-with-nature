from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("counter", "0001_initial"),
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
                ],
                max_length=7,
            ),
        ),
    ]
