from django.urls import path

from enquiries import views

# `/enquiry/` in English and `/vi/enquiry/` in Vietnamese (in i18n_patterns, config/urls.py).
enquiry_urlpatterns = [
    path("enquiry/", views.enquiry, name="enquiry"),
]
