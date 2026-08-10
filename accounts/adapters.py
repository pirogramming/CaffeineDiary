# accounts/adapters.py
from allauth.account.utils import user_username
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.base import AuthError
from django.http import HttpResponseRedirect


class KakaoSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # allauth 기본값은 카카오 닉네임 기반 username이라 자체 계정과 네임스페이스가 뒤섞인다.
        user_username(user, f"kakao_{sociallogin.account.uid}")
        return user

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        code = "KAKAO_AUTH_DENIED" if error == AuthError.CANCELLED else "SOCIAL_AUTH_FAILED"
        raise ImmediateHttpResponse(HttpResponseRedirect(f"/login?error={code}"))
