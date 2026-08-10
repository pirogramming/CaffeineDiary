"""
CALC-002 : 마감시각 산출
========================

"지금 이후 언제까지 한 잔을 더 마셔도 목표 취침시각의 잔류량이 임계치를 넘지 않는가"

    T = t_b - t_0
    E = Σ D_i · exp(-k_e (t_b - t_i))      # 취침시각 기존 잔류량
    B = θ - E                              # 허용 카페인
    r = B / D_p
    t_cut = t_b + (1/k_e) · ln r

선행: UserProfile.target_bedtime 설정, CALC-005의 θ 확정
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Sequence

from .pharmacokinetics import Dose, concentration_at, half_life_to_ke, hours_between


class CutoffStatus(str, Enum):
    OK = "OK"                            # 정상 산출
    BEDTIME_PASSED = "BEDTIME_PASSED"    # T <= 0
    OVER_THRESHOLD = "OVER_THRESHOLD"    # B <= 0, 기존 섭취만으로 초과
    NO_PLANNED_DOSE = "NO_PLANNED_DOSE"  # D_p <= 0, t_b 그대로 반환
    CUTOFF_PASSED = "CUTOFF_PASSED"      # t_cut <= t_0, 마감 지남 경고


@dataclass
class CutoffResult:
    """
    cutoff_at : 마감 절대시각. 명세상 None 반환 케이스(T<=0, B<=0)에서는 None.
    status    : 프론트 문구 분기용
    """

    cutoff_at: Optional[datetime]
    status: CutoffStatus
    bedtime: datetime
    residual_at_bedtime_mg: float
    budget_mg: float

    @property
    def is_drinkable(self) -> bool:
        return self.status in (CutoffStatus.OK, CutoffStatus.NO_PLANNED_DOSE)


def residual_at_bedtime(
    doses: Sequence[Dose],
    bedtime: datetime,
    ke: float = half_life_to_ke(),
) -> float:
    """E = Σ D_i · exp(-k_e (t_b - t_i))"""
    return concentration_at(doses, bedtime, ke)


def calc_cutoff(
    now: datetime,
    bedtime: datetime,
    planned_dose_mg: float,
    doses: Sequence[Dose],
    theta_mg: float,
    ke: float = half_life_to_ke(),
) -> CutoffResult:
    """
    마감시각 t_cut 산출.

    예외 분기
      T <= 0        : 취침시각 이미 경과 -> cutoff_at=None
      B <= 0        : 기존 섭취만으로 기준 초과 -> cutoff_at=None
      D_p <= 0      : t_b 반환
      t_cut <= t_0  : 마감 지남 경고와 함께 t_cut 반환
    """
    e_mg = residual_at_bedtime(doses, bedtime, ke)
    budget = theta_mg - e_mg

    if hours_between(now, bedtime) <= 0:
        return CutoffResult(None, CutoffStatus.BEDTIME_PASSED, bedtime, e_mg, budget)

    if budget <= 0:
        return CutoffResult(None, CutoffStatus.OVER_THRESHOLD, bedtime, e_mg, budget)

    if planned_dose_mg <= 0:
        return CutoffResult(bedtime, CutoffStatus.NO_PLANNED_DOSE, bedtime, e_mg, budget)

    r = budget / planned_dose_mg
    t_cut = bedtime + _hours(math.log(r) / ke)

    status = CutoffStatus.OK if t_cut > now else CutoffStatus.CUTOFF_PASSED
    return CutoffResult(t_cut, status, bedtime, e_mg, budget)


def _hours(h: float):
    from datetime import timedelta
    return timedelta(hours=h)
