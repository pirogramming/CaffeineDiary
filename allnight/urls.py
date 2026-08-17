# allnight/urls.py
"""allnight 앱 URL 라우팅.

config/urls.py에서 path("", include("allnight.urls"))로 루트에 마운트된다.
diary.urls와 마찬가지로 앱 이름을 URL에 노출하지 않는다.
"""

from django.urls import path

from . import views

app_name = "allnight"

urlpatterns = [
    path(
        "night-sessions/",
        views.NightSessionStartView.as_view(),
        name="night-session-start",
    ),
    path(
        "night-sessions/current/",
        views.NightSessionCurrentView.as_view(),
        name="night-session-current",
    ),
]
