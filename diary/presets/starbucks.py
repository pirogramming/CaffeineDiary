"""스타벅스 코리아 고카페인 음료 프리셋.

출처: https://www.starbucks.co.kr/menu/drink_list.do (영양정보 탭)
선정 기준: 100ml당 카페인 15mg 이상 (Tall 355ml 환산)

공식 영양정보는 Tall 단일 기준으로만 공개되므로 s2 값만 채워져 있다.
나머지 사이즈는 별도 자료로 확인해 직접 채울 것. None은 미확인 상태를 뜻한다.
"""

from django.db import models


class DrinkCategory(models.TextChoices):
    COFFEE = "coffee", "커피"
    TEA = "tea", "차"
    ENERGY = "energy", "에너지드링크"
    SODA = "soda", "탄산"


# 사이즈 코드는 브랜드 무관 서수(s1~s3), label만 브랜드별로 다르게 부여
STARBUCKS_SIZES = [
    {"code": "s1", "label": "Tall",   "volume_ml": 355},
    {"code": "s2", "label": "Grande", "volume_ml": 473},
    {"code": "s3", "label": "Venti",  "volume_ml": 591},
]


STARBUCKS = {
    "code": "starbucks",
    "name": "스타벅스",
    "sizes": STARBUCKS_SIZES,
    "drinks": [
        # ── 콜드 브루 커피 (21종) ────────────────────────────────
        {
            "name": "시그니처 더 블랙 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 680, "s2": None, "s3": None},  # Tall 191.5mg/100ml
        },
        {
            "name": "민트 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 415, "s2": None, "s3": None},  # Tall 116.9mg/100ml
        },
        {
            "name": "제주 비자림 리저브 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 250, "s2": None, "s3": None},  # Tall 70.4mg/100ml
        },
        {
            "name": "나이트로 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 245, "s2": None, "s3": None},  # Tall 69.0mg/100ml
        },
        {
            "name": "나이트로 바닐라 크림",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 232, "s2": None, "s3": None},  # Tall 65.4mg/100ml
        },
        {
            "name": "리저브 나이트로",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 190, "s2": None, "s3": None},  # Tall 53.5mg/100ml
        },
        {
            "name": "리저브 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 190, "s2": None, "s3": None},  # Tall 53.5mg/100ml
        },
        {
            "name": "블랙&화이트 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 190, "s2": None, "s3": None},  # Tall 53.5mg/100ml
        },
        {
            "name": "콜드 브루 몰트",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 190, "s2": None, "s3": None},  # Tall 53.5mg/100ml
        },
        {
            "name": "콜드 브루 플로트",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 190, "s2": None, "s3": None},  # Tall 53.5mg/100ml
        },
        {
            "name": "콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 155, "s2": None, "s3": None},  # Tall 43.7mg/100ml
        },
        {
            "name": "바닐라 크림 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 135, "s2": None, "s3": None},  # Tall 38.0mg/100ml
        },
        {
            "name": "스모크드 콜드 패션드",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 135, "s2": None, "s3": None},  # Tall 38.0mg/100ml
        },
        {
            "name": "바닐라 아인슈페너 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 134, "s2": None, "s3": None},  # Tall 37.7mg/100ml
        },
        {
            "name": "돌체 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 130, "s2": None, "s3": None},  # Tall 36.6mg/100ml
        },
        {
            "name": "베르가못 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 130, "s2": None, "s3": None},  # Tall 36.6mg/100ml
        },
        {
            "name": "씨솔트 카라멜 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 114, "s2": None, "s3": None},  # Tall 32.1mg/100ml
        },
        {
            "name": "서울 막걸리향 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 79, "s2": None, "s3": None},  # Tall 22.3mg/100ml
        },
        {
            "name": "코코 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 65, "s2": None, "s3": None},  # Tall 18.3mg/100ml
        },
        {
            "name": "오트 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 65, "s2": None, "s3": None},  # Tall 18.3mg/100ml
        },
        {
            "name": "프렌치 바닐라 콜드 브루",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 65, "s2": None, "s3": None},  # Tall 18.3mg/100ml
        },

        # ── 브루드 커피 (3종) ──────────────────────────────────
        {
            "name": "브루드 커피",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 260, "s2": None, "s3": None},  # Tall 73.2mg/100ml
        },
        {
            "name": "아이스 브루드 커피",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 140, "s2": None, "s3": None},  # Tall 39.4mg/100ml
        },
        {
            "name": "스위트 밀크 커피",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 60, "s2": None, "s3": None},  # Tall 16.9mg/100ml
        },

        # ── 에스프레소 (52종) ───────────────────────────────────
        {
            "name": "사케라또 비안코 오버 아이스",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 315, "s2": None, "s3": None},  # Tall 88.7mg/100ml
        },
        {
            "name": "코르타도",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 225, "s2": None, "s3": None},  # Tall 63.4mg/100ml
        },
        {
            "name": "스타벅스 1호점 카페 아메리카노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "아이스 스타벅스 1호점 카페 아메리카노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "바닐라 빈 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "번트 카라멜 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "스타벅스 1호점 카페 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "스타벅스 1호점 크림 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "아이스 바닐라 빈 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "아이스 스타벅스 1호점 카페 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "아이스 스타벅스 1호점 크림 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "제주 비자림 리저브 에스프레소 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "클래식 민트 모카",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "사케라또 아포가토",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "클래식 아포가토",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 210, "s2": None, "s3": None},  # Tall 59.2mg/100ml
        },
        {
            "name": "스타벅스 에어로카노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "스타벅스 자몽 허니 에어로카노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "아이스 카페 아메리카노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "카페 아메리카노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "스타벅스 돌체 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "아이스 스타벅스 돌체 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "바닐라 스타벅스 더블 샷",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "커피 스타벅스 더블 샷",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "헤이즐넛 스타벅스 더블 샷",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 150, "s2": None, "s3": None},  # Tall 42.3mg/100ml
        },
        {
            "name": "아이스 플랫 화이트",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 130, "s2": None, "s3": None},  # Tall 36.6mg/100ml
        },
        {
            "name": "플랫 화이트",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 130, "s2": None, "s3": None},  # Tall 36.6mg/100ml
        },
        {
            "name": "아이스 우베 코코넛 마키아또",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 105, "s2": None, "s3": None},  # Tall 29.6mg/100ml
        },
        {
            "name": "라벤더 카페 브레베",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 105, "s2": None, "s3": None},  # Tall 29.6mg/100ml
        },
        {
            "name": "아이스 라벤더 카페 브레베",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 105, "s2": None, "s3": None},  # Tall 29.6mg/100ml
        },
        {
            "name": "스파클링 시트러스 에스프레소",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 105, "s2": None, "s3": None},  # Tall 29.6mg/100ml
        },
        {
            "name": "아이스 카페 모카",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 95, "s2": None, "s3": None},  # Tall 26.8mg/100ml
        },
        {
            "name": "카페 모카",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 95, "s2": None, "s3": None},  # Tall 26.8mg/100ml
        },
        {
            "name": "피넛 크림 쿠키 아인슈페너",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "에스프레소 콘 파나",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "에스프레소 마키아또",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 카라멜 마키아또",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "카라멜 마키아또",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 카푸치노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "카푸치노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "밀크카라멜 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "바닐라 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "스타벅스 꿀 호떡 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 밀크카라멜 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 바닐라 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 스타벅스 꿀 호떡 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 인절미 크림 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 카페 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "인절미 크림 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "카페 라떼",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 화이트 초콜릿 모카",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "화이트 초콜릿 모카",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "에스프레소",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },

        # ── 프라푸치노 (6종) ───────────────────────────────────
        {
            "name": "더블 에스프레소 칩 프라푸치노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 130, "s2": None, "s3": None},  # Tall 36.6mg/100ml
        },
        {
            "name": "에스프레소 프라푸치노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 120, "s2": None, "s3": None},  # Tall 33.8mg/100ml
        },
        {
            "name": "자바 칩 프라푸치노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 100, "s2": None, "s3": None},  # Tall 28.2mg/100ml
        },
        {
            "name": "카라멜 프라푸치노",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 85, "s2": None, "s3": None},  # Tall 23.9mg/100ml
        },
        {
            "name": "제주 말차 크림 프라푸치노",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 80, "s2": None, "s3": None},  # Tall 22.5mg/100ml
        },
        {
            "name": "레드빈 말차 코코 프라푸치노",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 60, "s2": None, "s3": None},  # Tall 16.9mg/100ml
        },

        # ── 블렌디드 (3종) ────────────────────────────────────
        {
            "name": "블랙 글레이즈드 셔벗 플레이트",
            "category": DrinkCategory.COFFEE,
            "caffeine": {"s1": 159, "s2": None, "s3": None},  # Tall 44.8mg/100ml
        },
        {
            "name": "말차 폭포 유자 블렌디드",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 65, "s2": None, "s3": None},  # Tall 18.3mg/100ml
        },
        {
            "name": "스타벅스 클래식 밀크티 블렌디드",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 60, "s2": None, "s3": None},  # Tall 16.9mg/100ml
        },

        # ── 티(티바나) (16종) ──────────────────────────────────
        {
            "name": "스타벅스 클래식 밀크 티 보틀",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 195, "s2": None, "s3": None},  # Tall 54.9mg/100ml
        },
        {
            "name": "스타벅스 클래식 밀크 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 190, "s2": None, "s3": None},  # Tall 53.5mg/100ml
        },
        {
            "name": "얼 그레이 바닐라 티 라떼",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 90, "s2": None, "s3": None},  # Tall 25.4mg/100ml
        },
        {
            "name": "씨솔트 폼 블랙 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 80, "s2": None, "s3": None},  # Tall 22.5mg/100ml
        },
        {
            "name": "아이스 스타벅스 클래식 밀크 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 80, "s2": None, "s3": None},  # Tall 22.5mg/100ml
        },
        {
            "name": "아이스 제주 말차 라떼",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 80, "s2": None, "s3": None},  # Tall 22.5mg/100ml
        },
        {
            "name": "제주 말차 라떼",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 80, "s2": None, "s3": None},  # Tall 22.5mg/100ml
        },
        {
            "name": "말차 티라미수 라떼",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "아이스 말차 티라미수 라떼",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 75, "s2": None, "s3": None},  # Tall 21.1mg/100ml
        },
        {
            "name": "살구 조이풀 메들리 쉐이큰 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 70, "s2": None, "s3": None},  # Tall 19.7mg/100ml
        },
        {
            "name": "얼 그레이 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 70, "s2": None, "s3": None},  # Tall 19.7mg/100ml
        },
        {
            "name": "잉글리쉬 브렉퍼스트 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 70, "s2": None, "s3": None},  # Tall 19.7mg/100ml
        },
        {
            "name": "자몽 허니 블랙 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 70, "s2": None, "s3": None},  # Tall 19.7mg/100ml
        },
        {
            "name": "제주팔삭 & 자몽 허니 블랙 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 70, "s2": None, "s3": None},  # Tall 19.7mg/100ml
        },
        {
            "name": "복숭아 핫 티",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 70, "s2": None, "s3": None},  # Tall 19.7mg/100ml
        },
        {
            "name": "의암호의 보랏빛 라벤더 티 라떼",
            "category": DrinkCategory.TEA,
            "caffeine": {"s1": 70, "s2": None, "s3": None},  # Tall 19.7mg/100ml
        },

        # ── 스타벅스 피지오 (1종) ────────────────────────────────
        {
            "name": "쿨 라임 피지오",
            "category": DrinkCategory.SODA,
            "caffeine": {"s1": 100, "s2": None, "s3": None},  # Tall 28.2mg/100ml
        },

    ],
}

BRANDS = {"starbucks": STARBUCKS}