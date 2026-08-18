# allnight/views.py
"""allnight 앱 뷰 - 밤샘모드(AllNightSession) API.

명세(Notion API 명세서, NIGHT-001~003) 기준.

핵심 원칙: 섭취 스케줄(calcs.night_schedule, CALC-004)은 DB에 저장하지
않는다. GET /night-sessions/current를 호출할 때마다 그 시점 기준으로 다시
계산해서 돌려준다(사용자가 스케줄과 다르게 마셔도 다음 호출 때 보정된다).
"""

from django.db import IntegrityError
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile
from calcs.marginal_utility import calc_marginal_utility
from calcs.night_schedule import calc_night_schedule, next_dose
from calcs.pharmacokinetics import DAILY_LIMIT_MG, concentration_at
from diary.calc_bridge import doses_for_user, service_day_bounds
from diary.models import Drink

from .models import AllNightSession
from .serializers import NightSessionEndSerializer, NightSessionStartSerializer

# 메인피드(feed.js)의 즐겨찾는 음료 컵 슬롯과 동일하게 최대 3개까지만 보여준다.
MAX_FAVORITE_DRINKS = 3


def _iso(dt):
    """타임존 인지 datetime을 서버 로컬시각(Asia/Seoul) ISO-8601 문자열로."""
    return timezone.localtime(dt).isoformat() if dt else None


def _session_data(session):
    """POST 응답(NIGHT-001): 생성 직후의 최소 정보만 돌려준다.

    스케줄 상세는 GET /night-sessions/current에서 조회한다(명세 그대로).
    """
    return {
        "session_id": session.id,
        "started_at": _iso(session.started_at),
        "target_awake_until": _iso(session.target_time),
        "status": "active",
        "next": "/night",
    }


def _summary_data(session, *, reached_target, total_intake_mg):
    """종료(자동/수동) 응답(NIGHT-002 자동종료, NIGHT-003): 세션 요약."""
    duration_min = round((session.ended_at - session.started_at).total_seconds() / 60)
    return {
        "session_id": session.id,
        "status": "ended",
        "started_at": _iso(session.started_at),
        "ended_at": _iso(session.ended_at),
        "target_awake_until": _iso(session.target_time),
        "reached_target": reached_target,
        "duration_min": duration_min,
        "total_intake_mg": round(total_intake_mg, 1),
        # 밤샘일은 수면데이터가 없으므로 다음날 수면설문을 항상 스킵한다(SLEEP-001).
        # 실제 판정은 diary.views.FeedStatusView._sleep_survey_required가
        # AllNightSession 존재 여부로 다시 확인하므로, 여기선 통보용 값이다.
        "sleep_survey_skipped": True,
        "next": "/",
    }


class NightSessionStartView(APIView):
    """POST /night-sessions/ — 밤샘모드 시작(NIGHT-001).

    선행조건: 로그인 + UserProfile 존재. 활성 세션은 사용자당 동시에 하나뿐이다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not UserProfile.objects.filter(user=user).exists():
            return Response(
                {
                    "code": "PROFILE_NOT_FOUND",
                    "message": "프로필이 없습니다.",
                    "next": "/signup/profile",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        active = AllNightSession.objects.filter(
            user=user, status=AllNightSession.Status.ACTIVE
        ).first()
        if active is not None:
            return Response(
                {
                    "code": "NIGHT_SESSION_ALREADY_ACTIVE",
                    "message": "이미 진행 중인 밤샘모드가 있습니다.",
                    "session_id": active.id,
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = NightSessionStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 위 .filter().first() 체크와 아래 생성 사이의 경합은 uniq_active_session_per_user
        # 제약(모델 Meta)이 막는다 — 동시 요청이 둘 다 통과해도 하나는 여기서 걸린다.
        try:
            session = AllNightSession.objects.create(
                user=user,
                status=AllNightSession.Status.ACTIVE,
                started_at=timezone.now(),
                target_time=serializer.validated_data["target_awake_until"],
            )
        except IntegrityError:
            active = AllNightSession.objects.get(
                user=user, status=AllNightSession.Status.ACTIVE
            )
            return Response(
                {
                    "code": "NIGHT_SESSION_ALREADY_ACTIVE",
                    "message": "이미 진행 중인 밤샘모드가 있습니다.",
                    "session_id": active.id,
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(_session_data(session), status=status.HTTP_201_CREATED)


class NightSessionCurrentView(APIView):
    """GET/PATCH /night-sessions/current/ — 밤샘모드 진행 조회·종료(NIGHT-002~003).

    GET 응답의 favorite_drinks는 사용자의 즐겨찾는 음료(최대 3개, 메인피드 컵
    슬롯과 동일 기준)마다 이번 회차 섭취량(dose_mg)이 그 음료 몇 잔에 해당하는지
    (dose_cups)를 같이 내려준다 — "몇 잔 마시면 되는지"를 음료별로 보여주기 위함.
    """

    permission_classes = [permissions.IsAuthenticated]

    def _active_session(self, user):
        return AllNightSession.objects.filter(
            user=user, status=AllNightSession.Status.ACTIVE
        ).first()

    def _not_found(self):
        return Response(
            {
                "code": "NIGHT_SESSION_NOT_FOUND",
                "message": "진행 중인 밤샘모드가 없습니다.",
                "next": "/",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    def get(self, request):
        session = self._active_session(request.user)
        if session is None:
            return self._not_found()

        now = timezone.now()

        # 목표시각 경과 -> 이 조회 시점에 자동종료(명세: 별도 API 호출 불필요).
        if now >= session.target_time:
            session_doses = doses_for_user(request.user, now, since=session.started_at)
            total_intake_mg = sum(d.amount_mg for d in session_doses)
            session.status = AllNightSession.Status.COMPLETED
            session.ended_at = now
            session.save(update_fields=["status", "ended_at"])
            return Response(
                _summary_data(session, reached_target=True, total_intake_mg=total_intake_mg),
                status=status.HTTP_200_OK,
            )

        profile = getattr(request.user, "profile", None)
        body_weight_kg = profile.body_weight_kg if profile else None

        # E_today와 C(t_0) 양쪽 다 "오늘(서비스일)" 섭취 이력을 쓴다
        # (calcs/night_schedule.py 독스트링 참고). FeedStatusView와 같은 기준.
        _, day_start = service_day_bounds(now)
        doses = doses_for_user(request.user, now, since=day_start)

        schedule = calc_night_schedule(now, session.target_time, doses, body_weight_kg=body_weight_kg)
        current_mg = round(concentration_at(doses, now), 1)
        upcoming = next_dose(schedule, now)
        marginal = calc_marginal_utility(schedule.total_mg, schedule.dose_mg, body_weight_kg)

        # 회차별 섭취량(dose_mg, 모든 회차 공통값)을 즐겨찾는 음료마다 "몇 잔"으로
        # 환산한다. 즐겨찾는 음료가 하나도 없으면 빈 목록 — 화면에서 자연히 생략된다.
        favorite_drinks = list(
            Drink.objects.filter(user=request.user, is_favorite=True, is_active=True)
            .order_by("-created_at")[:MAX_FAVORITE_DRINKS]
        )
        favorite_drinks_data = [
            {
                "drink_id": d.id,
                "name": d.name,
                "caffeine_mg": d.caffeine_mg,
                "dose_cups": round(schedule.dose_mg / d.caffeine_mg, 1) if d.caffeine_mg > 0 else None,
            }
            for d in favorite_drinks
        ]

        warnings = []
        if schedule.exceeds_daily_limit:
            warnings.append(
                {"code": "DAILY_LIMIT_EXCEEDED", "message": "일일 권장 상한을 초과했습니다."}
            )

        data = {
            "session_id": session.id,
            "status": "active",
            "started_at": _iso(session.started_at),
            "target_awake_until": _iso(session.target_time),
            "now": _iso(now),
            "time_remaining_min": round((session.target_time - now).total_seconds() / 60),
            "current_mg": current_mg,
            "c_min": schedule.c_min,
            "c_max": schedule.c_max,
            "in_target_range": schedule.c_min <= current_mg <= schedule.c_max,
            "next_dose_at": _iso(upcoming.at) if upcoming else None,
            "next_dose_mg": upcoming.dose_mg if upcoming else None,
            "favorite_drinks": favorite_drinks_data,
            "schedule": [
                {"at": _iso(d.at), "dose_mg": d.dose_mg, "done": d.at <= now}
                for d in schedule.doses
            ],
            "total_mg": schedule.total_mg,
            "daily_limit_mg": DAILY_LIMIT_MG,
            "limit_reached_at": _iso(schedule.limit_reached_at),
            "marginal": {
                "g_pd_min": marginal.g_pd_after,
                "delta_g": marginal.delta_g,
                "warning": marginal.warning is not None,
            },
            "warnings": warnings,
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        session = self._active_session(request.user)
        if session is None:
            return self._not_found()

        serializer = NightSessionEndSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        now = timezone.now()
        session_doses = doses_for_user(request.user, now, since=session.started_at)
        total_intake_mg = sum(d.amount_mg for d in session_doses)

        session.status = AllNightSession.Status.ABORTED
        session.ended_at = now
        session.save(update_fields=["status", "ended_at"])

        return Response(
            _summary_data(session, reached_target=False, total_intake_mg=total_intake_mg),
            status=status.HTTP_200_OK,
        )
