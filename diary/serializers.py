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
from django.utils import timezone
from rest_framework import serializers

from calcs.pharmacokinetics import concentration_at

from .calc_bridge import doses_for_user
from .constants import Brand, DRINK_ICON_KEYS, DrinkType
from .models import CaffeineLog, Drink, SleepLog
from .presets import find_preset, size_labels


class DrinkSerializer(serializers.ModelSerializer):
    """사용자 소유 음료의 조회/생성/수정.

    직접 입력 음료와 프리셋에서 담은 음료를 구분하지 않고 동일하게 다룬다.
    둘 다 최종적으로 Drink 한 행으로 수렴하기 때문이다.

    user는 fields에서 제외했다. 클라이언트가 보낸 값을 신뢰하면 다른 계정에
    음료를 생성할 수 있으므로, 반드시 context의 request.user로만 주입한다.
    """

    type_display = serializers.CharField(source="get_type_display", read_only=True)
    brand_display = serializers.SerializerMethodField()

    class Meta:
        model = Drink
        fields = [
            "id",
            "type",
            "type_display",
            "brand",
            "custom_brand_name",
            "brand_display",
            "name",
            "size",
            "icon_key",
            "caffeine_mg",
            "is_favorite",
            "is_recent",
            "created_at",
        ]
        read_only_fields = ["id", "is_recent", "created_at"]

    def get_brand_display(self, obj):
        """brand=custom이고 custom_brand_name이 있으면 그 값을, 아니면 choices 라벨을 보여준다.

        Args:
            obj (Drink): 직렬화 대상 인스턴스

        Returns:
            str: 화면에 보여줄 브랜드명
        """
        if obj.brand == Brand.CUSTOM and obj.custom_brand_name:
            return obj.custom_brand_name
        return obj.get_brand_display()

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

        # custom이 아닌 브랜드에는 자유 입력 브랜드명이 의미가 없으므로 비워둔다.
        if brand != Brand.CUSTOM:
            attrs["custom_brand_name"] = ""

        icon_key = attrs.get("icon_key", getattr(self.instance, "icon_key", ""))
        if icon_key:
            drink_type = attrs.get("type", getattr(self.instance, "type", DrinkType.COFFEE))
            _validate_icon_key(icon_key, drink_type)

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
            custom_brand_name=validated_data.get("custom_brand_name", ""),
            name=validated_data["name"],
            size=validated_data.get("size", ""),
            defaults={
                "type": validated_data.get("type", DrinkType.COFFEE),
                "caffeine_mg": validated_data["caffeine_mg"],
                "is_favorite": validated_data.get("is_favorite", False),
                "icon_key": validated_data.get("icon_key", ""),
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
    icon_key = serializers.CharField(required=False, allow_blank=True, default="")
    is_favorite = serializers.BooleanField(default=False)

    def validate(self, attrs):
        """요청한 조합이 카탈로그에 실재하고 값이 채워져 있는지 확인한다.

        조회 결과를 attrs["_preset"]에 실어 create로 넘긴다. create에서
        다시 조회하면 카탈로그를 두 번 읽게 되므로 여기서 한 번만 읽는다.

        Args:
            attrs (dict): brand, name, size, icon_key, is_favorite

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
        if attrs.get("icon_key"):
            _validate_icon_key(attrs["icon_key"], preset["type"])

        attrs["_preset"] = preset
        return attrs

    def create(self, validated_data):
        """검증된 프리셋 값으로 Drink를 생성한다.

        type, caffeine_mg는 전부 프리셋에서 가져오고, 클라이언트가 정할 수
        있는 값은 icon_key·is_favorite뿐이다.

        Args:
            validated_data (dict): _preset이 포함된 검증 결과

        Returns:
            Drink: 새로 만들었거나 되살아난 인스턴스
        """
        preset = validated_data.pop("_preset")
        return _create_or_revive(
            user=self.context["request"].user,
            brand=preset["brand"],
            custom_brand_name="",
            name=preset["name"],
            size=preset["size"] or "",
            defaults={
                "type": preset["type"],
                "caffeine_mg": preset["caffeine_mg"],
                "is_favorite": validated_data["is_favorite"],
                "icon_key": validated_data.get("icon_key", ""),
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


class CaffeineLogSerializer(serializers.ModelSerializer):
    """카페인 섭취기록 조회/생성/수정.

    두 가지 기록 방식을 하나의 스키마로 받는다.
      - 한잔  : drink_id로 등록된 음료를 지목한다. caffeine_mg와 name은
                서버가 해당 Drink에서 스냅샷으로 박제하며, 클라이언트가 보낸
                값은 무시한다("스타벅스 라떼 = 5mg" 같은 위조를 막는다).
      - 커스텀: drink_id 없이 caffeine_mg와 name을 직접 입력한다.

    스냅샷 정책: 기록 이후 Drink가 수정/삭제되어도 이 로그의 값은 보존된다.
    drink는 SET_NULL이라 연결이 끊길 수 있으므로 name도 함께 박제한다.

    user는 fields에서 제외했다. 클라이언트가 보낸 값을 신뢰하면 다른 계정에
    기록을 남길 수 있으므로, create에서 context의 request.user로만 주입한다.
    """

    drink_id = serializers.PrimaryKeyRelatedField(
        source="drink",
        queryset=Drink.objects.none(),  # __init__에서 요청 사용자 소유로 좁힌다
        required=False,
        allow_null=True,
    )
    caffeine_mg = serializers.FloatField(required=False)

    class Meta:
        model = CaffeineLog
        fields = ["id", "drink_id", "name", "caffeine_mg", "created_at"]
        read_only_fields = ["id", "created_at"]

    def __init__(self, *args, **kwargs):
        """drink_id 후보를 요청 사용자의 활성 음료로 제한한다.

        queryset을 좁히면 타인 소유 drink_id는 존재하지 않는 값으로 취급되어
        검증 단계에서 걸러진다(다른 사람 음료로 기록을 남길 수 없다).
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None and getattr(request.user, "is_authenticated", False):
            self.fields["drink_id"].queryset = Drink.objects.filter(
                user=request.user, is_active=True
            )

    def validate(self, attrs):
        """한잔/커스텀을 구분해 스냅샷을 채우거나 입력값을 검증한다.

        이번 요청에 drink가 지정되면 '한잔'으로 보고 서버가 caffeine_mg/name을
        박제한다. drink가 없으면 '커스텀'이며, 생성 시에는 두 값이 필수다.
        drink를 보내지 않는 PATCH에서는 기존 스냅샷을 임의로 다시 덮어쓰지
        않는다(과거 기록의 caffeine_mg 불변성을 지키기 위해서다).

        Args:
            attrs (dict): 필드 단위 검증을 통과한 값들

        Returns:
            dict: 스냅샷이 채워졌거나 정리된 attrs

        Raises:
            serializers.ValidationError: 커스텀 생성에 필수값이 없거나,
                카페인량이 범위를 벗어나거나, 이름이 공백인 경우
        """
        if attrs.get("drink") is not None:
            drink = attrs["drink"]
            attrs["caffeine_mg"] = drink.caffeine_mg
            attrs["name"] = drink.name
            return attrs

        if self.instance is None:  # 커스텀 생성
            if attrs.get("caffeine_mg") is None:
                raise serializers.ValidationError(
                    {"caffeine_mg": "카페인량을 입력해주세요."}
                )
            if not (attrs.get("name") or "").strip():
                raise serializers.ValidationError({"name": "음료 이름을 입력해주세요."})

        # 넘어온 값만 범위/공백 검증한다(생성·수정 공통).
        if attrs.get("caffeine_mg") is not None and not 0 < attrs["caffeine_mg"] <= 1000:
            raise serializers.ValidationError(
                {"caffeine_mg": "카페인량은 1~1000mg 사이여야 합니다."}
            )
        if "name" in attrs:
            name = attrs["name"].strip()
            if not name:
                raise serializers.ValidationError({"name": "음료 이름을 입력해주세요."})
            attrs["name"] = name
        return attrs

    def create(self, validated_data):
        """요청 사용자 소유로 기록을 생성하고 참조 음료를 '최근'으로 표시한다.

        Args:
            validated_data (dict): 스냅샷이 채워진 검증 결과

        Returns:
            CaffeineLog: 생성된 인스턴스
        """
        validated_data["user"] = self.context["request"].user
        log = super().create(validated_data)
        if log.drink_id and not log.drink.is_recent:
            log.drink.is_recent = True
            log.drink.save(update_fields=["is_recent"])
        return log


class SleepLogSerializer(serializers.ModelSerializer):
    """수면기록 조회/생성/수정.

    residual_mg_at_sleep(취침시각의 잔류 카페인량)은 클라이언트가 보낼 수 없는
    계산값이다. actual_bedtime이 (처음) 정해지거나 바뀔 때, calcs 엔진으로
    해당 사용자의 최근 CaffeineLog를 모아 그 시각의 잔류량을 계산해 스냅샷으로
    박제한다. 이후 CaffeineLog가 추가/삭제돼도 이미 기록된 값은 보존된다
    (CaffeineLog.caffeine_mg 스냅샷 정책과 동일한 이유).

    user는 fields에서 제외했다. create에서 context의 request.user로만 주입한다.
    """

    residual_mg_at_sleep = serializers.FloatField(read_only=True)

    class Meta:
        model = SleepLog
        fields = [
            "id",
            "actual_bedtime",
            "wakeup_time",
            "sleep_quality",
            "residual_mg_at_sleep",
            "created_at",
        ]
        read_only_fields = ["id", "residual_mg_at_sleep", "created_at"]

    def validate_sleep_quality(self, value):
        """수면질은 1~5점 설문 척도다.

        Args:
            value (int): 입력된 수면질 점수

        Returns:
            int: 검증을 통과한 값

        Raises:
            serializers.ValidationError: 1~5 범위를 벗어난 경우
        """
        if not 1 <= value <= 5:
            raise serializers.ValidationError("수면질은 1~5 사이여야 합니다.")
        return value

    def validate(self, attrs):
        """기상 시각이 취침 시각보다 앞서거나, 취침 시각이 미래인 오입력을 막는다.

        미래 actual_bedtime 차단은 명세 SLEEP-002 요구사항이다("아직 안 일어난
        일"을 기록할 수 없게 한다).

        Args:
            attrs (dict): 필드 단위 검증을 통과한 값들

        Returns:
            dict: 그대로 통과된 attrs

        Raises:
            serializers.ValidationError: wakeup_time이 actual_bedtime보다 앞서거나,
                actual_bedtime이 미래 시각인 경우
        """
        bedtime = attrs.get("actual_bedtime", getattr(self.instance, "actual_bedtime", None))
        wakeup = attrs.get("wakeup_time", getattr(self.instance, "wakeup_time", None))
        if bedtime and wakeup and wakeup <= bedtime:
            raise serializers.ValidationError(
                {"wakeup_time": "기상 시각은 취침 시각 이후여야 합니다."}
            )
        if "actual_bedtime" in attrs and bedtime and bedtime > timezone.now():
            raise serializers.ValidationError(
                {"actual_bedtime": "미래 시각은 입력할 수 없습니다."}
            )
        return attrs

    @staticmethod
    def _residual_at(user, bedtime):
        """취침시각 기준, 요청 사용자의 최근 섭취기록으로 잔류 카페인량(mg)을 계산한다.

        Args:
            user (User): 대상 사용자
            bedtime (datetime): 잔류량을 계산할 시각

        Returns:
            float: 반올림된 잔류 카페인량(mg)
        """
        doses = doses_for_user(user, bedtime)
        return round(concentration_at(doses, bedtime), 2)

    def create(self, validated_data):
        """요청 사용자 소유로 기록을 생성하고, bedtime이 있으면 잔류량을 스냅샷한다.

        Args:
            validated_data (dict): 검증된 필드 값

        Returns:
            SleepLog: 생성된 인스턴스
        """
        user = self.context["request"].user
        validated_data["user"] = user
        bedtime = validated_data.get("actual_bedtime")
        if bedtime is not None:
            validated_data["residual_mg_at_sleep"] = self._residual_at(user, bedtime)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """actual_bedtime이 이번 요청에서 바뀔 때만 잔류량을 다시 계산한다.

        보내지 않은 필드는 건드리지 않아 기존 스냅샷을 임의로 덮어쓰지 않는다.

        Args:
            instance (SleepLog): 수정 대상
            validated_data (dict): 검증된 필드 값

        Returns:
            SleepLog: 수정된 인스턴스
        """
        if "actual_bedtime" in validated_data:
            bedtime = validated_data["actual_bedtime"]
            validated_data["residual_mg_at_sleep"] = (
                self._residual_at(instance.user, bedtime) if bedtime is not None else None
            )
        return super().update(instance, validated_data)


def _validate_icon_key(icon_key, drink_type):
    """icon_key가 drink_type에서 고를 수 있는 아이콘인지 확인한다.

    Args:
        icon_key (str): static/images/icons/<icon_key>.svg
        drink_type (str): constants.DrinkType 값

    Raises:
        serializers.ValidationError: 해당 종류에 없는 아이콘 키인 경우
    """
    valid_keys = DRINK_ICON_KEYS.get(drink_type, [])
    if icon_key not in valid_keys:
        raise serializers.ValidationError(
            {"icon_key": f"해당 종류에서 고를 수 없는 아이콘입니다. 가능: {', '.join(valid_keys)}"}
        )


@transaction.atomic
def _create_or_revive(user, brand, custom_brand_name, name, size, defaults):
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
        custom_brand_name (str): brand=custom일 때의 자유 입력 브랜드명. 그 외엔 빈 문자열
        name (str): 음료명
        size (str): 사이즈 라벨. 사이즈가 없으면 빈 문자열
        defaults (dict): type, caffeine_mg, is_favorite, icon_key

    Returns:
        Drink: 생성/복구/재사용된 인스턴스
    """
    existing = (
        Drink.objects.select_for_update()
        .filter(user=user, brand=brand, custom_brand_name=custom_brand_name, name=name, size=size)
        .order_by("-is_active", "-created_at")
        .first()
    )

    if existing is None:
        return Drink.objects.create(
            user=user, brand=brand, custom_brand_name=custom_brand_name, name=name, size=size, **defaults
        )

    if not existing.is_active:
        # 되살리면서 최신 카탈로그 값으로 갱신한다.
        existing.is_active = True
        existing.type = defaults["type"]
        existing.caffeine_mg = defaults["caffeine_mg"]
        existing.icon_key = defaults.get("icon_key", "")

    # 이미 활성 상태라면 즐겨찾기 요청만 반영한다.
    # 과거 로그가 참조하는 caffeine_mg를 임의로 덮어쓰지 않기 위해서다.
    if defaults.get("is_favorite"):
        existing.is_favorite = True

    existing.save()
    return existing