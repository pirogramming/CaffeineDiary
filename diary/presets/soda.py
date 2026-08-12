"""탄산음료(콜라) 프리셋.

매장 브랜드가 아니라 제조사 브랜드이므로 카페 프리셋과 달리 한 파일에
두 브랜드(펩시, 코카콜라)를 함께 둔다.

[사이즈] 캔/페트 규격 기준으로 s1=190ml(미니캔), s2=355ml(캔),
s3=500ml(페트) 3종을 둔다. 세 규격이 모두 판매되지 않는 제품은
해당 사이즈 키를 삭제할 것.

[카페인] 값은 미입력 상태(None)다. 제품별 실측치를 확인해 직접 채울 것.
제로 슈거 제품도 카페인은 일반 제품과 비슷하거나 동일하므로 별도로 확인한다.
"""

from ..constants import DrinkType


# 두 브랜드가 같은 규격을 쓰므로 사이즈 정의를 공유한다.
SODA_SIZES = [
    {"code": "s1", "label": "190ml", "volume_ml": 190},
    {"code": "s2", "label": "355ml", "volume_ml": 355},
    {"code": "s3", "label": "500ml", "volume_ml": 500},
]


PEPSI = {
    "code": "pepsi",
    "name": "펩시",
    "sizes": SODA_SIZES,
    "drinks": [
        {
            "name": "펩시",
            "category": DrinkType.SODA,
            "caffeine": {"s1": 24, "s2": 38, "s3": 53},
        },
        {
            "name": "펩시 제로 라임",
            "category": DrinkType.SODA,
            "caffeine": {"s1": 23, "s2": 46, "s3": 60},
        },
    ],
}


COCACOLA = {
    "code": "cocacola",
    "name": "코카콜라",
    "sizes": SODA_SIZES,
    "drinks": [
        {
            "name": "코카콜라",
            "category": DrinkType.SODA,
            "caffeine": {"s1": 18, "s2": 35, "s3": 60},
        },
        {
            "name": "코카콜라 제로",
            "category": DrinkType.SODA,
            "caffeine": {"s1": 18, "s2": 35, "s3": 60},
        },
    ],
}
