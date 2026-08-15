# accounts/serializers.py
"""accounts 앱 시리얼라이저.

두 갈래로 나뉜다.

1. SignupSerializer      - 회원가입(AUTH-002) 입력 검증
2. UserProfileSerializer - UserProfile 조회/생성/수정(PROF-001~002)

UserProfile은 calcs 엔진(CALC-002~003)이 쓰는 target_bedtime·body_weight_kg가
핵심 입력값이다.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from calcs.pharmacokinetics import W_MAX_KG, W_MIN_KG
from diary.constants import Brand, DrinkType
from diary.models import Drink

from .models import UserProfile

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """회원가입 입력(AUTH-002).

    계정 생성만 담당한다. UserProfile 생성과 즐겨찾는 Drink 등록은 별도
    엔드포인트(PROF-001)에서 처리한다.

    username 중복 검사는 여기서 하지 않는다 — 명세상 409(Conflict)인데,
    이 serializer의 검증 실패는 전부 400으로 매핑되기 때문이다(config의
    공통 예외 처리기 참고). 중복 검사는 view에서 별도로 한다.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True, required=False)

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("아이디를 입력해주세요.")
        return username

    def validate(self, attrs):
        """비밀번호 정책(settings.AUTH_PASSWORD_VALIDATORS)과 확인 일치를 검사한다.

        User.objects.create_user()는 이 검증기들을 자동으로 실행하지
        않으므로(흔한 Django 함정) 여기서 명시적으로 호출해야 한다.

        Args:
            attrs (dict): 필드 단위 검증을 통과한 값들

        Returns:
            dict: 그대로 통과된 attrs

        Raises:
            serializers.ValidationError: 비밀번호 불일치이거나 정책 위반인 경우
        """
        password = attrs.get("password")
        # password_confirm은 선택 입력이다. 보냈을 때만 일치 검사하고,
        # 안 보냈으면(현재 프론트 폼) 재확인 검사를 건너뛴다.
        confirm = attrs.get("password_confirm")
        if confirm is not None and password != confirm:
            raise serializers.ValidationError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )
        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": " ".join(exc.messages)})
        return attrs


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
    # 모델 필드(body_weight_kg = FloatField(null=True))는 선택값이라 ModelSerializer가
    # 자동 생성하면 required=False가 된다. 명세(PROF-001)는 생성 시 필수라서 명시적으로
    # 다시 선언한다 — target_bedtime과 같은 이유. PATCH(partial=True)에서는 DRF가 이
    # required를 무시하므로 그대로 선택값으로 동작한다.
    body_weight_kg = serializers.FloatField()
    drinks = ProfileDrinkSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = ["target_bedtime", "body_weight_kg", "drinks"]

    def validate_body_weight_kg(self, value):
        """calcs 엔진이 clamp_weight()로 내부적으로 [W_MIN_KG, W_MAX_KG]로 잘라내는데,
        API 경계에서 걸러야 할 값(음수·0·비현실적인 값)을 그냥 통과시키지 않기 위해
        같은 범위를 여기서도 검증한다.

        Args:
            value (float): 입력된 체중(kg)

        Returns:
            float: 검증을 통과한 값

        Raises:
            serializers.ValidationError: W_MIN_KG~W_MAX_KG 범위를 벗어난 경우
        """
        if not W_MIN_KG <= value <= W_MAX_KG:
            raise serializers.ValidationError(
                f"체중은 {W_MIN_KG:.0f}~{W_MAX_KG:.0f}kg 사이여야 합니다."
            )
        return value

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
