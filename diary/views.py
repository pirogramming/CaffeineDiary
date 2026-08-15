"""diary 앱 뷰 - 음료(Drink) API.

인증된 사용자의 음료 마스터를 다룬다. 직렬화기(serializers.py)와 프리셋
카탈로그(presets/)는 이미 완성돼 있으므로, 여기서는 요청/권한/쿼리셋만
연결한다.

권한 원칙:
  - 로그인 필수(IsAuthenticated). settings에 DEFAULT_PERMISSION_CLASSES가
    없어 기본값이 AllowAny이므로, 각 뷰에서 명시적으로 지정한다.
  - 쿼리셋을 request.user로 좁혀, 타인의 음료는 조회/수정/삭제 대상에서
    아예 제외한다(404로 떨어진다).
"""

from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile
from allnight.models import AllNightSession
from calcs.allowance import calc_allowance
from calcs.cutoff import CutoffStatus, calc_cutoff
from calcs.marginal_utility import calc_marginal_utility
from calcs.pharmacokinetics import (
    SERVICE_DAY_START_HOUR,
    build_curve_payload,
    concentration_at,
    resolve_next_occurrence,
    service_date,
)

from .calc_bridge import doses_for_user, reference_dose_mg, service_day_bounds, theta_for_user
from .models import CaffeineLog, Drink, SleepLog
from .presets import iter_presets
from .serializers import (
    CaffeineLogSerializer,
    DrinkFromPresetSerializer,
    DrinkSerializer,
    PresetDrinkSerializer,
    SleepLogSerializer,
)

# 임시로 추가
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.shortcuts import redirect
from django.urls import reverse

from .constants import DrinkType
from .presets import brands_for_type, menus_for_brand_and_type, sizes_for_drink


class DrinkListCreateView(generics.ListCreateAPIView):
    """음료 목록 조회 / 직접 입력 생성.

    GET  /users/me/drinks/   - 본인의 활성 음료 목록
    POST /users/me/drinks/   - 직접 입력으로 음료 생성

    생성 시 user는 클라이언트 값을 신뢰하지 않고 serializer가 context의
    request.user로 주입한다.
    """

    serializer_class = DrinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """본인의 활성 음료만, 즐겨찾기 우선 최신순으로 반환한다."""
        return (
            Drink.objects.filter(user=self.request.user, is_active=True)
            .order_by("-is_favorite", "-created_at")
        )


class DrinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """음료 상세 조회 / 수정 / 삭제.

    GET    /users/me/drinks/<id>/   - 상세 조회
    PATCH  /users/me/drinks/<id>/   - 수정 (즐겨찾기 토글 등)
    DELETE /users/me/drinks/<id>/   - 소프트 삭제

    쿼리셋을 본인 소유 + 활성 음료로 제한하므로, 타인의 음료나 이미 삭제된
    음료에 접근하면 404가 된다.
    """

    serializer_class = DrinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Drink.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        """DB에서 지우지 않고 is_active=False로 소프트 삭제한다.

        과거 CaffeineLog가 drink_id로 이 행을 참조하므로 실제 삭제하지
        않는다. 되살리기는 serializer의 _create_or_revive가 담당한다.
        """
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class PresetDrinkListView(generics.ListAPIView):
    """프리셋 카탈로그 조회 (읽기 전용).

    GET /users/me/drinks/presets/                    - 전체 프리셋
    GET /users/me/drinks/presets/?type=coffee        - 특정 종류만
    GET /users/me/drinks/presets/?brand=starbucks    - 특정 브랜드만
    GET /users/me/drinks/presets/?type=coffee&brand=starbucks - 둘 다 적용

    카탈로그는 DB 행이 아니라 상수이므로 (브랜드, 음료, 사이즈) leaf 단위로
    펼쳐 반환한다. 카페인량이 아직 입력되지 않은 사이즈는 제외된다.    """

    serializer_class = PresetDrinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        brand = self.request.query_params.get("brand")
        drink_type = self.request.query_params.get("type")

        presets = iter_presets(brand_code=brand)
        if drink_type:
            presets = (p for p in presets if p["type"] == drink_type)
        return list(presets)


class DrinkFromPresetView(generics.CreateAPIView):
    """프리셋을 골라 내 음료로 담기.

    POST /users/me/drinks/from-preset/

    클라이언트는 (브랜드, 음료명, 사이즈)만 보내고 카페인량은 서버가
    카탈로그에서 채운다. 응답은 DrinkSerializer 형식(id, caffeine_mg 포함)이라
    바로 카페인 로그를 남길 수 있다.
    """

    serializer_class = DrinkFromPresetSerializer
    permission_classes = [permissions.IsAuthenticated]

class CaffeineLogPagination(PageNumberPagination):
    """섭취기록 목록 페이지네이션.

    page_size_query_param을 열어 클라이언트가 page_size로 페이지 크기를
    조절할 수 있게 한다(명세: page, page_size). max_page_size로 과도한
    조회를 막는다.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CaffeineLogListCreateView(generics.ListCreateAPIView):
    """섭취기록 목록 조회 / 생성(한잔·커스텀).

    GET  /caffeine-logs/   - 본인 기록 목록(최신순). start_date~end_date로
                             기간을 좁히고 page/page_size로 페이지네이션한다.
    POST /caffeine-logs/   - 한잔(drink_id) 또는 커스텀(caffeine_mg+name) 기록

    기간 필터는 created_at의 날짜(서버 타임존 Asia/Seoul) 기준이다.
    start_date/end_date는 YYYY-MM-DD 형식이며 파싱에 실패하면 무시한다.
    """

    serializer_class = CaffeineLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CaffeineLogPagination

    def get_queryset(self):
        """본인 기록만 최신순으로, 요청된 기간으로 좁혀 반환한다."""
        qs = CaffeineLog.objects.filter(user=self.request.user).order_by("-created_at")

        start = parse_date(self.request.query_params.get("start_date", "") or "")
        end = parse_date(self.request.query_params.get("end_date", "") or "")
        if start:
            qs = qs.filter(created_at__date__gte=start)
        if end:
            qs = qs.filter(created_at__date__lte=end)
        return qs


class CaffeineLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """섭취기록 상세 조회 / 수정 / 삭제.

    GET    /caffeine-logs/<id>/   - 상세 조회
    PATCH  /caffeine-logs/<id>/   - 수정(커스텀 값 정정 등)
    DELETE /caffeine-logs/<id>/   - 삭제

    쿼리셋을 본인 소유로 제한하므로 타인의 기록에 접근하면 404가 된다.
    """

    serializer_class = CaffeineLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CaffeineLog.objects.filter(user=self.request.user)


class SleepLogPagination(PageNumberPagination):
    """수면기록 목록 페이지네이션. CaffeineLogPagination과 동일한 규칙."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class SleepLogListCreateView(generics.ListCreateAPIView):
    """수면기록 목록 조회 / 생성.

    GET  /sleep-logs/   - 본인 기록 목록(최신순). start_date~end_date로
                          기간을 좁히고 page/page_size로 페이지네이션한다.
    POST /sleep-logs/   - 수면기록 생성(명세 SLEEP-002, "수면 설문 입력"). 하루
                          1회만 허용하며, actual_bedtime을 보내면 그 시각의
                          잔류 카페인량과 갱신된 개인화 θ를 함께 계산해 저장한다.

    기간 필터는 created_at의 날짜(서버 타임존 Asia/Seoul) 기준이다.
    start_date/end_date는 YYYY-MM-DD 형식이며 파싱에 실패하면 무시한다.
    """

    serializer_class = SleepLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SleepLogPagination

    def get_queryset(self):
        """본인 기록만 최신순으로, 요청된 기간으로 좁혀 반환한다."""
        qs = SleepLog.objects.filter(user=self.request.user).order_by("-created_at")

        start = parse_date(self.request.query_params.get("start_date", "") or "")
        end = parse_date(self.request.query_params.get("end_date", "") or "")
        if start:
            qs = qs.filter(created_at__date__gte=start)
        if end:
            qs = qs.filter(created_at__date__lte=end)
        return qs

    def create(self, request, *args, **kwargs):
        """오늘자 수면기록이 이미 있으면 409로 막는다(명세: 하루 1회 제출).

        생성에 성공하면, 방금 만든 기록까지 반영한 개인화 진행도(θ, 설문
        누적 수, 가중치)를 응답에 함께 실어 CALC-005 갱신 결과를 바로
        보여준다.

        경계는 "서비스일 시작 이후 생성된 행"이라는 계산값이라(저장된 컬럼이
        아니다) DB UniqueConstraint로 못 막는다. 동시에 두 번 요청하면 이론상
        둘 다 생성될 수 있다 — Drink._create_or_revive의 최초 생성 경합과
        같은 급의, 확률이 매우 낮고 결과도 파괴적이지 않은(개인화 평균이
        하루치 더 들어가는 정도) 레이스라 지금은 감수한다.
        """
        today, day_start = service_day_bounds(timezone.now())
        if SleepLog.objects.filter(user=request.user, created_at__gte=day_start).exists():
            return Response(
                {
                    "code": "DAILY_LOG_ALREADY_EXISTS",
                    "message": "오늘의 수면 기록이 이미 저장되었습니다.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        response = super().create(request, *args, **kwargs)

        theta = theta_for_user(request.user)
        response.data["threshold_mg"] = theta.theta_mg
        response.data["daily_log_count"] = theta.n_records
        response.data["personalization_weight"] = theta.weight
        return response


class SleepLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """수면기록 상세 조회 / 수정 / 삭제.

    GET    /sleep-logs/<id>/   - 상세 조회
    PATCH  /sleep-logs/<id>/   - 수정 (actual_bedtime 변경 시 잔류량 재계산)
    DELETE /sleep-logs/<id>/   - 삭제

    쿼리셋을 본인 소유로 제한하므로 타인의 기록에 접근하면 404가 된다.
    """

    serializer_class = SleepLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SleepLog.objects.filter(user=self.request.user)


class FeedStatusView(APIView):
    """메인피드용 계산 결과 조회.

    GET /feed-status/   - CALC-001(잔류량+그래프), CALC-002(마감시각),
                          CALC-003(남은허용량/잔수), CALC-005(개인화 θ),
                          CALC-006(한계효용)을 이 안에서 호출해 한 번에 내려준다.
                          ?compact=true면 drinks/graph를 생략한다.

    명세(Notion API 명세서) URI는 /feed이지만, 그 경로는 diary/urls.py의
    "feed/"에서 프론트가 작업 중인 HTML 화면(FeedView)이 이미 쓰고 있다.
    같은 경로에 화면(HTML)과 데이터(JSON)를 동시에 둘 수 없어, 프론트와
    최종 경로를 맞추기 전까지 feed-status/에 임시로 둔다.

    선행조건: UserProfile 존재. 없으면 404 PROFILE_NOT_FOUND.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {
                    "code": "PROFILE_NOT_FOUND",
                    "message": "프로필이 없습니다.",
                    "next": "/signup/profile",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        compact = request.query_params.get("compact", "").lower() == "true"
        now = timezone.now()
        local_now = timezone.localtime(now)
        today, day_start = service_day_bounds(now)

        sleep_survey_required = self._sleep_survey_required(user, local_now, today, day_start)
        night_session_active = AllNightSession.objects.filter(
            user=user, status=AllNightSession.Status.ACTIVE
        ).exists()

        theta_mg = theta_for_user(user).theta_mg
        doses = doses_for_user(user, now, since=day_start)
        today_total_mg = sum(d.amount_mg for d in doses)
        current_mg = round(concentration_at(doses, now), 1)

        bedtime = resolve_next_occurrence(profile.target_sleeptime, now)
        ref_dose = reference_dose_mg(user)

        cutoff_result = calc_cutoff(now, bedtime, ref_dose, doses, theta_mg)
        allowance_result = calc_allowance(bedtime, doses, theta_mg, ref_dose)
        marginal_result = calc_marginal_utility(today_total_mg, ref_dose, profile.body_weight_kg)

        warnings = []
        if cutoff_result.status in (CutoffStatus.OVER_THRESHOLD, CutoffStatus.CUTOFF_PASSED):
            warnings.append(
                {"code": "CUTOFF_EXCEEDED", "message": "오늘의 카페인 마감시간이 지났습니다."}
            )
        if marginal_result.over_daily_limit:
            warnings.append(
                {"code": "DAILY_LIMIT_EXCEEDED", "message": "일일 권장 상한을 초과했습니다."}
            )
        elif marginal_result.negligible:
            warnings.append(
                {"code": "MARGINAL_EFFECT", "message": "추가 섭취는 각성 효과가 거의 없습니다."}
            )

        cutoff_at_local = timezone.localtime(cutoff_result.cutoff_at) if cutoff_result.cutoff_at else None

        data = {
            "date": today.isoformat(),
            "now": local_now.isoformat(),
            "sleep_survey_required": sleep_survey_required,
            "night_session_active": night_session_active,
            "target_bedtime": profile.target_sleeptime.strftime("%H:%M"),
            "threshold_mg": theta_mg,
            "current_mg": current_mg,
            "cutoff_at": cutoff_at_local.isoformat() if cutoff_at_local else None,
            "remaining_mg": allowance_result.remaining_mg,
            "remaining_cups": allowance_result.cups,
            "today_total_mg": round(today_total_mg, 1),
            "today_log_count": len(doses),
            "marginal": {
                "g_pd_min": marginal_result.g_pd_after,
                "delta_g": marginal_result.delta_g,
                "warning": marginal_result.warning is not None,
            },
            "warnings": warnings,
        }

        if not compact:
            data["drinks"] = [
                {"drink_id": d.id, "name": d.name, "caffeine_mg": d.caffeine_mg}
                for d in Drink.objects.filter(user=user, is_active=True)
            ]
            data["graph"] = build_curve_payload(
                doses,
                start=day_start,
                threshold_mg=theta_mg,
                threshold_role="max",
                now=now,
                bedtime=bedtime,
                cutoff_at=cutoff_result.cutoff_at,
            )

        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def _sleep_survey_required(user, local_now, today, day_start):
        """SLEEP-001: 수면설문 노출 판정.

        가입 당일, 서비스일 경계(05:00) 이전, 오늘자 SleepLog가 이미 있거나,
        전날(어제 서비스일) 밤샘모드였으면 노출하지 않는다 — 밤샘일은 수면
        데이터가 없으므로 다음날 설문을 건너뛴다(NIGHT-003).

        local_now는 서버 로컬시각(Asia/Seoul)으로 변환된 값이어야 한다.
        date_joined는 DB에 UTC로 저장되므로 비교 전에 같은 방식으로 변환한다.
        """
        if service_date(timezone.localtime(user.date_joined)) == today:
            return False
        if local_now.hour < SERVICE_DAY_START_HOUR:
            return False
        if SleepLog.objects.filter(user=user, created_at__gte=day_start).exists():
            return False
        yesterday_start = day_start - timedelta(hours=24)
        if AllNightSession.objects.filter(
            user=user, started_at__gte=yesterday_start, started_at__lt=day_start
        ).exists():
            return False
        return True


# main(맨 처음 들어갔을 때 화면) view 추가 (임시)
class MainView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/main.html"
    extra_context = {"page_title": "메인 화면"}


# feed(한잔마시기) view 추가 (임시))
class FeedView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/feed.html"
    extra_context = {"page_title": "피드 화면"}

# 수면 설문
class SleepLogTimeView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/daily_time.html"


class SleepLogRatingView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/daily_rating.html"
   
# intial_survey view 추가 (임시)

class SurveyStartView(LoginRequiredMixin, RedirectView):
    login_url = "/auth/login"
    pattern_name = "diary:survey-category"


class SurveyCategoryView(LoginRequiredMixin, TemplateView):
    """1단계: 음료 카테고리 선택. 첫 단계라 prev_url을 안 넣는다 """

    login_url = "/auth/login"
    template_name = "diary/survey_category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["options"] = DrinkType.choices
        return context

    def post(self, request, *args, **kwargs):
        request.session["survey_category"] = request.POST.get("choice")
        for key in ("survey_brand", "survey_menu", "survey_size"):
            request.session.pop(key, None)
        return redirect("diary:survey-brand")


class SurveyBrandView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/survey_brand.html"

    def get(self, request, *args, **kwargs):
        if not request.session.get("survey_category"):
            return redirect("diary:survey-category")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.request.session.get("survey_category")
        brands = brands_for_type(category) if category else []
        context["options"] = [(b["code"], b["name"]) for b in brands]
        context["prev_url"] = reverse("diary:survey-category")
        return context

    def post(self, request, *args, **kwargs):
        request.session["survey_brand"] = request.POST.get("choice")
        for key in ("survey_menu", "survey_size"):
            request.session.pop(key, None)
        return redirect("diary:survey-menu")


class SurveyMenuView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/survey_menu.html"

    def get(self, request, *args, **kwargs):
        if not request.session.get("survey_brand"):
            return redirect("diary:survey-brand")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.request.session.get("survey_category")
        brand = self.request.session.get("survey_brand")
        menus = menus_for_brand_and_type(brand, category) if brand and category else []
        context["options"] = [(d["name"], d["name"]) for d in menus]
        context["prev_url"] = reverse("diary:survey-brand")
        return context

    def post(self, request, *args, **kwargs):
        request.session["survey_menu"] = request.POST.get("choice")
        request.session.pop("survey_size", None)
        return redirect("diary:survey-size")


class SurveySizeView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/survey_size.html"

    def get(self, request, *args, **kwargs):
        if not request.session.get("survey_menu"):
            return redirect("diary:survey-menu")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = self.request.session.get("survey_brand")
        menu = self.request.session.get("survey_menu")
        sizes = sizes_for_drink(brand, menu) if brand and menu else []
        context["options"] = [(s["code"], s["label"]) for s in sizes]
        context["prev_url"] = reverse("diary:survey-menu")
        return context

    def post(self, request, *args, **kwargs):
        request.session["survey_size"] = request.POST.get("choice")
        return redirect("diary:survey-sleep")


class SurveySleepView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login"
    template_name = "diary/survey_sleep.html"
