"""The owner's enquiries inbox in the admin: read the messages, mark them replied or new."""

from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.defaultfilters import linebreaksbr
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import SafeString

from enquiries.inbox import (
    deleted_on,
    is_email,
    move_in_long,
    move_in_short,
    page_language,
    received,
    stay_label,
)
from enquiries.models import Enquiry, Status
from enquiries.services import delete_expired

if TYPE_CHECKING:
    EnquiryAdminBase = admin.ModelAdmin[Enquiry]
    EnquiryFormBase = forms.ModelForm[Enquiry]
else:  # ModelAdmin and ModelForm take their model type only for the type checker
    EnquiryAdminBase = admin.ModelAdmin
    EnquiryFormBase = forms.ModelForm


class EnquiryStatusForm(EnquiryFormBase):
    """Only the status can be edited; the label has no colon, as the read-only rows."""

    class Meta:
        model = Enquiry
        fields = ["status"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)


def _sensitive(value: str) -> SafeString:
    return format_html("<span data-sensitive>{}</span>", value)


@admin.register(Enquiry)
class EnquiryAdmin(EnquiryAdminBase):
    form = EnquiryStatusForm
    ordering = ["-created_at"]
    list_per_page = 100
    list_display = [
        "received_cell",
        "name_cell",
        "reply_to_cell",
        "move_in_cell",
        "stay_cell",
        "status_cell",
    ]
    list_display_links = ["received_cell"]
    list_filter = [("status", admin.ChoicesFieldListFilter)]
    show_facets = admin.ShowFacets.ALWAYS
    actions = ["mark_replied", "mark_new"]
    fields = [
        "received_row",
        "name_row",
        "reply_to_row",
        "move_in_row",
        "stay_row",
        "message_row",
        "deleted_on_row",
        "status",
    ]
    readonly_fields = [
        "received_row",
        "name_row",
        "reply_to_row",
        "move_in_row",
        "stay_row",
        "message_row",
        "deleted_on_row",
    ]

    # The list

    @admin.display(description="Received")
    def received_cell(self, obj: Enquiry) -> str:
        return received(obj.created_at)

    @admin.display(description="Name")
    def name_cell(self, obj: Enquiry) -> SafeString:
        return _sensitive(obj.name)

    @admin.display(description="Reply to")
    def reply_to_cell(self, obj: Enquiry) -> SafeString:
        return _sensitive(obj.reply_to)

    @admin.display(description="Move in")
    def move_in_cell(self, obj: Enquiry) -> str:
        return move_in_short(obj.move_in)

    @admin.display(description="Stay")
    def stay_cell(self, obj: Enquiry) -> str:
        return stay_label(obj.stay)

    @admin.display(description="Status")
    def status_cell(self, obj: Enquiry) -> SafeString:
        return format_html(
            '<span class="enq-badge enq-badge--{}">{}</span>',
            obj.status,
            obj.get_status_display(),
        )

    # The change page

    @admin.display(description="Received")
    def received_row(self, obj: Enquiry) -> str:
        return f"{received(obj.created_at)} ({page_language(obj.language)})"

    @admin.display(description="Name")
    def name_row(self, obj: Enquiry) -> SafeString:
        return _sensitive(obj.name)

    @admin.display(description="Reply to")
    def reply_to_row(self, obj: Enquiry) -> SafeString:
        if is_email(obj.reply_to):
            return format_html(
                '<span data-sensitive><a href="mailto:{}">{}</a></span>',
                obj.reply_to,
                obj.reply_to,
            )
        return _sensitive(obj.reply_to)

    @admin.display(description="Move in")
    def move_in_row(self, obj: Enquiry) -> str:
        return move_in_long(obj.move_in)

    @admin.display(description="Stay")
    def stay_row(self, obj: Enquiry) -> str:
        return stay_label(obj.stay)

    @admin.display(description="Message")
    def message_row(self, obj: Enquiry) -> SafeString:
        return format_html(
            '<div class="enq-msg" data-sensitive>{}</div>',
            linebreaksbr(obj.message, autoescape=True),
        )

    @admin.display(description="Deleted on")
    def deleted_on_row(self, obj: Enquiry) -> str:
        return deleted_on(obj.created_at)

    # Actions

    @admin.action(description="Mark as replied", permissions=["change"])
    def mark_replied(self, request: HttpRequest, queryset: QuerySet[Enquiry]) -> None:
        queryset.update(status=Status.REPLIED)

    @admin.action(description="Mark as new", permissions=["change"])
    def mark_new(self, request: HttpRequest, queryset: QuerySet[Enquiry]) -> None:
        queryset.update(status=Status.NEW)

    # Permissions and views

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        delete_expired(timezone.now())
        return super().changelist_view(request, {**(extra_context or {}), "title": "Enquiries"})

    def render_change_form(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        add: bool = False,
        change: bool = True,
        form_url: str = "",
        obj: Enquiry | None = None,
    ) -> HttpResponse:
        if obj is not None:
            context.update(
                {
                    "title": f"Enquiry from {obj.name}",
                    "subtitle": None,
                    "show_save_and_continue": False,
                }
            )
        return super().render_change_form(request, context, add, change, form_url, obj)
