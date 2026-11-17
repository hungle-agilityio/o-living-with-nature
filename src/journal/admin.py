"""The owner's admin for journal notes."""

from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib import admin
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse

from journal.models import COVER_CHOICES, JournalPost
from journal.services import refresh_flags

if TYPE_CHECKING:
    JournalPostAdminBase = admin.ModelAdmin[JournalPost]
    JournalPostFormBase = forms.ModelForm[JournalPost]
else:  # ModelAdmin and ModelForm take their model type only for the type checker
    JournalPostAdminBase = admin.ModelAdmin
    JournalPostFormBase = forms.ModelForm


class JournalPostForm(JournalPostFormBase):
    """The cover select starts with "No cover", then the site's photos."""

    class Meta:
        model = JournalPost
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["cover"].choices = [("", "— No cover —"), *COVER_CHOICES]  # type: ignore[attr-defined]


@admin.register(JournalPost)
class JournalPostAdmin(JournalPostAdminBase):
    form = JournalPostForm
    list_display = ["title", "date", "status", "vietnamese", "cover_photo"]
    list_filter = ["status"]
    search_fields = ["title"]
    ordering = ["-date", "-pk"]
    list_per_page = 100
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = [
        ("English (required)", {"fields": ["title", "slug", "summary", "body"]}),
        ("Tiếng Việt (optional)", {"fields": ["title_vi", "summary_vi", "body_vi"]}),
        ("Publishing", {"fields": ["cover", "date", "status"]}),
    ]

    @admin.display(description="Vietnamese")
    def vietnamese(self, obj: JournalPost) -> str:
        return "Yes" if obj.has_vietnamese else "No"

    @admin.display(description="Cover photo")
    def cover_photo(self, obj: JournalPost) -> str:
        return obj.get_cover_display() if obj.cover else "—"

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        context = {**(extra_context or {}), "title": "Journal posts"}
        return super().changelist_view(request, extra_context=context)

    def save_model(self, request: HttpRequest, obj: JournalPost, form: Any, change: bool) -> None:
        super().save_model(request, obj, form, change)
        refresh_flags()

    def delete_model(self, request: HttpRequest, obj: JournalPost) -> None:
        super().delete_model(request, obj)
        refresh_flags()

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[JournalPost]) -> None:
        with transaction.atomic():  # the bulk delete action is not atomic by itself
            super().delete_queryset(request, queryset)
            refresh_flags()
