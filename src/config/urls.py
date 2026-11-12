from django.contrib import admin
from django.urls import include, path

# The owner's admin: Django's own, at /owner/ (there is no /admin/).
admin.site.site_header = "Ở admin"
admin.site.site_title = "Ở admin"
admin.site.index_title = "Site administration"

urlpatterns = [
    path("owner/", admin.site.urls),
    path("", include("pages.urls")),
]
