"""
CALC-005 : 개인화 파라미터 갱신
===============================

    R_d  = Σ_{i∈I_d} D_i · exp(-k_e (S_d - t_i))     # 실제 수면시각 시점 잔류량
    B    = { d ∈ D : Q_d <= q_cut }
    θ̂_ind = mean(R_d for d in B)   (|B| = 0 이면 θ_pop)
    n = |D|,  w = n / (n + n_0)
    θ = w·θ̂_ind + (1 - w)·θ_pop

DailyLog는 residual_mg_at_sleep을 파생값으로 저장하므로 평상시엔 R_d를 다시
계산할 필요가 없다. compute_residual_at_sleep()은 그 값을 처음 만들 때만 쓴다.

밤샘 세션 섭취기록은 PK 계산에는 쓰이되 개인화 학습에서는 제외한다.

비고: w = n/(n + n_0) 형태의 가중 혼합은 Liu et al.(2017)의 EKF 개인화
      프레임워크에서 착안한 근사이며 논문 직접 인용이 아니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence

from .pharmacokinetics import (
    DEFAULT_N0,
    DEFAULT_Q_CUT,
    THETA_POP_MG,
    Dose,
    concentration_at,
    half_life_to_ke,
)


@dataclass
class SleepRecord:
    """DailyLog 1행. 수면설문 결과와 그날 취침 시점 잔류량."""

    sleep_quality: int              # Q_d
    residual_mg_at_sleep: float     # R_d
    slept_at: Optional[datetime] = None  # S_d (참조용)


@dataclass
class ThetaResult:
    theta_mg: float          # θ
    theta_ind_mg: float      # θ̂_ind
    theta_pop_mg: float      # θ_pop
    weight: float            # w
    n_records: int           # n
    n_bad_nights: int        # |B|


def compute_residual_at_sleep(
    doses: Sequence[Dose],
    slept_at: datetime,
    ke: float = half_life_to_ke(),
    exclude_all_nighter: bool = True,
) -> float:
    """
    R_d 산출. SLEEP-002 저장 시점에 한 번 계산해 DailyLog에 박제한다.
    밤샘 세션 로그는 학습 오염을 막기 위해 기본 제외.
    """
    pool = [d for d in doses if not (exclude_all_nighter and d.is_all_nighter)]
    return concentration_at(pool, slept_at, ke)


def estimate_theta(
    records: Sequence[SleepRecord],
    theta_pop_mg: float = THETA_POP_MG,
    n0: int = DEFAULT_N0,
    q_cut: int = DEFAULT_Q_CUT,
) -> ThetaResult:
    """
    개인화 임계치 θ 산출. 피드 요청마다 호출(캐싱하지 않음).

    기록 0건이면 w = 0 이므로 θ = θ_pop.
    """
    n = len(records)
    bad = [r.residual_mg_at_sleep for r in records if r.sleep_quality <= q_cut]

    theta_ind = sum(bad) / len(bad) if bad else theta_pop_mg
    w = n / (n + n0) if n > 0 else 0.0
    theta = w * theta_ind + (1 - w) * theta_pop_mg

    return ThetaResult(
        theta_mg=round(theta, 1),
        theta_ind_mg=round(theta_ind, 1),
        theta_pop_mg=theta_pop_mg,
        weight=round(w, 4),
        n_records=n,
        n_bad_nights=len(bad),
    )