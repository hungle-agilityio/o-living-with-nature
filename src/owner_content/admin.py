"""The owner's admin for the one record of site settings."""

from typing import TYPE_CHECKING

from django.contrib import admin
from django.http import HttpRequest

from owner_content.models import SiteSettings

if TYPE_CHECKING:
    SiteSettingsAdminBase = admin.ModelAdmin[SiteSettings]
else:  # ModelAdmin takes its model type only for the type checker
    SiteSettingsAdminBase = admin.ModelAdmin


@admin.register(SiteSettings)
class SiteSettingsAdmin(SiteSettingsAdminBase):
    def has_add_permission(self, request: HttpRequest) -> bool:
        # One record only: "Add" is offered while there is none.
        return super().has_add_permission(request) and not SiteSettings.objects.exists()

    def has_delete_permission(self, request: HttpRequest, obj: SiteSettings | None = None) -> bool:
        return False
