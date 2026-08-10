"""
CALC-004 : 밤샘 섭취 스케줄 생성
================================

목표 시각 T_w까지 C(t) ∈ [C_min, C_max]를 유지하는 톱니파 스케줄.

    m  = C_max / C_min
    D_k = C_max - C_min = (m - 1)·C_min
    Δs = (1/k_e)·ln m

    s_1 = t_0 + (1/k_e)·ln(C(t_0)/C_min)   if C(t_0) > C_min
        = t_0                              otherwise
    s_{k+1} = s_k + Δs
    K = ceil((T_w - s_1) / Δs)

    S_total = E_today + Σ D_k <= D_max
    K_lim = floor((D_max - E_today) / D_k),  T_lim = s_1 + K_lim·Δs

스케줄은 매 GET마다 재계산하며 영속화하지 않는다.
C_min / C_max 기본값은 아직 문헌 확정 전이므로 호출부에서 명시적으로 넘긴다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Sequence

from .pharmacokinetics import (
    DAILY_LIMIT_MG,
    NIGHT_C_MAX_REF_MG,
    NIGHT_C_MIN_REF_MG,
    Dose,
    concentration_at,
    dose_scale,
    half_life_to_ke,
    hours_between,
)

MAX_SESSION_HOURS = 24.0   # T_w - t_0 는 NIGHT-001에서 24h 초과 차단


def default_band(body_weight_kg: Optional[float] = None) -> tuple[float, float]:
    """
    체중 보정된 목표 농도 밴드 (C_min, C_max) 산출.

        C_min = 100 · (W / 65),  C_max = 200 · (W / 65)

    두 값에 같은 배율이 걸리므로 m = C_max/C_min = 2 가 유지되고,
    따라서 Δs = (1/k_e)·ln 2 = 반감기(5h)로 체중과 무관하게 고정된다.
    체중이 바꾸는 것은 회차당 용량 D_k 뿐이다.

    체중 미입력 시 W_ref=65kg 폴백 -> (100, 200).
    """
    scale = dose_scale(body_weight_kg)
    return (
        round(NIGHT_C_MIN_REF_MG * scale, 1),
        round(NIGHT_C_MAX_REF_MG * scale, 1),
    )


@dataclass
class ScheduledDose:
    index: int          # k
    at: datetime        # s_k
    dose_mg: float      # D_k
    exceeds_limit: bool # 이 시점 섭취가 D_max를 넘기는가


@dataclass
class NightScheduleResult:
    doses: List[ScheduledDose]
    c_min: float                    # 실제 적용된 밴드 하한 (체중 보정 후)
    c_max: float                    # 실제 적용된 밴드 상한
    dose_mg: float                  # D_k (모든 회차 동일)
    interval_h: float               # Δs
    first_intake_at: datetime       # s_1
    total_mg: float                 # S_total (E_today 포함)
    limit_reached_at: Optional[datetime]  # T_lim
    exceeds_daily_limit: bool


def calc_night_schedule(
    now: datetime,
    wake_until: datetime,
    doses: Sequence[Dose],
    c_min: Optional[float] = None,
    c_max: Optional[float] = None,
    body_weight_kg: Optional[float] = None,
    ke: float = half_life_to_ke(),
    daily_limit_mg: float = DAILY_LIMIT_MG,
) -> NightScheduleResult:
    """
    밤샘 섭취 스케줄 산출.

    c_min / c_max : 목표 농도 밴드(mg). 생략 시 body_weight_kg로 default_band() 도출.
                    세션 시작 시 확정한 값이 있으면 그것을 넘겨 세션 중 스케줄이
                    요동치지 않게 한다.
    doses         : 오늘 섭취 이력. E_today와 C(t_0) 양쪽에 사용
    """
    if c_min is None or c_max is None:
        c_min, c_max = default_band(body_weight_kg)

    if c_min <= 0 or c_max <= c_min:
        raise ValueError("c_max > c_min > 0 required")

    horizon_h = hours_between(now, wake_until)
    if horizon_h > MAX_SESSION_HOURS:
        raise ValueError("session longer than 24h is blocked by NIGHT-001")

    m = c_max / c_min
    dose_k = c_max - c_min
    delta_s_h = math.log(m) / ke

    # 첫 섭취 시점 s_1
    c_now = concentration_at(doses, now, ke)
    if c_now > c_min:
        wait_h = math.log(c_now / c_min) / ke
        s1 = now + timedelta(hours=wait_h)
    else:
        s1 = now

    # 회차 수 K
    span_h = hours_between(s1, wake_until)
    k_count = max(0, math.ceil(span_h / delta_s_h)) if span_h > 0 else 0

    e_today = sum(d.amount_mg for d in doses)
    budget = daily_limit_mg - e_today
    k_lim = max(0, math.floor(budget / dose_k)) if dose_k > 0 else 0

    schedule = [
        ScheduledDose(
            index=k + 1,
            at=s1 + timedelta(hours=delta_s_h * k),
            dose_mg=round(dose_k, 1),
            exceeds_limit=(k + 1) > k_lim,
        )
        for k in range(k_count)
    ]

    total = e_today + dose_k * k_count
    exceeds = total > daily_limit_mg
    t_lim = s1 + timedelta(hours=delta_s_h * k_lim) if exceeds else None

    return NightScheduleResult(
        doses=schedule,
        c_min=c_min,
        c_max=c_max,
        dose_mg=round(dose_k, 1),
        interval_h=round(delta_s_h, 3),
        first_intake_at=s1,
        total_mg=round(total, 1),
        limit_reached_at=t_lim,
        exceeds_daily_limit=exceeds,
    )


def next_dose(result: NightScheduleResult, now: datetime) -> Optional[ScheduledDose]:
    """NIGHT-002 피드용: now 이후 가장 가까운 예정 섭취."""
    return next((d for d in result.doses if d.at > now), None)