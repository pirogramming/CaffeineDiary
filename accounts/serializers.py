# accounts/serializers.py
"""accounts 앱 시리얼라이저.

UserProfile 조회/생성/수정을 다룬다. 명세(Notion API 명세서, PROF-001~002)
기준이며, calcs 엔진(CALC-002~003)이 쓰는 target_bedtime·body_weight_kg가
핵심 입력값이다.
"""

from rest_framework import serializers

from diary.constants import Brand, DrinkType
from diary.models import Drink

from .models import UserProfile


class ProfileDrinkSerializer(serializers.Serializer):
    """프로필 최초 생성 시 함께 등록하는 즐겨찾는 음료 입력.

    Drink는 유저 소유 모델이라 전역 마스터가 없다. 여기서 받은 값이 곧
    그 사용자의 Drink 레코드가 된다(명세 PROF-001).
    """

    name = serializers.CharField()
    caffeine_mg = serializers.FloatField()

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("음료 이름을 입력해주세요.")
        return name

    def validate_caffeine_mg(self, value):
        if not 0 < value <= 1000:
            raise serializers.ValidationError("카페인량은 1~1000mg 사이여야 합니다.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """UserProfile 조회/생성/수정.

    target_bedtime(명세 필드명) <-> target_sleeptime(모델 필드명)을 매핑한다.
    두 이름이 다른 이유는 모델이 명세보다 먼저 존재했기 때문이다 — 모델을
    바꾸면 기존 마이그레이션 이력이 깨지므로, 여기서 이름만 맞춘다.

    drinks는 생성 시에만 받는 쓰기 전용 입력이다(PROF-002 PATCH는 프로필
    필드만 바꾸고, 음료 목록은 diary의 Drink API로 별도 관리한다).
    """

    target_bedtime = serializers.TimeField(
        source="target_sleeptime", format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"]
    )
    drinks = ProfileDrinkSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = ["target_bedtime", "body_weight_kg", "drinks"]

    def validate_drinks(self, value):
        """최초 생성 시에는 즐겨찾는 음료가 최소 1개 필요하고, 이름 중복도 막는다.

        Args:
            value (list[dict]): 검증된 개별 음료 입력들

        Returns:
            list[dict]: 그대로 통과된 값

        Raises:
            serializers.ValidationError: 생성인데 0개이거나, 이름이 중복된 경우
        """
        if self.instance is None and not value:
            raise serializers.ValidationError("즐겨찾는 음료를 최소 1개 이상 등록해주세요.")
        names = [d["name"] for d in value]
        if len(names) != len(set(names)):
            raise serializers.ValidationError("음료 이름이 중복되었습니다.")
        return value

    def create(self, validated_data):
        """UserProfile을 만들고, 함께 받은 음료들을 사용자 소유 Drink로 생성한다.

        Args:
            validated_data (dict): target_sleeptime, body_weight_kg, drinks

        Returns:
            UserProfile: 생성된 인스턴스
        """
        drinks = validated_data.pop("drinks", [])
        user = self.context["request"].user
        profile = UserProfile.objects.create(user=user, **validated_data)
        for d in drinks:
            Drink.objects.create(
                user=user,
                name=d["name"],
                caffeine_mg=d["caffeine_mg"],
                brand=Brand.CUSTOM,
                type=DrinkType.COFFEE,
                is_favorite=True,
            )
        return profile
