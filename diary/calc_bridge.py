# diary/calc_bridge.py
"""calcs 엔진과 Django ORM을 잇는 조회 계층.

calcs 패키지는 Django에 의존하지 않는 순수 계산 모듈이다(각 calcs/*.py
docstring 참고). CaffeineLog/SleepLog/Drink를 calcs가 쓰는 Dose/SleepRecord로
변환하는 코드는 대신 여기 둔다. accounts(프로필)와 diary(피드) 양쪽에서
재사용한다.
"""

from datetime import datetime, timedelta
from datetime import time as dt_time

from django.utils import timezone

from calcs.pharmacokinetics import SERVICE_DAY_START_HOUR, Dose, service_date
from calcs.personalization import SleepRecord, ThetaResult, estimate_theta

from .models import CaffeineLog, Drink, SleepLog

# 잔류량 계산에 포함할 과거 섭취기록의 최대 조회 범위(시간). 집단 평균 반감기가 5h이므로
# 48h(~10 half-life) 이전 기록의 기여도는 2^-9.6 ≈ 0.1%로 무시할 수 있는 수준이다.
DOSE_LOOKBACK_HOURS = 48

# 대표 음료(1잔 기준)가 없을 때 쓰는 기본값. calcs/allowance.py의 ref_dose_mg
# 설명("기본 음료 없으면 아이스아메리카노 180mg")을 그대로 따른다.
DEFAULT_REF_DOSE_MG = 180.0


def doses_for_user(user, until, since=None):
    """[since, until] 구간의 CaffeineLog를 calcs.Dose 목록으로 변환한다.

    since를 생략하면 until 기준 DOSE_LOOKBACK_HOURS 이전부터 조회한다.
    """
    if since is None:
        since = until - timedelta(hours=DOSE_LOOKBACK_HOURS)
    logs = CaffeineLog.objects.filter(user=user, created_at__gte=since, created_at__lte=until)
    return [
        Dose(amount_mg=log.caffeine_mg, taken_at=log.created_at, log_id=log.id, drink_name=log.name)
        for log in logs
    ]


def theta_for_user(user) -> ThetaResult:
    """사용자의 SleepLog 이력으로 CALC-005 개인화 임계치를 산출한다.

    residual_mg_at_sleep/sleep_quality가 없는 기록(취침시각을 안 남긴 경우)은
    θ 추정에 쓸 수 없으므로 제외한다.
    """
    logs = SleepLog.objects.filter(
        user=user, residual_mg_at_sleep__isnull=False, sleep_quality__isnull=False
    )
    records = [
        SleepRecord(
            sleep_quality=log.sleep_quality,
            residual_mg_at_sleep=log.residual_mg_at_sleep,
            slept_at=log.actual_bedtime,
        )
        for log in logs
    ]
    return estimate_theta(records)


def service_day_bounds(now):
    """now가 속한 서비스일(today)과 그 시작 시각(day_start)을 반환한다.

    서비스일 경계는 05:00, 서버 로컬시각(Asia/Seoul) 기준이다. now는 항상
    UTC를 담고 있으므로(Django timezone.now() 규약) localtime으로 변환한
    뒤 날짜를 뽑아야 한다. FeedStatusView(피드 계산)와 SleepLog 하루 1회
    제한 판정 양쪽에서 같은 "오늘"을 써야 하므로 여기 모아둔다.
    """
    local_now = timezone.localtime(now)
    today = service_date(local_now)
    day_start = timezone.make_aware(datetime.combine(today, dt_time(hour=SERVICE_DAY_START_HOUR)))
    return today, day_start


def reference_dose_mg(user):
    """CALC-002/003/006에 쓰는 '대표 음료 1잔' 기준량(mg).

    즐겨찾는 음료 중 가장 최근 것을 대표로 쓰고, 없으면 기본값으로 폴백한다.
    """
    favorite = (
        Drink.objects.filter(user=user, is_favorite=True, is_active=True)
        .order_by("-created_at")
        .first()
    )
    return favorite.caffeine_mg if favorite else DEFAULT_REF_DOSE_MG
