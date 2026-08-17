"""drinks 앱 공용 상수.

음료 종류와 브랜드처럼 값이 고정된 항목만 둔다. 개별 음료 목록은 값이 자주
늘어나므로 choices가 아니라 presets 패키지의 데이터로 관리한다.

이 모듈은 models.py나 presets 패키지를 import하지 않는다. 양쪽 모두가 이
모듈을 참조하므로, 반대 방향 의존이 생기면 순환 import가 발생한다.
"""

from django.db import models


class DrinkType(models.TextChoices):
    """음료 종류. Drink.type의 choices이자 프리셋 카탈로그의 분류 값이다.

    브랜드와 무관한 음료 자체의 속성이므로 브랜드 계층 밖에 둔다.
    """

    COFFEE = "coffee", "커피"
    TEA = "tea", "차"
    ENERGY = "energy", "에너지드링크"
    SODA = "soda", "탄산"
    OTHER = "other", "기타"


class Brand(models.TextChoices):
    """브랜드. Drink.brand의 choices.

    프리셋이 있는 브랜드는 PRESET_BRANDS의 키와 값이 일치해야 한다.
    presets를 import하면 순환 참조가 생기므로 여기서는 수동으로 유지하고,
    정합성은 테스트로 검증한다.

    CUSTOM은 프리셋이 없는 직접 입력용이며, 사이즈 검증 대상에서 제외된다.
    """

    STARBUCKS = "starbucks", "스타벅스"
    COMPOSE = "compose", "컴포즈커피"
    BAIK = "baik", "빽다방"
    MAMMOTH = "mammoth", "매머드커피"
    EDIYA = "ediya", "이디야커피"
    MEGA = "mega", "메가엠지씨커피"
    GONGCHA = "gongcha", "공차"
    PEPSI = "pepsi", "펩시"
    COCACOLA = "cocacola", "코카콜라"
    ENERGY = "energy", "에너지드링크"
    CUSTOM = "custom", "직접 입력"


# 음료 종류(DrinkType)별로 고를 수 있는 아이콘 키 목록. 파일 실체는
# static/images/icons/<key>.svg 이다. Drink.icon_key가 이 목록에 있는
# 값인지 serializer가 검증한다(음료 종류와 안 맞는 아이콘은 못 고르게).
DRINK_ICON_KEYS = {
    DrinkType.COFFEE: [f"coffee_icon{i}" for i in range(1, 7)],
    DrinkType.TEA: ["tea_icon"],
    DrinkType.ENERGY: [f"energydrink_icon{i}" for i in range(1, 8)],
    DrinkType.SODA: [f"cola_icon{i}" for i in range(1, 3)],
}
# "기타"는 전용 아이콘이 없어 커피 아이콘 세트를 그대로 재사용한다.
DRINK_ICON_KEYS[DrinkType.OTHER] = DRINK_ICON_KEYS[DrinkType.COFFEE]