"""컴포즈커피 고카페인 음료 프리셋.

출처: https://composecoffee.com/compose?tab=nutrition ("02. 커피ㆍ콜드브루" 탭 1~3페이지 + "03. 베버리지" · "04. 프라페ㆍ스무디" · "05. 밀크쉐이크" · "09. 아이스크림" 탭)
선정 기준: 100ml당 카페인 15mg 이상

[수집 범위] 커피ㆍ콜드브루 · 베버리지 · 프라페ㆍ스무디 · 밀크쉐이크 ·
아이스크림 탭을 포함한다. 티 / 에이드ㆍ주스 탭은 전 품목이 기준 미달이라 제외했다.
아이스크림 탭 항목은 컵 단위 제공량 기준이며 사이즈 선택지가 없다.

[사이즈] s1=레귤러, s2=빅포즈. 빅포즈는 일부 메뉴만 제공하므로 미제공 음료는
s2가 None이다. 사이즈 개념이 없는 에스프레소는 s2 키를 두지 않는다.
빅포즈 용량은 대부분 946ml이나 파인애플 커피만 649ml로 표기돼 있어,
COMPOSE_SIZES의 volume_ml은 대표값이며 개별 음료와 어긋날 수 있다.

[표기] H- 접두는 핫, I- 접두는 아이스이며 원본 메뉴명을 그대로 사용한다.
두 버전의 카페인량은 동일하다.
"""

from ..constants import DrinkType


COMPOSE_SIZES = [
    {"code": "s1", "label": "레귤러", "volume_ml": 591},
    {"code": "s2", "label": "빅포즈", "volume_ml": 946},
]


COMPOSE = {
    "code": "compose",
    "name": "컴포즈커피",
    "sizes": COMPOSE_SIZES,
    "drinks": [
        {
            "name": "에스프레소",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186},  # 레귤러 412.9mg/100ml
        },
        {
            "name": "아이스크림 모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 188},  # 레귤러 45.5mg/100ml
        },
        {
            "name": "아이스크림 카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186},  # 레귤러 44.9mg/100ml
        },
        {
            "name": "솔티드 카라멜 아이스크림 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186},  # 레귤러 44.9mg/100ml
        },
        {
            "name": "H-카페모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 254, "s2": None},  # 레귤러 42.9mg/100ml
        },
        {
            "name": "I-카페모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 254, "s2": None},  # 레귤러 42.9mg/100ml
        },
        {
            "name": "H-카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "I-카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": 495},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "H-카푸치노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "H-바닐라라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "I-바닐라라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": 495},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "H-헤이즐넛라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "I-헤이즐넛라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": 495},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "H-돌체라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "I-돌체라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": 495},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "H-캬라멜마끼아또",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "I-캬라멜마끼아또",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "I-아인슈페너라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 248, "s2": None},  # 레귤러 41.9mg/100ml
        },
        {
            "name": "아포가토",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 124},  # 레귤러 41.8mg/100ml
        },
        {
            "name": "I-컴포즈믹스커피",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 216, "s2": None},  # 레귤러 36.5mg/100ml
        },
        {
            "name": "I-아샷추",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 201, "s2": 209},  # 레귤러 34.1mg/100ml
        },
        {
            "name": "모카자바칩프라페",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 200, "s2": None},  # 레귤러 33.9mg/100ml
        },
        {
            "name": "그린티프라페",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 196, "s2": None},  # 레귤러 33.2mg/100ml
        },
        {
            "name": "I-베러댄아인슈페너",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.5mg/100ml
        },
        {
            "name": "H-아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "I-아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": 372},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "I-달고나라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "H-꿀아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "I-꿀아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "쫀득카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "커피엔 역시 커피빵",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "커피 밀크쉐이크",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 186, "s2": None},  # 레귤러 31.4mg/100ml
        },
        {
            "name": "H-콜드브루",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": None},  # 레귤러 30.6mg/100ml
        },
        {
            "name": "I-콜드브루",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": None},  # 레귤러 30.6mg/100ml
        },
        {
            "name": "H-콜드브루라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": None},  # 레귤러 30.6mg/100ml
        },
        {
            "name": "I-콜드브루라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": None},  # 레귤러 30.6mg/100ml
        },
        {
            "name": "I-바닐라크림라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 125, "s2": None},  # 레귤러 30.1mg/100ml
        },
        {
            "name": "I-너티크림라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 124, "s2": None},  # 레귤러 29.9mg/100ml
        },
        {
            "name": "I-흑당 카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 124, "s2": None},  # 레귤러 21.0mg/100ml
        },
        {
            "name": "I-매샷추",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 124, "s2": None},  # 레귤러 21.0mg/100ml
        },
        {
            "name": "I-파인애플 커피",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 124, "s2": 186},  # 레귤러 21.0mg/100ml · 빅포즈 649ml
        },
        {
            "name": "I-흑당 버블 카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 124, "s2": None},  # 레귤러 21.0mg/100ml
        },
        {
            "name": "H-밀크티",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 124, "s2": None},  # 레귤러 20.9mg/100ml
        },
        {
            "name": "I-밀크티",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 124, "s2": None},  # 레귤러 20.9mg/100ml
        },
        {
            "name": "H-그린티라떼",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 113, "s2": None},  # 레귤러 19.1mg/100ml
        },
        {
            "name": "I-그린티라떼",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 113, "s2": None},  # 레귤러 19.1mg/100ml
        },
    ],
}