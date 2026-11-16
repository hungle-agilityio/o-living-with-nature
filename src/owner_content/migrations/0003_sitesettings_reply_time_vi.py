"""Add the Vietnamese reply time the owner edits in the admin and say which page each reply time is
shown on (vietnamese spec, issue #106)."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("owner_content", "0002_owner_values")]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="reply_time_vi",
            field=models.CharField(
                default="trong vòng một giờ",
                help_text=(
                    'Shown on the Vietnamese page as "Mình thường trả lời …", '
                    'for example "trong vòng một giờ".'
                ),
                max_length=60,
                verbose_name="Usual reply time (Vietnamese)",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="reply_time",
            field=models.CharField(
                default="within an hour",
                help_text=(
                    'Shown on the English page as "I usually reply …", '
                    'for example "within an hour".'
                ),
                max_length=60,
                verbose_name="Usual reply time",
            ),
        ),
    ]
