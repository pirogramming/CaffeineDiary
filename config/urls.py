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
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from django.views.static import serve as static_serve

from django.urls import path, include
from django.views.generic import TemplateView #임시

from diary import views as diary_views # 메인 view 연결

# def home(request):
    # TODO: 프론트엔드 구현 후 SPA index 서빙으로 교체
   # return JsonResponse({"is_authenticated": request.user.is_authenticated})


def login_placeholder(request):
    # TODO: 프론트엔드 구현 후 로그인 페이지로 교체
    return JsonResponse({"error": request.GET.get("error")})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', diary_views.MainView.as_view(), name='home'), # 메인 view 연결
    path('login', login_placeholder, name='login-placeholder'),
    path('auth/', include('accounts.urls')),
    path('auth/social/', include('allauth.urls')),
    path('mypage/', TemplateView.as_view(template_name='mypage.html'), name='mypage'),
    path('allnight_mode/', TemplateView.as_view(template_name='allnight_mode.html'), name='allnight_mode'),
    path('allnight_setup/', TemplateView.as_view(template_name='allnight_setup.html'), name='allnight_setup'),
    path('', include('diary.urls')),
]

if settings.DEBUG:
    # 개발용 테스트 프론트(testpages/)를 같은 origin에서 서빙 - 세션/CSRF 쿠키 공유 목적
    urlpatterns += [
        re_path(
            r"^testpages/(?P<path>.*)$",
            static_serve,
            {"document_root": settings.BASE_DIR / "testpages"},
        ),
    ]