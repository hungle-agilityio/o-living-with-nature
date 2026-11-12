from django.urls import path

from pages import views

urlpatterns = [
    path("", views.home, name="home"),
    # The old page addresses of epic 1, each sent to its chapter of the one page.
    path("house/", views.chapter, {"chapter_id": "house"}, name="house"),
    path("hoa-xuan/", views.chapter, {"chapter_id": "hoa-xuan"}, name="hoa_xuan"),
    path("faq/", views.chapter, {"chapter_id": "faq"}, name="faq"),
    path("contact/", views.chapter, {"chapter_id": "contact"}, name="contact"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("robots.txt", views.robots, name="robots"),
    path("healthz/", views.health, name="health"),
]
