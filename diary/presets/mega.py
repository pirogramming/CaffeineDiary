"""메가엠지씨커피(메가커피) 고카페인 음료 프리셋.

출처: 메가엠지씨커피 공식 영양성분표 (이미지)

[선정 기준] 다른 브랜드와 달리 100ml당 농도가 아니라 브랜드가 직접 표시한
고카페인 여부를 따랐다. 메가커피 영양성분표에는 컵용량 컬럼이 없어 농도를
계산할 수 없는 대신, 표 각주에 "노란색 박스로 표기된 메뉴는 다량의 카페인을
함유한다"는 안내가 있어 해당 하이라이트 행 45종을 그대로 채택했다.
제조사 자체 판정이므로 근거로서는 오히려 더 명확하다.

[사이즈] 컵용량 정보가 없고 HOT/ICE·왕메가·할메가 등 규격 차이가 메뉴명에
포함되어 있어, 사이즈 코드는 s1 하나만 둔다.

[주의] 카페인량은 표준 레시피 기준이며 샷 추가 등 옵션 변경 시 달라진다.
디카페인 라인업은 하이라이트가 없어 포함되지 않았다.
"""

from ..constants import DrinkType


MEGA_SIZES = [
    {"code": "s1", "label": "기본"},
]


MEGA = {
    "code": "mega",
    "name": "메가엠지씨커피",
    "sizes": MEGA_SIZES,
    "drinks": [
        {
            "name": "왕메가카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 347},  # 표기값 347.1mg
        },
        {
            "name": "ICE 큐브라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 313},  # 표기값 313.4mg
        },
        {
            "name": "메가리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 291},  # 표기값 290.8mg
        },
        {
            "name": "왕메가 헛개리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 235},  # 표기값 234.6mg
        },
        {
            "name": "카페모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 233},  # 표기값 233.2mg
        },
        {
            "name": "ICE 카페모카",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 232},  # 표기값 232.5mg
        },
        {
            "name": "바닐라 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 221},  # 표기값 220.7mg
        },
        {
            "name": "HOT 콜드브루",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 217},  # 표기값 217.0mg
        },
        {
            "name": "ICE 헤이즐넛라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 217},  # 표기값 216.9mg
        },
        {
            "name": "HOT 콜드브루라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 217},  # 표기값 216.7mg
        },
        {
            "name": "ICE 바닐라 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 212},  # 표기값 211.5mg
        },
        {
            "name": "헤이즐넛 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 210},  # 표기값 209.8mg
        },
        {
            "name": "라이트 바닐라 아몬드라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 206},  # 표기값 206.2mg
        },
        {
            "name": "헤이즐넛 라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 205},  # 표기값 204.6mg
        },
        {
            "name": "아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 204},  # 표기값 204.2mg
        },
        {
            "name": "카라멜마끼아또",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 203},  # 표기값 203.4mg
        },
        {
            "name": "카푸치노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 201},  # 표기값 201.4mg
        },
        {
            "name": "ICE 카라멜마끼아또",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 200},  # 표기값 200.0mg
        },
        {
            "name": "ICE 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 200},  # 표기값 199.7mg
        },
        {
            "name": "꿀아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 199},  # 표기값 199.4mg
        },
        {
            "name": "ICE 카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 199},  # 표기값 199.1mg
        },
        {
            "name": "ICE 꿀아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 199},  # 표기값 198.6mg
        },
        {
            "name": "ICE 헤이즐넛 아메리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 197},  # 표기값 196.7mg
        },
        {
            "name": "왕할메가커피(32oz)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 196},  # 표기값 196.4mg
        },
        {
            "name": "ICE 바닐라라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 195},  # 표기값 195.1mg
        },
        {
            "name": "연유라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 194},  # 표기값 194.2mg
        },
        {
            "name": "ICE 카푸치노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 192},  # 표기값 192.3mg
        },
        {
            "name": "카페라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 190},  # 표기값 189.9mg
        },
        {
            "name": "바닐라라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 190},  # 표기값 189.9mg
        },
        {
            "name": "에스프레소도피오",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 185},  # 표기값 184.7mg
        },
        {
            "name": "HOT 헛개리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 182},  # 표기값 181.6mg
        },
        {
            "name": "ICE 헛개리카노",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 181},  # 표기값 181.2mg
        },
        {
            "name": "할메가 미숫커피",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 180},  # 표기값 180.1mg
        },
        {
            "name": "코코넛 커피 스무디",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 174},  # 표기값 173.8mg
        },
        {
            "name": "ICE연유라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 166},  # 표기값 165.9mg
        },
        {
            "name": "커피프라페",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 163},  # 표기값 162.6mg
        },
        {
            "name": "ICE 콜드브루",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 156},  # 표기값 156.4mg
        },
        {
            "name": "초코젤라또 말차라떼",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 154},  # 표기값 153.8mg
        },
        {
            "name": "ICE 콜드브루라떼",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 132},  # 표기값 131.7mg
        },
        {
            "name": "ICE 로얄밀크티",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 118},  # 표기값 118.1mg
        },
        {
            "name": "녹차프라페",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 110},  # 표기값 110.1mg
        },
        {
            "name": "로얄밀크티",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 106},  # 표기값 106.2mg
        },
        {
            "name": "에스프레소",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 105},  # 표기값 104.8mg
        },
        {
            "name": "할메가커피(20oz)",
            "category": DrinkType.COFFEE,
            "caffeine": {"s1": 100},  # 표기값 99.6mg
        },
        {
            "name": "얼그레이",
            "category": DrinkType.TEA,
            "caffeine": {"s1": 73},  # 표기값 73.4mg
        },
    ],
}
