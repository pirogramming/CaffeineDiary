"""diary 앱 URL 라우팅.

config/urls.py에서 path("", include("diary.urls"))로 루트에 마운트된다.
리소스 중심 경로(/users/me/drinks/...)를 채택해 앱 이름(diary)을 URL에
노출하지 않는다. me는 현재 로그인 사용자를 가리킨다.

정적 경로(presets/, from-preset/)를 <int:pk> 앞에 두어 경로 충돌을 피한다.
"""

from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "diary"

urlpatterns = [
    path(
        "users/me/drinks/",
        views.DrinkListCreateView.as_view(),
        name="drink-list",
    ),
    path(
        "users/me/drinks/presets/",
        views.PresetDrinkListView.as_view(),
        name="drink-preset-list",
    ),
    path(
        "users/me/drinks/from-preset/",
        views.DrinkFromPresetView.as_view(),
        name="drink-from-preset",
    ),
    path(
        "users/me/drinks/<int:pk>/",
        views.DrinkDetailView.as_view(),
        name="drink-detail",
    ),

    path(
        "caffeine-logs/",
        views.CaffeineLogListCreateView.as_view(),
        name="log-list",
    ),
    path(
        "caffeine-logs/<int:pk>/",
        views.CaffeineLogDetailView.as_view(),
        name="log-detail",
    ),

    # feed url 임시로추가
    path("feed/", views.FeedView.as_view(), name="feed"),  

    path("favorites/", TemplateView.as_view(template_name="diary/favorites.html"), name="favorites"),
    path("mypage/", TemplateView.as_view(template_name="diary/mypage.html"), name="mypage"),
    path("allnight-setup/", TemplateView.as_view(template_name="diary/allnight_setup.html"), name="allnight-setup"),
    path("allnight-mode/", TemplateView.as_view(template_name="diary/allnight_mode.html"), name="allnight-mode"),
    path("mydiary/", TemplateView.as_view(template_name="diary/mydiary.html"), name="mydiary"),
]
