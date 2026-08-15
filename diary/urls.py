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

    path(
        "sleep-logs/",
        views.SleepLogListCreateView.as_view(),
        name="sleep-log-list",
    ),
    # daily_rating.js가 슬래시 없이 POST /sleep-logs를 호출한다(확인됨). Django의
    # APPEND_SLASH는 POST 요청에는 리다이렉트를 못 해줘서(RuntimeError) 슬래시 없는
    # 요청도 같은 뷰로 직접 받도록 별도 경로를 하나 더 둔다.
    path(
        "sleep-logs",
        views.SleepLogListCreateView.as_view(),
        name="sleep-log-list-noslash",
    ),
    path(
        "sleep-logs/<int:pk>/",
        views.SleepLogDetailView.as_view(),
        name="sleep-log-detail",
    ),

    # 명세상 URI는 /feed지만 아래 "feed/"(프론트 HTML 화면)와 경로가 겹쳐
    # 임시로 feed-status/에 둔다. FeedStatusView 참고.
    path(
        "feed-status/",
        views.FeedStatusView.as_view(),
        name="feed-status",
    ),

    # feed url 임시로추가
    path("feed/", views.FeedView.as_view(), name="feed"),  

    # 수면 설문 임시로 추가
    path("sleep-logs/time", views.SleepLogTimeView.as_view(), name="sleep-log-time"),
    path("sleep-logs/rating", views.SleepLogRatingView.as_view(), name="sleep-log-rating"),

    # intial_survey url 임시로추가
    path("initial_survey/", views.SurveyStartView.as_view(), name="survey-start"),
    path("initial_survey/category/", views.SurveyCategoryView.as_view(), name="survey-category"),
    path("initial_survey/brand/", views.SurveyBrandView.as_view(), name="survey-brand"),
    path("initial_survey/menu/", views.SurveyMenuView.as_view(), name="survey-menu"),
    path("initial_survey/size/", views.SurveySizeView.as_view(), name="survey-size"),
    path("initial_survey/sleep/", views.SurveySleepView.as_view(), name="survey-sleep"),
    path("favorites/", TemplateView.as_view(template_name="diary/favorites.html"), name="favorites"),
    path("mypage/", TemplateView.as_view(template_name="diary/mypage.html"), name="mypage"),
    path("allnight-setup/", TemplateView.as_view(template_name="diary/allnight_setup.html"), name="allnight-setup"),
    path("allnight-mode/", TemplateView.as_view(template_name="diary/allnight_mode.html"), name="allnight-mode"),
    path("mydiary/", TemplateView.as_view(template_name="diary/mydiary.html"), name="mydiary"),
]
