# 에너지드링크는 사이즈 옵션이 없으므로 sizes 없이
from .starbucks import DrinkCategory

ENERGY = {
    "code": "energy",
    "name": "에너지드링크",
    "sizes": None,
    "drinks": [
        {
            "name": "몬스터 에너지",
            "category": DrinkCategory.ENERGY,
            "caffeine": 100,
        },
        {
            "name": "핫식스 더 킹",
            "category": DrinkCategory.ENERGY,
            "caffeine": 100,
        },
        {
            "name": "레드불",
            "category": DrinkCategory.ENERGY,
            "caffeine": 62.5,
        },
    ],
}