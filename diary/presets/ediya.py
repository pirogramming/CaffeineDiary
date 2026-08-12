"""이디야커피 고카페인 음료 프리셋.

출처: https://www.ediya.com/contents/drink.html
      목록 페이지에 각 메뉴의 영양정보가 인라인으로 포함되어 있어 그대로 파싱했다.
선정 기준: 100ml당 카페인 15mg 이상 (사이즈별 농도 중 최댓값 기준)

[수집 범위] 전체 386종을 수집했다. 모든 항목에 카페인 값이 있으나,
컵용량이 없는 49종은 농도를 계산할 수 없어 판정에서 제외됐다.

[사이즈] 메뉴명 접두 (L)=520ml, (EX)=650~670ml가 사이즈에 해당하므로
s1/s2로 병합했다. 접두가 없는 품목(빙수, 병음료, 아이스크림, 에스프레소 등)은
사이즈 선택지가 없어 s1 키만 둔다.

[표기] HOT/ICED는 사이즈가 아니라 별도 메뉴이므로 이름에 그대로 남긴다.
같은 음료라도 두 버전의 카페인량이 다를 수 있다.

[중복] 원본에는 이름이 동일한 블록이 두 개씩 존재하며(일반/디카페인)
제목만으로는 구분되지 않는다. 값이 큰 쪽을 일반 메뉴로 보고 채택했다.
따라서 이 파일에 디카페인 항목은 포함되지 않는다.
"""

from ..constants import DrinkType


EDIYA_SIZES = [
    {"code": "s1", "label": "L",  "volume_ml": 520},
    {"code": "s2", "label": "EX", "volume_ml": 670},
]


EDIYA = {
    "code": "ediya",
    "name": "이디야커피",
    "sizes": EDIYA_SIZES,
    "drinks": [
        {
            "name": "HOT 카페 모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 245, "s2": 368},  # 최대 56.6mg/100ml
        },
        {
            "name": "ICED 카페 모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 245, "s2": 368},  # 최대 54.9mg/100ml
        },
        {
            "name": "얼박사 젤리 플랫치노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 264, "s2": 352},  # 최대 52.5mg/100ml
        },
        {
            "name": "얼박샷추",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 261, "s2": 341},  # 최대 50.9mg/100ml
        },
        {
            "name": "HOT 민트 모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 207, "s2": 311},  # 최대 47.8mg/100ml
        },
        {
            "name": "HOT 시그니처 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 헤이즐넛 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 에스프레소 코코넛",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 카페 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 카라멜 마끼아또",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 연유 카페 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 바닐라 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 화이트 초콜릿 모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 카페 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "HOT 카푸치노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 46.6mg/100ml
        },
        {
            "name": "ICED 민트 모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 207, "s2": 311},  # 최대 46.4mg/100ml
        },
        {
            "name": "ICED 넛츠 크림 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 207, "s2": 310},  # 최대 46.3mg/100ml
        },
        {
            "name": "ICED 헤이즐넛 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 시그니처 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "에스프레소 쉐이크",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 에스프레소 코코넛",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 연유 카페 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 카라멜 마끼아또",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 꿀화이트 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 바닐라 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 화이트 초콜릿 모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 카페 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 카페 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "ICED 카푸치노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": 303},  # 최대 45.2mg/100ml
        },
        {
            "name": "흑당 콜드브루",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": 272},  # 최대 40.6mg/100ml
        },
        {
            "name": "콜드브루",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": 272},  # 최대 40.6mg/100ml
        },
        {
            "name": "연유 콜드브루",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": 272},  # 최대 40.6mg/100ml
        },
        {
            "name": "콜드브루 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181, "s2": 272},  # 최대 40.6mg/100ml
        },
        {
            "name": "얼박사 코코 에이드",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 176, "s2": 264},  # 최대 39.4mg/100ml
        },
        {
            "name": "아이스크림 카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": None},  # 최대 38.8mg/100ml
        },
        {
            "name": "얼박샷추(디카페인 원두)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 163, "s2": 243},  # 최대 36.3mg/100ml
        },
        {
            "name": "HOT 로열 밀크티",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 119, "s2": 178},  # 최대 27.4mg/100ml
        },
        {
            "name": "ICED 로열 밀크티",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 119, "s2": 178},  # 최대 26.6mg/100ml
        },
        {
            "name": "HOT 달달커피",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 108, "s2": 162},  # 최대 24.9mg/100ml
        },
        {
            "name": "ICED 제로슈가 아샷추 복숭아",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 129, "s2": 143},  # 최대 24.8mg/100ml
        },
        {
            "name": "ICED 달달커피",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 108, "s2": 162},  # 최대 24.2mg/100ml
        },
        {
            "name": "아샷추 복숭아",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 124, "s2": 109},  # 최대 23.8mg/100ml
        },
        {
            "name": "ICED 말차초코라떼",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 98, "s2": 158},  # 최대 23.6mg/100ml
        },
        {
            "name": "초콜릿 칩 플랫치노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 99, "s2": 143},  # 최대 21.3mg/100ml
        },
        {
            "name": "HOT 말차라떼",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": 115},  # 최대 17.7mg/100ml
        },
        {
            "name": "말차 초코 쉐이크",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 79, "s2": 117},  # 최대 17.5mg/100ml
        },
        {
            "name": "ICED 말차라떼",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": 115},  # 최대 17.2mg/100ml
        },
    ],
}
