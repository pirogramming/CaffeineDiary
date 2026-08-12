"""공차 고카페인 음료 프리셋.

출처: https://www.gong-cha.co.kr/brand/menu/product ("영양정보 전체보기" 탭)
선정 기준: 100ml당 카페인 15mg 이상 (사이즈별 농도 중 최댓값 기준)

[수집 범위] 영양정보 표에 실린 전 메뉴를 수집했다. 카테고리별 표에 같은
메뉴가 중복 등장하는 경우가 있어 (메뉴명, 구분, 사이즈, 용량)으로 중복 제거했다.

[사이즈] s1=L, s2=J(점보). 컵용량은 구분에 따라 다르다.
  COLD: L 473ml / J 651ml
  HOT : L 414ml / J 473ml
GONGCHA_SIZES의 volume_ml은 COLD 기준 대표값이므로 HOT 메뉴와는 어긋난다.

[표기] HOT/COLD는 사이즈가 아니라 별도 메뉴로 취급하며 메뉴명 뒤에 붙인다.
두 버전의 카페인량은 서로 다르다.

[주의] 원본 각주에 따르면 기본 레시피(당도 0%) 및 표준 컵 사이즈 기준이며,
커스터마이징이나 매장 상황에 따라 실제 값은 달라질 수 있다.
"""

from ..constants import DrinkType


GONGCHA_SIZES = [
    {"code": "s1", "label": "L", "volume_ml": 473},
    {"code": "s2", "label": "J", "volume_ml": 651},
]


GONGCHA = {
    "code": "gongcha",
    "name": "공차",
    "sizes": GONGCHA_SIZES,
    "drinks": [
        {
            "name": "아메리카노 (DRIP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 273, "s2": 364},  # 최대 77.0mg/100ml
        },
        {
            "name": "얼그레이 아메리카노 (DRIP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 239, "s2": 313},  # 최대 66.2mg/100ml
        },
        {
            "name": "아메리카노 (DRIP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 273, "s2": 364},  # 최대 57.7mg/100ml
        },
        {
            "name": "공차슈페너 (DRIP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 250, "s2": None},  # 최대 52.9mg/100ml
        },
        {
            "name": "얼그레이 아메리카노 (DRIP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 239, "s2": 313},  # 최대 50.5mg/100ml
        },
        {
            "name": "얼그레이 아메리카노 (ESP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 168, "s2": 230},  # 최대 48.6mg/100ml
        },
        {
            "name": "저당 얼그레이 오리지널 티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 175, "s2": 224},  # 최대 47.4mg/100ml
        },
        {
            "name": "브라운슈가 시그니처 얼그레이 밀크티 + 펄 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 195, "s2": 224},  # 최대 47.4mg/100ml
        },
        {
            "name": "얼그레이티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 175, "s2": 224},  # 최대 47.4mg/100ml
        },
        {
            "name": "더블 말차 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 201, "s2": None},  # 최대 42.5mg/100ml
        },
        {
            "name": "더블 말차 밀크티 + 펄 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 174, "s2": None},  # 최대 42.0mg/100ml
        },
        {
            "name": "더블 말차 밀크티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 174, "s2": None},  # 최대 42.0mg/100ml
        },
        {
            "name": "납작복숭아 아이스티 얼그레이 + 샷 (DRIP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": None, "s2": 268},  # 최대 41.2mg/100ml
        },
        {
            "name": "카페 모카 (DRIP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 152, "s2": 190},  # 최대 40.2mg/100ml
        },
        {
            "name": "얼그레이 말차 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 186, "s2": None},  # 최대 39.3mg/100ml
        },
        {
            "name": "납작복숭아 아이스티 얼그레이 + 샷 (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": None, "s2": 251},  # 최대 38.6mg/100ml
        },
        {
            "name": "바닐라 카페라떼 (DRIP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 145, "s2": 182},  # 최대 38.5mg/100ml
        },
        {
            "name": "카페 모카 (ESP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 135, "s2": 180},  # 최대 38.1mg/100ml
        },
        {
            "name": "공차슈페너 (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 178, "s2": None},  # 최대 37.6mg/100ml
        },
        {
            "name": "저당 얼그레이 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 175, "s2": 243},  # 최대 37.3mg/100ml
        },
        {
            "name": "포도 말랑 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 175, "s2": None},  # 최대 37.0mg/100ml
        },
        {
            "name": "저당 얼그레이 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 175, "s2": None},  # 최대 37.0mg/100ml
        },
        {
            "name": "얼그레이 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 175, "s2": 224},  # 최대 37.0mg/100ml
        },
        {
            "name": "더블 말차 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 174, "s2": None},  # 최대 36.8mg/100ml
        },
        {
            "name": "아메리카노 (ESP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 129, "s2": 171},  # 최대 36.2mg/100ml
        },
        {
            "name": "바닐라 카페라떼 (ESP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 129, "s2": 171},  # 최대 36.2mg/100ml
        },
        {
            "name": "카페라떼 (ESP) (HOT)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 129, "s2": 171},  # 최대 36.2mg/100ml
        },
        {
            "name": "얼그레이 아메리카노 (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 168, "s2": 230},  # 최대 35.5mg/100ml
        },
        {
            "name": "얼그레이 밀크티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 146, "s2": 165},  # 최대 35.3mg/100ml
        },
        {
            "name": "저당 블랙 오리지널 티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 128, "s2": 163},  # 최대 34.5mg/100ml
        },
        {
            "name": "말차샷 타로 밀크티 (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 163, "s2": None},  # 최대 34.5mg/100ml
        },
        {
            "name": "브라운슈가 시그니처 밀크티 +펄 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 142, "s2": 163},  # 최대 34.5mg/100ml
        },
        {
            "name": "블랙티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 128, "s2": 163},  # 최대 34.5mg/100ml
        },
        {
            "name": "카페 스무디 with 블랙티 (공차치노) (DRIP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 160, "s2": None},  # 최대 33.8mg/100ml
        },
        {
            "name": "카페 모카 (DRIP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 152, "s2": 190},  # 최대 32.1mg/100ml
        },
        {
            "name": "저당 얼그레이 오리지널 티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 146, "s2": 195},  # 최대 30.9mg/100ml
        },
        {
            "name": "딸기 쥬얼리 시그니처 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 146, "s2": None},  # 최대 30.9mg/100ml
        },
        {
            "name": "허니 자몽 블랙티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 128, "s2": 142},  # 최대 30.9mg/100ml
        },
        {
            "name": "얼그레이티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 146, "s2": 195},  # 최대 30.9mg/100ml
        },
        {
            "name": "바닐라 카페라떼 (DRIP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 145, "s2": 182},  # 최대 30.7mg/100ml
        },
        {
            "name": "카페 스무디 with 블랙티 (공차치노) (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 143, "s2": None},  # 최대 30.2mg/100ml
        },
        {
            "name": "브라운슈가 시그니처 얼그레이 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 126, "s2": 195},  # 최대 30.0mg/100ml
        },
        {
            "name": "카페 모카 (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 135, "s2": 180},  # 최대 28.5mg/100ml
        },
        {
            "name": "아메리카노 (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 129, "s2": 171},  # 최대 27.3mg/100ml
        },
        {
            "name": "바닐라 카페라떼 (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 129, "s2": 171},  # 최대 27.3mg/100ml
        },
        {
            "name": "카페라떼 (ESP) (COLD)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 129, "s2": 171},  # 최대 27.3mg/100ml
        },
        {
            "name": "저당 블랙 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 128, "s2": 177},  # 최대 27.2mg/100ml
        },
        {
            "name": "저당 블랙 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 128, "s2": None},  # 최대 27.1mg/100ml
        },
        {
            "name": "블랙 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 128, "s2": 163},  # 최대 27.1mg/100ml
        },
        {
            "name": "블랙 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 128, "s2": 163},  # 최대 27.1mg/100ml
        },
        {
            "name": "블랙 밀크티 + 펄 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106, "s2": 121},  # 최대 25.6mg/100ml
        },
        {
            "name": "블랙 밀크티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106, "s2": 121},  # 최대 25.6mg/100ml
        },
        {
            "name": "우롱티 + 코코넛 + 밀크폼 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 95, "s2": 120},  # 최대 25.4mg/100ml
        },
        {
            "name": "자스민 코코 with 말차폼 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 115, "s2": None},  # 최대 24.3mg/100ml
        },
        {
            "name": "저당 자스민 오리지널 티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": 114},  # 최대 24.1mg/100ml
        },
        {
            "name": "자스민티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": 114},  # 최대 24.1mg/100ml
        },
        {
            "name": "초코바른 제주 그린 스무디 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 112, "s2": None},  # 최대 23.7mg/100ml
        },
        {
            "name": "제주 그린 스무디 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 109, "s2": None},  # 최대 23.0mg/100ml
        },
        {
            "name": "저당 블랙 오리지널 티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106, "s2": 142},  # 최대 22.4mg/100ml
        },
        {
            "name": "허니 자몽 블랙티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106, "s2": 142},  # 최대 22.4mg/100ml
        },
        {
            "name": "블랙티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106, "s2": 142},  # 최대 22.4mg/100ml
        },
        {
            "name": "브라운슈가 시그니처 밀크티 +펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 92, "s2": 142},  # 최대 21.8mg/100ml
        },
        {
            "name": "브라운슈가 시그니처 밀크티 +미니펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 92, "s2": 142},  # 최대 21.8mg/100ml
        },
        {
            "name": "레몬 자스민티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": 100},  # 최대 21.7mg/100ml
        },
        {
            "name": "자몽 자스민티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": 100},  # 최대 21.7mg/100ml
        },
        {
            "name": "청포도 자스민티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": 100},  # 최대 21.7mg/100ml
        },
        {
            "name": "저당 우롱 오리지널 티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": 99},  # 최대 20.9mg/100ml
        },
        {
            "name": "브라운슈가 시그니처 우롱 밀크티 + 펄 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 86, "s2": 99},  # 최대 20.9mg/100ml
        },
        {
            "name": "우롱티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": 99},  # 최대 20.9mg/100ml
        },
        {
            "name": "저당 자스민 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": 124},  # 최대 19.0mg/100ml
        },
        {
            "name": "저당 자스민 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": None},  # 최대 19.0mg/100ml
        },
        {
            "name": "자스민 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 90, "s2": 114},  # 최대 19.0mg/100ml
        },
        {
            "name": "말차 초코 스무디 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 89, "s2": None},  # 최대 18.8mg/100ml
        },
        {
            "name": "납작복숭아 아이스티 얼그레이 + 미니펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": None, "s2": 122},  # 최대 18.7mg/100ml
        },
        {
            "name": "밀크티 모찌 빙수 쉐이크 + 소프트 아이스크림 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 87, "s2": None},  # 최대 18.4mg/100ml
        },
        {
            "name": "자스민 밀크티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 75, "s2": 85},  # 최대 18.1mg/100ml
        },
        {
            "name": "제주 그린 밀크티 + 펄 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 54, "s2": 81},  # 최대 17.1mg/100ml
        },
        {
            "name": "말차 쥬얼리 시그니처 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 80, "s2": None},  # 최대 16.9mg/100ml
        },
        {
            "name": "저당 우롱 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": 107},  # 최대 16.4mg/100ml
        },
        {
            "name": "저당 햅쌀 미숫가루 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": None},  # 최대 16.3mg/100ml
        },
        {
            "name": "저당 우롱 밀크티 + 펄 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": None},  # 최대 16.3mg/100ml
        },
        {
            "name": "우롱 밀크티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 77, "s2": 99},  # 최대 16.3mg/100ml
        },
        {
            "name": "저당 자스민 오리지널 티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 75, "s2": 100},  # 최대 15.9mg/100ml
        },
        {
            "name": "레몬 자스민티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 75, "s2": 100},  # 최대 15.9mg/100ml
        },
        {
            "name": "자몽 자스민티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 75, "s2": 100},  # 최대 15.9mg/100ml
        },
        {
            "name": "청포도 자스민티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 75, "s2": 100},  # 최대 15.9mg/100ml
        },
        {
            "name": "자스민티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 75, "s2": 100},  # 최대 15.9mg/100ml
        },
        {
            "name": "우롱 밀크티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 64, "s2": 73},  # 최대 15.5mg/100ml
        },
        {
            "name": "트로피컬 블러쉬 아이스티 (COLD)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": None, "s2": 100},  # 최대 15.4mg/100ml
        },
        {
            "name": "제주 그린 밀크티 (HOT)",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 62, "s2": 71},  # 최대 15.0mg/100ml
        },
    ],
}
