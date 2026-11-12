from django.apps import AppConfig


class OwnerContentConfig(AppConfig):
    name = "owner_content"
    label = "owner_content"
    verbose_name = "Owner content"

    def ready(self) -> None:
        # Importing the module registers its system check.
        from owner_content import checks  # noqa: F401
