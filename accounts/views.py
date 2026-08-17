# accounts/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from calcs.cutoff import calc_cutoff
from calcs.pharmacokinetics import resolve_next_occurrence
from diary.calc_bridge import doses_for_user, reference_dose_mg, theta_for_user
from diary.models import Drink

from .models import UserProfile
from .serializers import SignupSerializer, UserProfileSerializer
from django.views.generic import TemplateView

# Create your views here.

def _has_profile(user) -> bool:
    return UserProfile.objects.filter(user=user).exists()

# 회원가입
@api_view(["POST"])
@permission_classes([AllowAny])   # 공개 엔드포인트
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    # 흔한 경로는 여기서 먼저 걸러 불필요한 IntegrityError를 피하고,
    # 동시 요청으로 인한 경합은 아래 create_user()의 IntegrityError로 막는다
    # (DB의 username UNIQUE 제약이 최종 방어선이다).
    if User.objects.filter(username=username).exists():
        return Response(
            {"code": "USERNAME_ALREADY_EXISTS", "message": "이미 사용 중인 아이디입니다."},
            status=status.HTTP_409_CONFLICT,
        )

    try:
        user = User.objects.create_user(username=username, password=password)
    except IntegrityError:
        return Response(
            {"code": "USERNAME_ALREADY_EXISTS", "message": "이미 사용 중인 아이디입니다."},
            status=status.HTTP_409_CONFLICT,
        )

    auth_login(request, user)  # 가입직후 세션 생성

    return Response(
        {"user_id": user.id, "username": user.username,
         "has_profile": False, "next": "/signup/profile"},
        status=status.HTTP_201_CREATED,
    )

# 로그인
@api_view(["POST"])
@permission_classes([AllowAny])   # 공개 엔드포인트
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    # 400: 필수값 누락
    if not username or not password:
        return Response(
            {"code": "INVALID_INPUT",
             "message": "아이디와 비밀번호를 모두 입력해주세요."
             },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    user = authenticate(request, username=username, password=password)

    if user is None:    # 401: 인증 실패
        return Response(
            {"code": "INVALID_CREDENTIALS",
            "message": "아이디 또는 비밀번호가 일치하지 않습니다."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    auth_login(request, user)  # 로그인 성공 시 세션 생성
    has_profile = _has_profile(user)  # 프로필 존재 여부 확인
    return Response(
        {"user_id": user.id, "username": user.username,
         "has_profile": has_profile, "next": "/" if has_profile else "/signup/profile"},
         status=status.HTTP_200_OK,
    )

# 로그아웃
@api_view(["POST"])
@permission_classes([IsAuthenticated])  
def logout(request):
    auth_logout(request)  # 세션 삭제
    return Response(
        {"success": True, "night_session_active": True, "next": "/"},
        status=status.HTTP_200_OK
    )

# 세션 확인
@api_view(["GET"])
@permission_classes([AllowAny])   
@ensure_csrf_cookie
def session(request):
    # 미인증
    if not request.user.is_authenticated:
        return Response(
            {"is_authenticated": False, "user_id": None,
             "has_profile": False, "next": "/auth/login"},
            status=status.HTTP_200_OK,
        )

    # 인증됨
    has_profile = _has_profile(request.user)
    return Response(
        {"is_authenticated": True, "user_id": request.user.id,
         "has_profile": has_profile, "next": "/" if has_profile else "/signup/profile"},
        status=status.HTTP_200_OK,
    )


def _serialize_profile(profile, *, include_calc=True):
    """UserProfile을 명세(GET /users/me/profile) 응답 형태로 변환한다.

    include_calc=False는 PATCH 응답처럼 threshold_mg/daily_log_count/drinks가
    필요 없는 경우에 계산 비용을 아끼기 위한 것이다.
    """
    data = {
        "profile_id": profile.id,
        "username": profile.user.username,
        "target_bedtime": profile.target_sleeptime.strftime("%H:%M"),
        "body_weight_kg": profile.body_weight_kg,
    }
    if include_calc:
        theta = theta_for_user(profile.user)
        drinks = Drink.objects.filter(user=profile.user, is_active=True)
        data["threshold_mg"] = theta.theta_mg
        data["daily_log_count"] = theta.n_records
        data["drinks"] = [
            {"drink_id": d.id, "name": d.name, "caffeine_mg": d.caffeine_mg} for d in drinks
        ]
    return data


# 프로필 조회 / 생성 / 수정
@api_view(["GET", "POST", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    """GET/POST/PATCH /users/me/profile/.

    UserProfile은 사용자당 1개(OneToOne)라 리스트가 아닌 단일 리소스로 다룬다.
    calcs 엔진(CALC-002~003, CALC-005)의 입력값(체중, 목표 취침시각)을 다루므로,
    조회 응답에는 계산된 θ(threshold_mg)와 설문 누적 수(daily_log_count)도 함께 싣는다.
    """
    existing = UserProfile.objects.filter(user=request.user).first()

    if request.method == "GET":
        if existing is None:
            return Response(
                {"code": "PROFILE_NOT_FOUND", "message": "프로필이 없습니다.",
                 "next": "/signup/profile"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(_serialize_profile(existing), status=status.HTTP_200_OK)

    if request.method == "POST":
        if existing is not None:
            return Response(
                {"code": "PROFILE_ALREADY_EXISTS", "message": "이미 프로필이 생성되어 있습니다."},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = UserProfileSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        # 위 existing 체크와 이 save() 사이의 경합은 UserProfile.user가 OneToOneField라
        # DB 차원에서 이미 유일하다 — 동시 요청이 둘 다 통과해도 하나는 여기서 걸린다.
        try:
            new_profile = serializer.save()
        except IntegrityError:
            return Response(
                {"code": "PROFILE_ALREADY_EXISTS", "message": "이미 프로필이 생성되어 있습니다."},
                status=status.HTTP_409_CONFLICT,
            )
        data = _serialize_profile(new_profile, include_calc=False)
        data["drinks"] = [
            {"drink_id": d.id, "name": d.name, "caffeine_mg": d.caffeine_mg}
            for d in Drink.objects.filter(user=request.user, is_active=True)
        ]
        data["next"] = "/"
        return Response(data, status=status.HTTP_201_CREATED)

    # PATCH
    if existing is None:
        return Response(
            {"code": "PROFILE_NOT_FOUND", "message": "프로필이 없습니다.",
             "next": "/signup/profile"},
            status=status.HTTP_404_NOT_FOUND,
        )

    old_bedtime = existing.target_sleeptime
    serializer = UserProfileSerializer(
        existing, data=request.data, partial=True, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    updated = serializer.save()

    data = _serialize_profile(updated, include_calc=False)

    bedtime_changed = "target_bedtime" in request.data and updated.target_sleeptime != old_bedtime
    if not bedtime_changed:
        data["applied_from"] = "today"
        data["cutoff_at"] = None
        return Response(data, status=status.HTTP_200_OK)

    # target_bedtime이 바뀐 경우에만 CALC-002를 재계산한다. 기존(변경 전) 마감시각이
    # 이미 지났으면 오늘 계산엔 개입하지 않고 내일부터 적용한다(명세 PROF-002).
    now = timezone.now()
    doses = doses_for_user(request.user, now)
    theta_mg = theta_for_user(request.user).theta_mg
    ref_dose = reference_dose_mg(request.user)

    old_next_bedtime = resolve_next_occurrence(old_bedtime, now)
    old_result = calc_cutoff(now, old_next_bedtime, ref_dose, doses, theta_mg)

    if old_result.cutoff_at is not None and now > old_result.cutoff_at:
        data["applied_from"] = "tomorrow"
        data["cutoff_at"] = None
        data["message"] = "오늘의 마감시간은 이미 지나 변경은 내일부터 적용됩니다."
        return Response(data, status=status.HTTP_200_OK)

    new_bedtime = resolve_next_occurrence(updated.target_sleeptime, now)
    new_result = calc_cutoff(now, new_bedtime, ref_dose, doses, theta_mg)
    data["applied_from"] = "today"
    data["cutoff_at"] = (
        timezone.localtime(new_result.cutoff_at).isoformat() if new_result.cutoff_at else None
    )
    return Response(data, status=status.HTTP_200_OK)
class LoginPageView(TemplateView): #login page view 추가 
    template_name = "accounts/login.html"


class SignupPageView(TemplateView): #signup page view 추가
    template_name = "accounts/signup.html"
