from django.urls import path

from journal import views

# The journal: `/journal/` in English and `/vi/journal/` in Vietnamese (config/urls.py wraps it
# in i18n_patterns).
journal_urlpatterns = [
    path("journal/", views.journal_list, name="journal"),
    path("journal/<slug:slug>/", views.journal_note, name="journal_note"),
]
