"""diary 앱 뷰 - 음료(Drink) API.

인증된 사용자의 음료 마스터를 다룬다. 직렬화기(serializers.py)와 프리셋
카탈로그(presets/)는 이미 완성돼 있으므로, 여기서는 요청/권한/쿼리셋만
연결한다.

권한 원칙:
  - 로그인 필수(IsAuthenticated). settings에 DEFAULT_PERMISSION_CLASSES가
    없어 기본값이 AllowAny이므로, 각 뷰에서 명시적으로 지정한다.
  - 쿼리셋을 request.user로 좁혀, 타인의 음료는 조회/수정/삭제 대상에서
    아예 제외한다(404로 떨어진다).
"""

from django.utils.dateparse import parse_date
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from .models import CaffeineLog, Drink
from .presets import iter_presets
from .serializers import (
    CaffeineLogSerializer,
    DrinkFromPresetSerializer,
    DrinkSerializer,
    PresetDrinkSerializer,
)

# 임시로 추가
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DrinkListCreateView(generics.ListCreateAPIView):
    """음료 목록 조회 / 직접 입력 생성.

    GET  /users/me/drinks/   - 본인의 활성 음료 목록
    POST /users/me/drinks/   - 직접 입력으로 음료 생성

    생성 시 user는 클라이언트 값을 신뢰하지 않고 serializer가 context의
    request.user로 주입한다.
    """

    serializer_class = DrinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """본인의 활성 음료만, 즐겨찾기 우선 최신순으로 반환한다."""
        return (
            Drink.objects.filter(user=self.request.user, is_active=True)
            .order_by("-is_favorite", "-created_at")
        )


class DrinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """음료 상세 조회 / 수정 / 삭제.

    GET    /users/me/drinks/<id>/   - 상세 조회
    PATCH  /users/me/drinks/<id>/   - 수정 (즐겨찾기 토글 등)
    DELETE /users/me/drinks/<id>/   - 소프트 삭제

    쿼리셋을 본인 소유 + 활성 음료로 제한하므로, 타인의 음료나 이미 삭제된
    음료에 접근하면 404가 된다.
    """

    serializer_class = DrinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Drink.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        """DB에서 지우지 않고 is_active=False로 소프트 삭제한다.

        과거 CaffeineLog가 drink_id로 이 행을 참조하므로 실제 삭제하지
        않는다. 되살리기는 serializer의 _create_or_revive가 담당한다.
        """
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class PresetDrinkListView(generics.ListAPIView):
    """프리셋 카탈로그 조회 (읽기 전용).

    GET /users/me/drinks/presets/                    - 전체 프리셋
    GET /users/me/drinks/presets/?type=coffee        - 특정 종류만
    GET /users/me/drinks/presets/?brand=starbucks    - 특정 브랜드만
    GET /users/me/drinks/presets/?type=coffee&brand=starbucks - 둘 다 적용

    카탈로그는 DB 행이 아니라 상수이므로 (브랜드, 음료, 사이즈) leaf 단위로
    펼쳐 반환한다. 카페인량이 아직 입력되지 않은 사이즈는 제외된다.    """

    serializer_class = PresetDrinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        brand = self.request.query_params.get("brand")
        drink_type = self.request.query_params.get("type")

        presets = iter_presets(brand_code=brand)
        if drink_type:
            presets = (p for p in presets if p["type"] == drink_type)
        return list(presets)


class DrinkFromPresetView(generics.CreateAPIView):
    """프리셋을 골라 내 음료로 담기.

    POST /users/me/drinks/from-preset/

    클라이언트는 (브랜드, 음료명, 사이즈)만 보내고 카페인량은 서버가
    카탈로그에서 채운다. 응답은 DrinkSerializer 형식(id, caffeine_mg 포함)이라
    바로 카페인 로그를 남길 수 있다.
    """

    serializer_class = DrinkFromPresetSerializer
    permission_classes = [permissions.IsAuthenticated]

class CaffeineLogPagination(PageNumberPagination):
    """섭취기록 목록 페이지네이션.

    page_size_query_param을 열어 클라이언트가 page_size로 페이지 크기를
    조절할 수 있게 한다(명세: page, page_size). max_page_size로 과도한
    조회를 막는다.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CaffeineLogListCreateView(generics.ListCreateAPIView):
    """섭취기록 목록 조회 / 생성(한잔·커스텀).

    GET  /caffeine-logs/   - 본인 기록 목록(최신순). start_date~end_date로
                             기간을 좁히고 page/page_size로 페이지네이션한다.
    POST /caffeine-logs/   - 한잔(drink_id) 또는 커스텀(caffeine_mg+name) 기록

    기간 필터는 created_at의 날짜(UTC) 기준이다. start_date/end_date는
    YYYY-MM-DD 형식이며 파싱에 실패하면 무시한다.
    """

    serializer_class = CaffeineLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CaffeineLogPagination

    def get_queryset(self):
        """본인 기록만 최신순으로, 요청된 기간으로 좁혀 반환한다."""
        qs = CaffeineLog.objects.filter(user=self.request.user).order_by("-created_at")

        start = parse_date(self.request.query_params.get("start_date", "") or "")
        end = parse_date(self.request.query_params.get("end_date", "") or "")
        if start:
            qs = qs.filter(created_at__date__gte=start)
        if end:
            qs = qs.filter(created_at__date__lte=end)
        return qs


class CaffeineLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """섭취기록 상세 조회 / 수정 / 삭제.

    GET    /caffeine-logs/<id>/   - 상세 조회
    PATCH  /caffeine-logs/<id>/   - 수정(커스텀 값 정정 등)
    DELETE /caffeine-logs/<id>/   - 삭제

    쿼리셋을 본인 소유로 제한하므로 타인의 기록에 접근하면 404가 된다.
    """

    serializer_class = CaffeineLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CaffeineLog.objects.filter(user=self.request.user)


# main(맨 처음 들어갔을 때 화면) view 추가 (임시)
class MainView(LoginRequiredMixin, TemplateView):
    login_url = "/login"
    template_name = "diary/base.html"
    extra_context = {"page_title": "메인 화면"}


# feed(한잔마시기) view 추가 (임시))
class FeedView(LoginRequiredMixin, TemplateView):
    login_url = "/login"
    template_name = "diary/feed.html"
    extra_context = {"page_title": "피드 화면"}