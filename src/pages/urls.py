from django.urls import path

from pages import views

urlpatterns = [
    path("", views.home, name="home"),
    path("house/", views.house, name="house"),
    path("hoa-xuan/", views.hoa_xuan, name="hoa_xuan"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("robots.txt", views.robots, name="robots"),
    path("healthz/", views.health, name="health"),
]
