"""The contact counts in the owner's admin: a read-only report, nothing to add, change or delete."""

from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import URLPattern, path

from counter.models import DailyCount
from counter.report import build_report

if TYPE_CHECKING:
    DailyCountAdminBase = admin.ModelAdmin[DailyCount]
else:  # ModelAdmin takes its model type only for the type checker
    DailyCountAdminBase = admin.ModelAdmin


@admin.register(DailyCount)
class DailyCountAdmin(DailyCountAdminBase):
    """Only the report page exists: the add, change, delete and history pages are not served."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        return False

    def get_urls(self) -> list[URLPattern]:
        info = (self.opts.app_label, self.opts.model_name)
        return [
            path(
                "",
                self.admin_site.admin_view(self.changelist_view),
                name="{}_{}_changelist".format(*info),
            )
        ]

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> TemplateResponse:
        if not self.has_view_permission(request):
            raise PermissionDenied
        request.current_app = self.admin_site.name
        context = {
            **(extra_context or {}),
            **self.admin_site.each_context(request),
            "opts": self.opts,
            "title": "Contact counts",
            "report": build_report(),
        }
        return TemplateResponse(request, "admin/counter/report.html", context)
