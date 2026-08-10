"""
CALC-001 : 체내 잔류 카페인 산출
================================

1구획 지수감쇠 모델. 모든 CALC 모듈의 기반이 되며, 공통 상수도 여기에 둔다.

    k_e = ln2 / t_half
    C(t) = Σ D_i · exp(-k_e (t - t_i)) · 1[t >= t_i]

Django 의존성 없음. 순수 계산 모듈.

참고: Ramakrishnan et al. (2014), J Theor Biol 358:11-24
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Iterable, List, Optional, Sequence

# ---------------------------------------------------------------------------
# 공통 상수
# ---------------------------------------------------------------------------

POP_HALF_LIFE_H = 5.0        # 집단 평균 반감기 (h)
THETA_POP_MG = 80.0          # 기본 임계치 θ_pop (mg) — 서비스 정책값, 문헌 근거 아님
DEFAULT_N0 = 5               # 개인화 가중치 기준 기록 수
DEFAULT_Q_CUT = 2            # 하위 컨디션 판정 커트라인
DAILY_LIMIT_MG = 400.0       # 1일 권장 상한 D_max (경고 전용, 기능 차단 안 함)
SERVICE_DAY_START_HOUR = 5   # 서비스 하루 경계 05:00

W_REF_KG = 65.0              # 기준 체중
W_MIN_KG, W_MAX_KG = 30.0, 200.0

# 밤샘 목표 농도 밴드 (W_REF 기준값, mg)
# 근거: Ramakrishnan(2014)에서 200mg 단회 투여가 40% 예측오차 개선을 보인 반면
#       100mg은 13%에 그침. [100, 200] 밴드의 시간평균(~144mg)이 200mg 투여
#       프로파일과 대응. m=2 이므로 Δs = t_half = 5h.
NIGHT_C_MIN_REF_MG = 100.0
NIGHT_C_MAX_REF_MG = 200.0


def half_life_to_ke(half_life_h: float = POP_HALF_LIFE_H) -> float:
    """반감기(h) -> 소실 상수 k_e(1/h)."""
    if half_life_h <= 0:
        raise ValueError("half_life_h must be positive")
    return math.log(2) / half_life_h


def ke_to_half_life(ke: float) -> float:
    """소실 상수 k_e(1/h) -> 반감기(h)."""
    if ke <= 0:
        raise ValueError("ke must be positive")
    return math.log(2) / ke


# ---------------------------------------------------------------------------
# 체중 보정 (CALC-004, CALC-006 공용)
# ---------------------------------------------------------------------------

def clamp_weight(body_weight_kg: Optional[float]) -> float:
    """
    체중 미설정 -> W_ref 폴백. 범위 밖 -> [30, 200]kg 클램프.

    클램프 목적: M_0 = 9.86·(W_ref/W) 가 극단 체중에서 발산하는 것을 막는다.
    """
    if body_weight_kg is None or body_weight_kg <= 0:
        return W_REF_KG
    return min(max(body_weight_kg, W_MIN_KG), W_MAX_KG)


def dose_scale(body_weight_kg: Optional[float]) -> float:
    """
    동일 각성 수준(g_PD)을 유지하기 위한 용량 배율 = W / W_ref.

    유도: g_PD = 1/(1 + M_0(W)·D) 이고 M_0 ∝ 1/W 이므로,
          g_PD 고정 <=> M_0·D 일정 <=> D ∝ W.
    무거울수록 같은 효과에 더 많은 mg이 필요하다. (65/W 가 아니라 W/65)
    """
    return clamp_weight(body_weight_kg) / W_REF_KG


# ---------------------------------------------------------------------------
# 시각 유틸리티
# ---------------------------------------------------------------------------

def hours_between(start: datetime, end: datetime) -> float:
    """start -> end 경과 시간(h). 음수 가능."""
    return (end - start).total_seconds() / 3600.0


def resolve_next_occurrence(target: time, now: datetime) -> datetime:
    """고정된 목표 시각(time) 기준 now 이후 가장 가까운 datetime."""
    candidate = datetime.combine(now.date(), target, tzinfo=now.tzinfo)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def service_date(moment: datetime):
    """서비스 하루 경계 05:00 기준 service_date."""
    return (moment - timedelta(hours=SERVICE_DAY_START_HOUR)).date()


def fmt_hhmm(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# ---------------------------------------------------------------------------
# 섭취 기록
# ---------------------------------------------------------------------------

@dataclass
class Dose:
    """
    카페인 섭취 1회. CaffeineLog 1행에 대응.

    drink_name / caffeine_mg 스냅샷 정책에 따라 amount_mg는 로그에 박제된 값을 그대로 받는다.
    log_id, drink_name은 그래프 marks 생성용(옵션).
    """

    amount_mg: float
    taken_at: datetime
    log_id: Optional[int] = None
    drink_name: Optional[str] = None
    is_all_nighter: bool = False   # 개인화 학습(CALC-005)에서 제외 판정용


# ---------------------------------------------------------------------------
# 농도 계산
# ---------------------------------------------------------------------------

def concentration_from_dose(dose: Dose, at: datetime, ke: float) -> float:
    """단일 도즈의 at 시점 잔류량(mg). 아직 섭취 전이면 0."""
    elapsed_h = hours_between(dose.taken_at, at)
    if elapsed_h < 0:
        return 0.0
    return dose.amount_mg * math.exp(-ke * elapsed_h)


def concentration_at(
    doses: Iterable[Dose],
    at: datetime,
    ke: float = half_life_to_ke(),
) -> float:
    """
    C(t) = Σ D_i · exp(-k_e (t - t_i))

    섭취기록 0건이면 0.0.
    """
    return sum(concentration_from_dose(d, at, ke) for d in doses)


def concentration_series(
    doses: Sequence[Dose],
    start: datetime,
    interval_min: int,
    count: int,
    ke: float = half_life_to_ke(),
) -> List[float]:
    """start부터 interval_min 간격으로 count개 샘플링한 농도 배열."""
    step = timedelta(minutes=interval_min)
    return [
        round(concentration_at(doses, start + step * i, ke), 2)
        for i in range(count)
    ]


def time_to_index(moment: Optional[datetime], start: datetime, interval_min: int,
                  count: int) -> Optional[int]:
    """절대 시각을 그래프 배열 인덱스로 변환. 범위 밖이면 None."""
    if moment is None:
        return None
    idx = round(hours_between(start, moment) * 60 / interval_min)
    return idx if 0 <= idx < count else None


def build_curve_payload(
    doses: Sequence[Dose],
    start: datetime,
    interval_min: int = 15,
    count: int = 96,
    ke: float = half_life_to_ke(),
    threshold_mg: Optional[float] = None,
    threshold_role: str = "max",
    now: Optional[datetime] = None,
    bedtime: Optional[datetime] = None,
    cutoff_at: Optional[datetime] = None,
) -> dict:
    """
    프론트 그래프용 JSON 페이로드 생성.

    threshold_role : "max"(취침 임계치 θ) | "min"(밤샘 하한 C_min)
    """
    mg = concentration_series(doses, start, interval_min, count, ke)

    marks = []
    for d in doses:
        idx = time_to_index(d.taken_at, start, interval_min, count)
        if idx is None:
            continue
        marks.append({
            "index": idx,
            "log_id": d.log_id,
            "at": d.taken_at.isoformat(),
            "dose_mg": d.amount_mg,
            "drink": d.drink_name,
        })

    return {
        "start": start.isoformat(),
        "interval_min": interval_min,
        "count": count,
        "mg": mg,
        "threshold_mg": threshold_mg,
        "threshold_role": threshold_role,
        "now_index": time_to_index(now, start, interval_min, count),
        "bedtime_index": time_to_index(bedtime, start, interval_min, count),
        "cutoff_index": time_to_index(cutoff_at, start, interval_min, count),
        "cutoff_at": cutoff_at.isoformat() if cutoff_at else None,
        "marks": marks,
    }