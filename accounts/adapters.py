# accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_username
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.base import AuthError
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import UserProfile


class AccountAdapter(DefaultAccountAdapter):
    """소셜 로그인(카카오 등)의 로그인 후 리다이렉트 목적지를 정한다.

    일반 로그인(accounts.views.login)은 allauth를 거치지 않는 자체 API라
    "next": "/" if has_profile else "/signup/profile" 을 프론트가 직접
    처리하지만, 소셜 로그인은 allauth의 로그인 완료 흐름을 그대로 타서
    이 어댑터가 없으면 LOGIN_REDIRECT_URL(마케팅 첫 화면 "/")로 떨어진다.
    """

    def get_login_redirect_url(self, request):
        if UserProfile.objects.filter(user=request.user).exists():
            return reverse("diary:feed")
        return reverse("diary:survey-start")


class KakaoSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # allauth 기본값은 카카오 닉네임 기반 username이라 자체 계정과 네임스페이스가 뒤섞인다.
        user_username(user, f"kakao_{sociallogin.account.uid}")
        return user

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        code = "KAKAO_AUTH_DENIED" if error == AuthError.CANCELLED else "SOCIAL_AUTH_FAILED"
        raise ImmediateHttpResponse(HttpResponseRedirect(f"/login?error={code}"))
