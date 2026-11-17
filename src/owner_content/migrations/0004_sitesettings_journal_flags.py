"""Two flags that say whether a published journal note exists (journal spec, issue #136)."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("owner_content", "0003_sitesettings_reply_time_vi")]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="journal_en",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="journal_vi",
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
