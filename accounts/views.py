# accounts/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

# Create your views here.
# 회원가입
@api_view(["POST"])
@permission_classes([AllowAny])   # 공개 엔드포인트
def signup(request):
    username = request.data.get("username")
    password = request.data.get("password")

    # TODO: 검증 — 필수값 누락, username 중복, 비밀번호 정책 등

    user = User.objects.create_user(username=username, password=password)
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
             "message": "아이디 또는 비밀번호를 모두 입력해주세요."
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
         "has_profile": True, "next": "/" if has_profile else "/signup/profile"},
         status=status.HTTP_200_OK,
    )

# 로그아웃
def logout(request):
    return render(request, "accounts/logout.html")

# 세션 확인
def session(request):
    return render(request, "accounts/session.html")

# 프로필 생성
@login_required
def profile_create(request):
