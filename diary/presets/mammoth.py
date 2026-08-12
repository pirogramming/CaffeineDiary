"""매머드커피(매머드 익스프레스) 고카페인 음료 프리셋.

출처: https://mmthcoffee.com/sub/menu/list.html
      상세 영양정보는 /sub/menu/list_coffee_view.php?menuSeq={id} 로 별도 제공되며,
      목록 페이지에는 포함되지 않아 메뉴별로 개별 수집했다.
선정 기준: 100ml당 카페인 15mg 이상

[수집 범위] 목록에 노출된 전체 메뉴 171종을 수집했다. 이 중 카페인 항목이
있는 것은 106종이며, 나머지는 베이커리/디저트이거나 표기가 "-"였다.

[사이즈] 매머드는 메뉴별로 컵 규격이 고정되어 사이즈 선택지가 없다.
HOT은 16oz(473ml), ICE는 22oz(650ml)가 기본이며 일부 메뉴만 14oz/32oz다.
따라서 사이즈 코드는 s1 하나만 두고, 실제 용량은 각 항목 주석에 남긴다.

[표기] HOT/ICE는 컵 크기와 카페인량이 모두 달라 별도 메뉴로 취급하며,
메뉴명 뒤에 괄호로 붙인다.
"""

from ..constants import DrinkType


MAMMOTH_SIZES = [
    {"code": "s1", "label": "기본", "volume_ml": 650},
]


MAMMOTH = {
    "code": "mammoth",
    "name": "매머드커피",
    "sizes": MAMMOTH_SIZES,
    "drinks": [
        {
            "name": "베트남 연유 커피(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 426},  # 16oz 473ml · 90.0mg/100ml
        },
        {
            "name": "믹스 커피(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 369},  # 16oz 473ml · 78.0mg/100ml
        },
        {
            "name": "베트남 연유 커피(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 426},  # 22oz 650ml · 65.5mg/100ml
        },
        {
            "name": "아인슈페너 커피(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 14oz 414ml · 64.2mg/100ml
        },
        {
            "name": "아인슈페너 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 14oz 414ml · 64.2mg/100ml
        },
        {
            "name": "바닐라 크럼블 아이스크림 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 14oz 414ml · 64.2mg/100ml
        },
        {
            "name": "믹스 커피(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 369},  # 22oz 650ml · 56.8mg/100ml
        },
        {
            "name": "헤이즐넛 커피(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 268},  # 16oz 473ml · 56.6mg/100ml
        },
        {
            "name": "헤이즐넛 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 268},  # 16oz 473ml · 56.6mg/100ml
        },
        {
            "name": "헤이즐넛 모카(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 267},  # 16oz 473ml · 56.5mg/100ml
        },
        {
            "name": "아메리카노(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "꿀 커피(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "카페 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "꿀 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "바닐라 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "아몬드 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "골든 코코넛 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "시그니처 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "카페 모카(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "솔티드 카라멜 마키아토(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 16oz 473ml · 56.2mg/100ml
        },
        {
            "name": "말차 클래식 프라페(ICE)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 278},  # 22oz 650ml · 42.8mg/100ml
        },
        {
            "name": "헤이즐넛 커피(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 268},  # 22oz 650ml · 41.2mg/100ml
        },
        {
            "name": "헤이즐넛 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 268},  # 22oz 650ml · 41.2mg/100ml
        },
        {
            "name": "헤이즐넛 모카(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 267},  # 22oz 650ml · 41.1mg/100ml
        },
        {
            "name": "아메리카노(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "꿀 커피(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "카페 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "꿀 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "바닐라 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "아몬드 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "골든 코코넛 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "시그니처 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "카페 모카(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "솔티드 카라멜 마키아토(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 266},  # 22oz 650ml · 40.9mg/100ml
        },
        {
            "name": "말차 클래식 라떼(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 185},  # 16oz 473ml · 39.2mg/100ml
        },
        {
            "name": "콜드브루 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 155},  # 16oz 473ml · 32.7mg/100ml
        },
        {
            "name": "돌체 콜드브루 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 155},  # 16oz 473ml · 32.7mg/100ml
        },
        {
            "name": "로얄 밀크티(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 148},  # 16oz 473ml · 31.3mg/100ml
        },
        {
            "name": "레몬&오렌지(홍차)티(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 145},  # 16oz 473ml · 30.7mg/100ml
        },
        {
            "name": "말차 클래식 라떼(ICE)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 185},  # 22oz 650ml · 28.5mg/100ml
        },
        {
            "name": "아샷추 복숭아 아이스티(ICE)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 170},  # 22oz 650ml · 26.2mg/100ml
        },
        {
            "name": "샷추가 파인애플 주스(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 160},  # 22oz 650ml · 24.6mg/100ml
        },
        {
            "name": "콜드브루(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 116},  # 16oz 473ml · 24.5mg/100ml
        },
        {
            "name": "콜드브루 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 155},  # 22oz 650ml · 23.8mg/100ml
        },
        {
            "name": "돌체 콜드브루 라떼(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 155},  # 22oz 650ml · 23.8mg/100ml
        },
        {
            "name": "로얄 밀크티(ICE)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 148},  # 22oz 650ml · 22.8mg/100ml
        },
        {
            "name": "얼그레이티(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 93},  # 16oz 473ml · 19.6mg/100ml
        },
        {
            "name": "콜드브루(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 116},  # 22oz 650ml · 17.8mg/100ml
        },
        {
            "name": "레몬 토닉 콜드브루(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 116},  # 22oz 650ml · 17.8mg/100ml
        },
        {
            "name": "달고나 콜드브루 라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 77},  # 16oz 473ml · 16.3mg/100ml
        },
        {
            "name": "자바칩 프라페(ICE)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 104},  # 22oz 650ml · 16.0mg/100ml
        },
    ],
}
