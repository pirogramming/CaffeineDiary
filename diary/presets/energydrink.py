# 에너지드링크는 캔 규격이 고정되어 사이즈 선택지가 없다.
# 다른 브랜드(예: 매머드커피)와 동일하게, 사이즈 코드는 s1("기본") 하나만
# 두고 caffeine도 {코드: mg} 형태로 맞춘다. presets/__init__.py의 헬퍼들이
# 전부 brand["sizes"]를 리스트로, drink["caffeine"]을 dict로 가정하기
# 때문이다.
from ..constants import DrinkType


ENERGY_SIZES = [
    {"code": "s1", "label": "기본"},
]


ENERGY = {
    "code": "energy",
    "name": "에너지드링크",
    "sizes": ENERGY_SIZES,
    "drinks": [
        {
            "name": "몬스터 에너지",
            "category": DrinkType.ENERGY,
            "caffeine": {"s1": 100},
        },
        {
            "name": "핫식스 더 킹",
            "category": DrinkType.ENERGY,
            "caffeine": {"s1": 100},
        },
        {
            "name": "레드불",
            "category": DrinkType.ENERGY,
            "caffeine": {"s1": 62.5},
        },
    ],
}