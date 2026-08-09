"""
CALC-003 : 남은 허용량 산출
===========================

목표 취침시각 기준으로 오늘 더 마실 수 있는 카페인량.

    R = max(0, θ - C(t_b))
    n_cup = floor(R / D_ref)

주의: R은 "취침시각 시점의 잔류 여유"가 아니라 "지금 마셔도 되는 mg"이 아니다.
      명세상 D_i를 취침시각까지 감쇠시킨 값과 θ의 차이이므로,
      실제로 지금 마실 수 있는 양은 이보다 크다(감쇠 이득). 명세 원식 그대로 구현.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from .pharmacokinetics import (
    DAILY_LIMIT_MG,
    Dose,
    concentration_at,
    half_life_to_ke,
)


@dataclass
class AllowanceResult:
    remaining_mg: float          # R
    cups: int                    # n_cup
    residual_at_bedtime_mg: float
    over_threshold: bool         # θ - C(t_b) < 0 -> 초과 경고
    under_one_cup: bool          # R < D_ref -> "한 잔은 어렵습니다"
    over_daily_limit: bool       # 오늘 누적이 400mg 초과 (경고만, 차단 아님)


def calc_allowance(
    bedtime: datetime,
    doses: Sequence[Dose],
    theta_mg: float,
    ref_dose_mg: float,
    ke: float = half_life_to_ke(),
    daily_limit_mg: float = DAILY_LIMIT_MG,
) -> AllowanceResult:
    """
    남은 허용량 R과 환산 잔 수 n_cup 산출.

    ref_dose_mg : 1잔 기준 카페인량 (기본 음료 없으면 아이스아메리카노 180mg)
    """
    if ref_dose_mg <= 0:
        raise ValueError("ref_dose_mg must be positive")

    c_bedtime = concentration_at(doses, bedtime, ke)
    raw = theta_mg - c_bedtime
    remaining = max(0.0, raw)
    cups = math.floor(remaining / ref_dose_mg)

    consumed_today = sum(d.amount_mg for d in doses)

    return AllowanceResult(
        remaining_mg=round(remaining, 1),
        cups=cups,
        residual_at_bedtime_mg=round(c_bedtime, 1),
        over_threshold=raw < 0,
        under_one_cup=remaining < ref_dose_mg,
        over_daily_limit=consumed_today > daily_limit_mg,
    )
