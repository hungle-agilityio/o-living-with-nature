from django.urls import path

from pages import views

# The home page: `/` in English and `/vi/` in Vietnamese (config/urls.py wraps it in i18n_patterns).
home_urlpatterns = [
    path("", views.home, name="home"),
]

# The rest has one address only, with no `/vi/` version.
urlpatterns = [
    # The old page addresses of epic 1, each sent to its chapter of the one page.
    path("house/", views.chapter, {"chapter_id": "house"}, name="house"),
    path("hoa-xuan/", views.chapter, {"chapter_id": "hoa-xuan"}, name="hoa_xuan"),
    path("faq/", views.chapter, {"chapter_id": "faq"}, name="faq"),
    path("contact/", views.chapter, {"chapter_id": "contact"}, name="contact"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("robots.txt", views.robots, name="robots"),
    path("healthz/", views.health, name="health"),
]
