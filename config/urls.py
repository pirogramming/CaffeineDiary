"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def home(request):
    # TODO: 프론트엔드 구현 후 SPA index 서빙으로 교체
    return JsonResponse({"is_authenticated": request.user.is_authenticated})


def login_placeholder(request):
    # TODO: 프론트엔드 구현 후 로그인 페이지로 교체
    return JsonResponse({"error": request.GET.get("error")})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login', login_placeholder, name='login-placeholder'),
    path('auth/', include('accounts.urls')),
    path('auth/social/', include('allauth.urls')),
]