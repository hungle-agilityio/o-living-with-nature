"""Create the one record of site settings with the owner's values (docs/intent/website.md)."""

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

OWNER_NUMBER = "0945 384 500"


def create_owner_values(apps: Apps, schema_editor: BaseDatabaseSchemaEditor | None) -> None:
    site_settings = apps.get_model("owner_content", "SiteSettings")
    if site_settings.objects.exists():
        return  # the owner's record is left as it is
    site_settings.objects.create(
        price_from_million=13,
        price_to_million=14,
        phone=OWNER_NUMBER,
        whatsapp=OWNER_NUMBER,
        zalo=OWNER_NUMBER,
        owner_first_name="Bún",
        reply_time="within an hour",
    )


class Migration(migrations.Migration):
    dependencies = [("owner_content", "0001_initial")]

    operations = [migrations.RunPython(create_owner_values, migrations.RunPython.noop)]
