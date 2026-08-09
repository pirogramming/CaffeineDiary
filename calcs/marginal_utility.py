"""
CALC-006 : 한계효용 판정
========================

    M_0(W) = M_0^ref · (W_ref / W)          # W_ref = 65kg, M_0^ref = 9.86 g^-1
    g_PD^min(D) = 1 / (1 + M_0·D)           # D 단위는 그램(g)
    Δg = g_PD^min(D_cum) - g_PD^min(D_cum + D_p)

    Δg < ε (=0.02) 이면 "효과 미미" 경고.

주의: M_0의 단위가 g^-1 이므로 서비스 내부의 mg 값을 반드시 g로 환산해야 한다.

인용 구분
  - M_0 = F/(V_d · g_PK50) 및 9.86 g^-1 : Ramakrishnan et al. (2014) 직접 인용
  - 65kg 정규화 후 개인 체중 스케일링   : 본 서비스의 적용 확장(논문에 없음)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .pharmacokinetics import (
    DAILY_LIMIT_MG,
    W_REF_KG,
    clamp_weight,
)

M0_REF_PER_G = 9.86      # 집단평균 진폭 기울기 (g^-1), Ramakrishnan 2014 Study A
DEFAULT_EPSILON = 0.02   # 한계효용 하한 ε


@dataclass
class MarginalUtilityResult:
    g_pd_current: float      # g_PD^min(D_cum), 0에 가까울수록 각성효과 큼
    g_pd_after: float        # g_PD^min(D_cum + D_p)
    delta_g: float           # Δg
    m0: float                # M_0(W)
    negligible: bool         # Δg < ε
    over_daily_limit: bool   # D_cum >= D_max (Δg와 무관하게 우선 경고)

    @property
    def warning(self) -> Optional[str]:
        """상한 경고가 한계효용 경고보다 우선."""
        if self.over_daily_limit:
            return "DAILY_LIMIT_EXCEEDED"
        if self.negligible:
            return "NEGLIGIBLE_EFFECT"
        return None


def m0_for_weight(body_weight_kg: Optional[float]) -> float:
    """M_0(W) = 9.86 · 65 / W   (단위 g^-1)"""
    return M0_REF_PER_G * (W_REF_KG / clamp_weight(body_weight_kg))


def g_pd_min(dose_mg: float, m0: float) -> float:
    """g_PD^min(D) = 1 / (1 + M_0·D).  dose_mg는 mg -> g 환산 후 대입."""
    return 1.0 / (1.0 + m0 * (max(0.0, dose_mg) / 1000.0))


def calc_marginal_utility(
    cumulative_mg: float,
    planned_dose_mg: float,
    body_weight_kg: Optional[float] = None,
    epsilon: float = DEFAULT_EPSILON,
    daily_limit_mg: float = DAILY_LIMIT_MG,
) -> MarginalUtilityResult:
    """
    추가 1회분 D_p가 실제로 각성 개선을 주는지 판정.
    경고만 발생시키며 어떤 기능도 차단하지 않는다.
    """
    m0 = m0_for_weight(body_weight_kg)
    g_now = g_pd_min(cumulative_mg, m0)
    g_after = g_pd_min(cumulative_mg + max(0.0, planned_dose_mg), m0)
    delta = g_now - g_after

    return MarginalUtilityResult(
        g_pd_current=round(g_now, 4),
        g_pd_after=round(g_after, 4),
        delta_g=round(delta, 4),
        m0=round(m0, 3),
        negligible=delta < epsilon,
        over_daily_limit=cumulative_mg >= daily_limit_mg,
    )