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

from rest_framework import generics, permissions

from .models import Drink
from .presets import iter_presets
from .serializers import (
    DrinkFromPresetSerializer,
    DrinkSerializer,
    PresetDrinkSerializer,
)


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

    GET /users/me/drinks/presets/           - 전체 프리셋
    GET /users/me/drinks/presets/?brand=... - 특정 브랜드만

    카탈로그는 DB 행이 아니라 상수이므로 (브랜드, 음료, 사이즈) leaf 단위로
    펼쳐 반환한다. 카페인량이 아직 입력되지 않은 사이즈는 제외된다.
    """

    serializer_class = PresetDrinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        brand = self.request.query_params.get("brand")
        return list(iter_presets(brand_code=brand))


class DrinkFromPresetView(generics.CreateAPIView):
    """프리셋을 골라 내 음료로 담기.

    POST /users/me/drinks/from-preset/

    클라이언트는 (브랜드, 음료명, 사이즈)만 보내고 카페인량은 서버가
    카탈로그에서 채운다. 응답은 DrinkSerializer 형식(id, caffeine_mg 포함)이라
    바로 카페인 로그를 남길 수 있다.
    """

    serializer_class = DrinkFromPresetSerializer
    permission_classes = [permissions.IsAuthenticated]
