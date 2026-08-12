"""drinks 앱 시리얼라이저.

세 갈래로 나뉜다.

1. DrinkSerializer          - 사용자가 직접 만든 음료의 CRUD
2. PresetDrinkSerializer    - 프리셋 카탈로그 조회 (읽기 전용)
3. DrinkFromPresetSerializer- 프리셋을 골라 내 음료로 담기

핵심 원칙: 카페인량은 신뢰 경계를 넘어온 값을 그대로 쓰지 않는다.
프리셋에서 담을 때는 클라이언트가 "무엇을 골랐는지"만 보내고,
실제 mg 값은 서버가 카탈로그에서 조회해 채운다.
"""

from django.db import transaction
from rest_framework import serializers

from .constants import Brand, DrinkType
from .models import Drink
from .presets import find_preset, size_labels


class DrinkSerializer(serializers.ModelSerializer):
    """사용자 소유 음료의 조회/생성/수정.

    직접 입력 음료와 프리셋에서 담은 음료를 구분하지 않고 동일하게 다룬다.
    둘 다 최종적으로 Drink 한 행으로 수렴하기 때문이다.

    user는 fields에서 제외했다. 클라이언트가 보낸 값을 신뢰하면 다른 계정에
    음료를 생성할 수 있으므로, 반드시 context의 request.user로만 주입한다.
    """

    type_display = serializers.CharField(source="get_type_display", read_only=True)
    brand_display = serializers.CharField(source="get_brand_display", read_only=True)

    class Meta:
        model = Drink
        fields = [
            "id",
            "type",
            "type_display",
            "brand",
            "brand_display",
            "name",
            "size",
            "caffeine_mg",
            "is_favorite",
            "is_recent",
            "created_at",
        ]
        read_only_fields = ["id", "is_recent", "created_at"]

    def validate_name(self, value):
        """음료명 공백을 정리하고 빈 문자열을 거부한다.

        Args:
            value (str): 입력된 음료명

        Returns:
            str: 앞뒤 공백이 제거된 음료명

        Raises:
            serializers.ValidationError: 공백만 입력된 경우
        """
        name = value.strip()
        if not name:
            raise serializers.ValidationError("음료 이름을 입력해주세요.")
        return name

    def validate_caffeine_mg(self, value):
        """카페인량이 물리적으로 있을 법한 범위인지 확인한다.

        상한 1000mg은 오타 방지용이다. 건강 기준(400mg)이 아니며,
        400mg 초과는 경고 대상일 뿐 등록을 막지 않는다(공통 규칙 1.7).

        Args:
            value (int): 1회 제공량 기준 카페인량(mg)

        Returns:
            int: 검증을 통과한 값

        Raises:
            serializers.ValidationError: 0 이하이거나 1000 초과인 경우
        """
        if not 0 < value <= 1000:
            raise serializers.ValidationError("카페인량은 1~1000mg 사이여야 합니다.")
        return value

    def validate(self, attrs):
        """브랜드와 사이즈의 조합 정합성을 검사한다.

        사이즈 명칭은 브랜드에 종속되므로 전역 검증이 불가능하다.
        프리셋이 있는 브랜드는 해당 브랜드의 사이즈 라벨만 허용하고,
        프리셋이 없는 브랜드(직접 입력)는 자유 입력을 허용한다.

        Args:
            attrs (dict): 필드 단위 검증을 통과한 값들

        Returns:
            dict: 그대로 통과된 attrs

        Raises:
            serializers.ValidationError: 브랜드에 없는 사이즈이거나,
                사이즈가 필요한 브랜드인데 비어 있는 경우
        """
        brand = attrs.get("brand") or getattr(self.instance, "brand", Brand.CUSTOM)
        size = attrs.get("size", getattr(self.instance, "size", ""))

        labels = size_labels(brand)
        if not labels:
            return attrs

        if not size:
            raise serializers.ValidationError(
                {"size": f"사이즈를 선택해주세요. 가능: {', '.join(labels)}"}
            )
        if size not in labels:
            raise serializers.ValidationError(
                {"size": f"해당 브랜드에 없는 사이즈입니다. 가능: {', '.join(labels)}"}
            )
        return attrs

    def create(self, validated_data):
        """요청 사용자 소유로 음료를 생성하되, 중복은 되살려 재사용한다.

        같은 (user, brand, name, size) 조합이 소프트 삭제 상태로 남아 있으면
        새 행을 만들지 않고 is_active를 되돌린다. 과거 CAFFEINE_LOG의
        drink_id 연결이 끊기지 않게 하기 위함이다.

        Args:
            validated_data (dict): 검증된 필드 값

        Returns:
            Drink: 새로 만들었거나 되살아난 인스턴스
        """
        user = self.context["request"].user
        return _create_or_revive(
            user=user,
            brand=validated_data.get("brand", Brand.CUSTOM),
            name=validated_data["name"],
            size=validated_data.get("size", ""),
            defaults={
                "type": validated_data.get("type", DrinkType.COFFEE),
                "caffeine_mg": validated_data["caffeine_mg"],
                "is_favorite": validated_data.get("is_favorite", False),
            },
        )


class PresetDrinkSerializer(serializers.Serializer):
    """프리셋 카탈로그 응답 스키마 (읽기 전용).

    프리셋은 DB 행이 아니라 상수 dict이므로 ModelSerializer가 아닌
    일반 Serializer를 쓴다. 카탈로그 내부 구조가 바뀌어도 응답 스키마는
    이 클래스가 고정해준다.

    쓰기에는 사용하지 않는다. 프리셋에서 음료를 담을 때는
    DrinkFromPresetSerializer를 쓴다.
    """

    brand = serializers.CharField(read_only=True)
    brand_name = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    size = serializers.CharField(read_only=True, allow_null=True)
    caffeine_mg = serializers.IntegerField(read_only=True)


class DrinkFromPresetSerializer(serializers.Serializer):
    """프리셋 음료를 골라 사용자 음료로 담는다.

    caffeine_mg를 입력으로 받지 않는 것이 이 클래스의 존재 이유다.
    클라이언트는 선택한 조합만 보내고 수치는 서버가 카탈로그에서 채우므로,
    "스타벅스 카페 라떼 Tall = 20mg" 같은 레코드가 만들어질 수 없다.

    아직 카페인량이 입력되지 않은 사이즈는 여기서 걸러진다. 따라서
    Grande/Venti 값이 비어 있는 상태로도 안전하게 배포할 수 있다.
    """

    brand = serializers.CharField()
    name = serializers.CharField()
    size = serializers.CharField(required=False, allow_blank=True)
    is_favorite = serializers.BooleanField(default=False)

    def validate(self, attrs):
        """요청한 조합이 카탈로그에 실재하고 값이 채워져 있는지 확인한다.

        조회 결과를 attrs["_preset"]에 실어 create로 넘긴다. create에서
        다시 조회하면 카탈로그를 두 번 읽게 되므로 여기서 한 번만 읽는다.

        Args:
            attrs (dict): brand, name, size, is_favorite

        Returns:
            dict: _preset 키가 추가된 attrs

        Raises:
            serializers.ValidationError: 존재하지 않는 조합이거나,
                해당 사이즈의 카페인량이 아직 등록되지 않은 경우
        """
        preset = find_preset(
            attrs["brand"], attrs["name"].strip(), attrs.get("size") or None
        )
        if preset is None:
            raise serializers.ValidationError("존재하지 않는 프리셋 음료입니다.")
        if preset["caffeine_mg"] is None:
            raise serializers.ValidationError(
                {"size": "해당 사이즈의 카페인 정보가 아직 등록되지 않았습니다."}
            )

        attrs["_preset"] = preset
        return attrs

    def create(self, validated_data):
        """검증된 프리셋 값으로 Drink를 생성한다.

        type, caffeine_mg는 전부 프리셋에서 가져오고, 클라이언트가 정할 수
        있는 값은 is_favorite뿐이다.

        Args:
            validated_data (dict): _preset이 포함된 검증 결과

        Returns:
            Drink: 새로 만들었거나 되살아난 인스턴스
        """
        preset = validated_data.pop("_preset")
        return _create_or_revive(
            user=self.context["request"].user,
            brand=preset["brand"],
            name=preset["name"],
            size=preset["size"] or "",
            defaults={
                "type": preset["type"],
                "caffeine_mg": preset["caffeine_mg"],
                "is_favorite": validated_data["is_favorite"],
            },
        )

    def to_representation(self, instance):
        """생성 결과를 DrinkSerializer 형식으로 응답한다.

        입력 스키마와 출력 스키마가 다른 경우다. 클라이언트는 방금 만든
        음료의 id와 caffeine_mg를 받아야 바로 카페인 로그를 남길 수 있다.

        Args:
            instance (Drink): create가 반환한 인스턴스

        Returns:
            dict: DrinkSerializer 직렬화 결과
        """
        return DrinkSerializer(instance, context=self.context).data


@transaction.atomic
def _create_or_revive(user, brand, name, size, defaults):
    """중복 음료를 새로 만들지 않고 되살리거나 갱신한다.

    Drink에 걸린 UniqueConstraint는 is_active=True 조건부라서 DRF의
    UniqueTogetherValidator가 자동으로 처리하지 못한다. IntegrityError가
    500으로 새어나가지 않도록 여기서 명시적으로 처리한다.

    동작:
      - 활성 상태의 동일 음료가 있으면 -> 그 행을 반환 (필요 시 즐겨찾기만 갱신)
      - 소프트 삭제된 동일 음료가 있으면 -> is_active를 되돌리고 값 갱신
      - 없으면 -> 새로 생성

    Args:
        user (User): 소유자
        brand (str): 브랜드 코드
        name (str): 음료명
        size (str): 사이즈 라벨. 사이즈가 없으면 빈 문자열
        defaults (dict): type, caffeine_mg, is_favorite

    Returns:
        Drink: 생성/복구/재사용된 인스턴스
    """
    existing = (
        Drink.objects.select_for_update()
        .filter(user=user, brand=brand, name=name, size=size)
        .order_by("-is_active", "-created_at")
        .first()
    )

    if existing is None:
        return Drink.objects.create(
            user=user, brand=brand, name=name, size=size, **defaults
        )

    if not existing.is_active:
        # 되살리면서 최신 카탈로그 값으로 갱신한다.
        existing.is_active = True
        existing.type = defaults["type"]
        existing.caffeine_mg = defaults["caffeine_mg"]

    # 이미 활성 상태라면 즐겨찾기 요청만 반영한다.
    # 과거 로그가 참조하는 caffeine_mg를 임의로 덮어쓰지 않기 위해서다.
    if defaults.get("is_favorite"):
        existing.is_favorite = True

    existing.save()
    return existing