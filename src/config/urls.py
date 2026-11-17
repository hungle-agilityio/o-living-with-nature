from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

from enquiries.urls import enquiry_urlpatterns
from pages.urls import home_urlpatterns

# The owner's admin: Django's own, at /owner/ (there is no /admin/).
admin.site.site_header = "Ở admin"
admin.site.site_title = "Ở admin"
admin.site.index_title = "Site administration"

urlpatterns: list[URLPattern | URLResolver] = [
    path("owner/", admin.site.urls),
    path("", include("counter.urls")),
    path("", include("pages.urls")),
]

# The home page and the enquiry address have two languages: `/` and `/enquiry/` are English,
# `/vi/` and `/vi/enquiry/` Vietnamese.
urlpatterns += i18n_patterns(*home_urlpatterns, *enquiry_urlpatterns, prefix_default_language=False)
