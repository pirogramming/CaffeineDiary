"""빽다방 고카페인 음료 프리셋.

출처: https://paikdabang.com/menu/menu_coffee/ ("커피" 탭)
      https://paikdabang.com/menu/menu_drink/ ("음료" 탭)
      https://paikdabang.com/menu/menu_dessert/ ("아이스크림ㆍ디저트" 탭)
      https://paikdabang.com/menu/menu_ccino/ ("빽스치노" 탭)
선정 기준: 100ml당 카페인 15mg 이상

[수집 범위] 커피 · 음료 · 아이스크림ㆍ디저트 · 빽스치노 탭 전체를 포함한다.
아이스크림 항목은 컵 단위(440ml) 제공량 기준이며 사이즈 선택지가 없다.

[사이즈] s1=기본, s2=빽사이즈(990ml). 기본 컵용량은 HOT 510ml, ICED 660ml로
메뉴명에 따라 다르므로 BAIK_SIZES의 volume_ml은 ICED 기준 대표값이다.
빽사이즈 미제공 음료는 s2가 None이고, 사이즈가 없는 더블에스프레소는
s2 키를 두지 않는다.

[표기] HOT/ICED는 사이즈가 아니라 별도 메뉴로 취급하며 원본 메뉴명을
그대로 사용한다. 두 버전의 카페인량은 서로 다르다.

[제외] 디카페인 라인업은 대부분 100ml당 3mg 미만이라 기준에 미달해 빠졌다.
단, 디카페인 카페모카 계열은 초콜릿 유래 카페인 때문에 기준을 넘어 포함됐다.
음료 탭은 원본에 카페인 항목 자체가 없는 메뉴가 30여 종 있어 판정에서 제외했다.
빽스치노의 BASIC/SOFT는 사이즈가 아니라 베이스 종류이므로 별도 메뉴로 둔다.
"""

from ..constants import DrinkType


BAIK_SIZES = [
    {"code": "s1", "label": "기본", "volume_ml": 660},
    {"code": "s2", "label": "빽사이즈", "volume_ml": 990},
]


BAIK = {
    "code": "baik",
    "name": "빽다방",
    "sizes": BAIK_SIZES,
    "drinks": [
        {
            "name": "더블에스프레소",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 269},  # 60ml · 448.3mg/100ml
        },
        {
            "name": "원조커피(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 358, "s2": None},  # 510ml · 70.1mg/100ml
        },
        {
            "name": "카페모카(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 299, "s2": None},  # 510ml · 58.6mg/100ml
        },
        {
            "name": "코코넛카페라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 243, "s2": None},  # 510ml · 47.6mg/100ml
        },
        {
            "name": "아이스크림카페모카(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 309, "s2": None},  # 660ml · 46.8mg/100ml
        },
        {
            "name": "에어폼 아메리카노(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 293, "s2": None},  # 660ml · 44.4mg/100ml
        },
        {
            "name": "원조빽스치노(SOFT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 280},  # 660ml · 42.4mg/100ml
        },
        {
            "name": "카페모카(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 270, "s2": None},  # 660ml · 40.9mg/100ml
        },
        {
            "name": "콜드브루라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 202, "s2": None},  # 510ml · 39.6mg/100ml
        },
        {
            "name": "말차빽스치노(SOFT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 260},  # 660ml · 39.4mg/100ml
        },
        {
            "name": "원조커피크림 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 257, "s2": None},  # 660ml · 39.0mg/100ml
        },
        {
            "name": "아메리카노(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 197, "s2": None},  # 510ml · 38.6mg/100ml
        },
        {
            "name": "콜드브루 연유라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 197, "s2": None},  # 510ml · 38.6mg/100ml
        },
        {
            "name": "콜드브루 흑당라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 197, "s2": None},  # 510ml · 38.6mg/100ml
        },
        {
            "name": "원조커피(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 247, "s2": 468},  # 660ml · 37.4mg/100ml
        },
        {
            "name": "헤이즐넛아메리카노(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 190, "s2": None},  # 510ml · 37.3mg/100ml
        },
        {
            "name": "달달연유라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 187, "s2": None},  # 510ml · 36.7mg/100ml
        },
        {
            "name": "헤이즐넛라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 184, "s2": None},  # 510ml · 36.1mg/100ml
        },
        {
            "name": "생크림 아메리카노(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 232, "s2": None},  # 660ml · 35.1mg/100ml
        },
        {
            "name": "생크림 카페라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 232, "s2": None},  # 660ml · 35.1mg/100ml
        },
        {
            "name": "꿀아메리카노(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 175, "s2": None},  # 510ml · 34.3mg/100ml
        },
        {
            "name": "콜드브루(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 174, "s2": None},  # 510ml · 34.1mg/100ml
        },
        {
            "name": "피스타치오 생크림 카페라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 222, "s2": None},  # 660ml · 33.6mg/100ml
        },
        {
            "name": "바닐라라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 168, "s2": None},  # 510ml · 32.9mg/100ml
        },
        {
            "name": "카라멜마키아또(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 165, "s2": None},  # 510ml · 32.4mg/100ml
        },
        {
            "name": "챔피언스 유자 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 204, "s2": None},  # 660ml · 31.0mg/100ml
        },
        {
            "name": "코코넛커피스무디",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 199, "s2": None},  # 660ml · 30.2mg/100ml
        },
        {
            "name": "밀크티(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 153, "s2": None},  # 510ml · 29.9mg/100ml
        },
        {
            "name": "카페라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 152, "s2": None},  # 510ml · 29.8mg/100ml
        },
        {
            "name": "바닐라커피 빽스치노(BASIC)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 196},  # 660ml · 29.7mg/100ml
        },
        {
            "name": "바닐라커피 빽스치노(SOFT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 196},  # 660ml · 29.7mg/100ml
        },
        {
            "name": "콜드브루 흑당라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 195, "s2": None},  # 660ml · 29.5mg/100ml
        },
        {
            "name": "챔피언스 유자셔벗 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 190, "s2": None},  # 660ml · 28.8mg/100ml
        },
        {
            "name": "콜드브루 연유라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 188, "s2": None},  # 660ml · 28.4mg/100ml
        },
        {
            "name": "콜드브루(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 178, "s2": None},  # 660ml · 26.9mg/100ml
        },
        {
            "name": "코코넛카페라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 177, "s2": None},  # 660ml · 26.8mg/100ml
        },
        {
            "name": "디카페인 카페모카(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 137, "s2": None},  # 510ml · 26.8mg/100ml
        },
        {
            "name": "아이스크림카페라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 176, "s2": None},  # 660ml · 26.7mg/100ml
        },
        {
            "name": "아이스크림바닐라라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 172, "s2": None},  # 660ml · 26.1mg/100ml
        },
        {
            "name": "카라멜마키아또(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 171, "s2": None},  # 660ml · 25.9mg/100ml
        },
        {
            "name": "콜드브루라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 171, "s2": None},  # 660ml · 25.9mg/100ml
        },
        {
            "name": "헤이즐넛라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 170, "s2": None},  # 660ml · 25.8mg/100ml
        },
        {
            "name": "말차라떼(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 130, "s2": None},  # 510ml · 25.6mg/100ml
        },
        {
            "name": "아메리카노(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 166, "s2": 293},  # 660ml · 25.2mg/100ml
        },
        {
            "name": "헤이즐넛아메리카노(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 166, "s2": None},  # 660ml · 25.2mg/100ml
        },
        {
            "name": "달달연유라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 164, "s2": None},  # 660ml · 24.8mg/100ml
        },
        {
            "name": "카페라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 163, "s2": 286},  # 660ml · 24.7mg/100ml
        },
        {
            "name": "꿀아메리카노(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 161, "s2": None},  # 660ml · 24.4mg/100ml
        },
        {
            "name": "밀크티(ICED)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 157, "s2": None},  # 660ml · 23.8mg/100ml
        },
        {
            "name": "바닐라라떼(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 156, "s2": 322},  # 660ml · 23.6mg/100ml
        },
        {
            "name": "레드불 꿀샷추(ICED)",
            "category": DrinkType.ENERGY,
            "caffeine": {"s1": 154, "s2": None},  # 660ml · 23.3mg/100ml
        },
        {
            "name": "에스프레소 소프트",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 85},  # 440ml · 19.3mg/100ml
        },
        {
            "name": "말차쿠키 소프트",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 82},  # 440ml · 18.6mg/100ml
        },
        {
            "name": "바나나 카페라떼(HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 94, "s2": None},  # 510ml · 18.4mg/100ml
        },
        {
            "name": "우롱티(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 92, "s2": None},  # 510ml · 18.0mg/100ml
        },
        {
            "name": "말차쿠키 요거트아이스크림",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 79},  # 440ml · 18.0mg/100ml
        },
        {
            "name": "원조 소프트",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 79},  # 440ml · 18.0mg/100ml
        },
        {
            "name": "디카페인 카페모카(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 118, "s2": None},  # 660ml · 17.8mg/100ml
        },
        {
            "name": "오렌지자몽블랙티(HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": None},  # 510ml · 17.6mg/100ml
        },
        {
            "name": "디카페인 아이스크림카페모카(ICED)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 114, "s2": None},  # 660ml · 17.3mg/100ml
        },
        {
            "name": "아이스티샷 망고추가(아샷망추)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106, "s2": 177},  # 660ml · 16.1mg/100ml
        },
        {
            "name": "제로슈거 납작복숭아 아.샷.추",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106, "s2": None},  # 660ml · 16.1mg/100ml
        },
        {
            "name": "말차라떼(ICED)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 104, "s2": None},  # 660ml · 15.8mg/100ml
        },
        {
            "name": "말차 소프트",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 68},  # 440ml · 15.5mg/100ml
        },
        {
            "name": "아이스티샷추가(아샷추)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 100, "s2": 179},  # 660ml · 15.2mg/100ml
        },
        {
            "name": "말차 요거트 아이스크림",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 67},  # 440ml · 15.2mg/100ml
        },
        {
            "name": "바나나 커피쉐이크",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 99, "s2": None},  # 660ml · 15.0mg/100ml
        },
    ],
}