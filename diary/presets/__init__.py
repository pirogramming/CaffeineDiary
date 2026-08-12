"""프리셋 음료 카탈로그 레지스트리.

브랜드별 원본 데이터(`starbucks.py`, `compose.py` 등)를 읽기 전용으로 모아두고,
(브랜드, 음료, 사이즈) leaf 단위로 조회할 수 있는 헬퍼를 제공한다.

이 패키지는 DB에 접근하지 않는다. Drink 모델과의 연결은 serializer가 담당한다.
새 브랜드를 추가할 때는 (1) 데이터 파일을 만들고 (2) 아래 PRESET_BRANDS에
등록한 뒤 (3) constants.Brand에도 같은 코드를 추가해야 한다.
"""

from .baik import BAIK
from .compose import COMPOSE
from .ediya import EDIYA
from .gongcha import GONGCHA
from .mega import MEGA
from .soda import COCACOLA, PEPSI
from .mammoth import MAMMOTH
from .starbucks import STARBUCKS

# 브랜드 코드 -> 브랜드 정의. 등록 순서가 목록 노출 순서가 된다.
PRESET_BRANDS = {
    b["code"]: b
    for b in (STARBUCKS, COMPOSE, BAIK, MAMMOTH, EDIYA, MEGA, GONGCHA, PEPSI, COCACOLA)
}


def brand_choices():
    """프리셋이 있는 브랜드의 (코드, 표시명) 목록을 반환한다.

    constants.Brand와의 정합성을 테스트에서 확인하거나, 브랜드 선택
    드롭다운을 만들 때 쓴다.

    Returns:
        list[tuple[str, str]]: 예) [("starbucks", "스타벅스"), ...]
    """
    return [(code, b["name"]) for code, b in PRESET_BRANDS.items()]


def size_labels(brand_code):
    """브랜드가 취급하는 사이즈 라벨을 표시 순서대로 반환한다.

    Args:
        brand_code (str): 브랜드 코드. 예) "starbucks"

    Returns:
        list[str]: 사이즈 라벨 목록. 예) ["Tall", "Grande", "Venti"]
            프리셋이 없는 브랜드(직접 입력 등)는 빈 리스트를 반환하며,
            호출부는 이를 "사이즈 검증 대상 아님"으로 해석한다.
    """
    brand = PRESET_BRANDS.get(brand_code)
    return [s["label"] for s in brand["sizes"]] if brand else []


def _leaf(brand, drink, size):
    """음료 1건 + 사이즈 1건을 평면 dict 하나로 조립한다.

    내부 헬퍼. `iter_presets`와 `find_preset`이 동일한 형태의 결과를
    내도록 조립 로직을 한 곳에 모아둔 것이다.

    Args:
        brand (dict): PRESET_BRANDS의 브랜드 정의
        drink (dict): 브랜드 정의 안의 음료 항목
        size (dict): 브랜드 정의 안의 사이즈 항목

    Returns:
        dict: brand, brand_name, type, name, size, caffeine_mg 키를 가진 dict.
            caffeine_mg는 아직 값이 입력되지 않았으면 None이다.
    """
    return {
        "brand": brand["code"],
        "brand_name": brand["name"],
        "type": drink["category"],
        "name": drink["name"],
        "size": size["label"],
        "caffeine_mg": drink["caffeine"].get(size["code"]),
    }


def iter_presets(brand_code=None, include_unfilled=False):
    """프리셋을 (브랜드, 음료, 사이즈) leaf 단위로 펼쳐서 순회한다.

    카탈로그는 브랜드 > 음료 > 사이즈 3단 중첩이지만, 클라이언트가 실제로
    선택하는 단위는 leaf 하나다. 이 함수가 그 변환을 담당한다.

    Args:
        brand_code (str | None): 특정 브랜드만 조회할 때 지정.
            None이면 전체 브랜드를 순회한다.
        include_unfilled (bool): 카페인량이 아직 None인 사이즈도 포함할지 여부.
            기본값 False. 사용자에게 노출하는 목록에는 포함하지 않는다.

    Yields:
        dict: `_leaf` 형태의 dict.
    """
    if brand_code:
        brands = [PRESET_BRANDS[brand_code]] if brand_code in PRESET_BRANDS else []
    else:
        brands = list(PRESET_BRANDS.values())

    for brand in brands:
        for drink in brand["drinks"]:
            for size in brand["sizes"]:
                leaf = _leaf(brand, drink, size)
                if leaf["caffeine_mg"] is None and not include_unfilled:
                    continue
                yield leaf


def find_preset(brand_code, name, size_label=None):
    """프리셋 leaf 하나를 정확히 찾아 반환한다.

    클라이언트가 보낸 (브랜드, 음료명, 사이즈)가 실재하는 조합인지
    확인하고, 서버가 신뢰할 수 있는 카페인량을 얻기 위해 사용한다.

    Args:
        brand_code (str): 브랜드 코드
        name (str): 음료명. 카탈로그에 적힌 것과 정확히 일치해야 한다.
        size_label (str | None): 사이즈 라벨. 브랜드에 사이즈가 없으면 None.

    Returns:
        dict | None: 일치하는 leaf. 없으면 None.
            찾았지만 카페인량이 미입력이면 caffeine_mg가 None인 채로 반환하므로,
            호출부에서 별도로 확인해야 한다.
    """
    brand = PRESET_BRANDS.get(brand_code)
    if brand is None:
        return None

    drink = next((d for d in brand["drinks"] if d["name"] == name), None)
    if drink is None:
        return None

    size = next((s for s in brand["sizes"] if s["label"] == size_label), None)
    if size is None:
        return None

    return _leaf(brand, drink, size)