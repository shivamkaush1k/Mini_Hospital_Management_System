from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contacts, name="contacts"),

    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),

    path("users/", views.users, name="users"),
    path("users/<uuid:pk>/delete/", views.delete_user, name="delete_user"),
]