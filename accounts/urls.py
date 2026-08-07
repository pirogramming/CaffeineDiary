# accounts/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    path("signup/", views.signup, name="signup"),

    path("login/", views.login, name="login"),

    path("logout/", views.logout, name="logout"),

    path("session/", views.session, name="session"),  # GET /auth/session

]