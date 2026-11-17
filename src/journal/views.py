from django import forms
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from journal import context
from owner_content.services import site_settings
from pages import language


class PageForm(forms.Form):
    """The `?page=` of the list: a whole number from 1; none means the first page."""

    page = forms.IntegerField(min_value=1, required=False)


def journal_list(request: HttpRequest) -> HttpResponse:
    """`/journal/` and `/vi/journal/`: the published notes of the language, 12 a page."""
    form = PageForm(request.GET)
    if not form.is_valid():
        raise Http404("Invalid journal page")
    number: int = form.cleaned_data["page"] or 1
    lang = language.of_request(request)
    owner = site_settings(lang)
    return render(request, "journal/list.html", context.list_context(lang, number, owner))


def journal_note(request: HttpRequest, slug: str) -> HttpResponse:
    """`/journal/<slug>/` and `/vi/journal/<slug>/`: one published note and how to get in touch."""
    lang = language.of_request(request)
    owner = site_settings(lang)
    return render(request, "journal/note.html", context.note_context(lang, slug, owner))
