import uuid
from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
  

    path("", views.notification_list, name="list"),

    path(
        "<uuid:pk>/",
        views.mark_read,
        name="read",
    ),

]