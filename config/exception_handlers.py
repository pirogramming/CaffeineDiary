# config/exception_handlers.py
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    # 미인증: DRF 기본 403 -> 401로 변환 
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {"code": "NOT_AUTHENTICATED",
                         "message": "로그인 상태가 아닙니다."}

    # CSRF 실패: 403
    elif isinstance(exc, PermissionDenied):
        response.data = {"code": "CSRF_FAILED",
                         "message": "요청이 유효하지 않습니다. 새로고침 후 다시 시도해주세요."}

    return response