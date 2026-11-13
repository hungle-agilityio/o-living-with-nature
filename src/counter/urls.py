from django.urls import path

from counter import views

app_name = "counter"

urlpatterns = [
    path("count/", views.count, name="count"),
]
