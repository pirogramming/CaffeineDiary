# accounts/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    # 화면 (GET, 슬래시 없음)
    path("login", views.LoginPageView.as_view(), name="login-page"),
    path("signup", views.SignupPageView.as_view(), name="signup-page"),

    path("signup/", views.signup, name="signup"),

    path("login/", views.login, name="login"),

    path("logout/", views.logout, name="logout"),

    path("session/", views.session, name="session"),  # GET /auth/session

]