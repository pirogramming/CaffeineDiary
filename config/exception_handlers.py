# config/exception_handlers.py
"""DRF 예외를 API 명세서 공통 에러 포맷({code, message, errors})으로 통일한다.

미결 사항이었던 항목: 400(ValidationError)이 DRF 기본 포맷
({"field": ["메시지"]})으로 그대로 나가던 문제. 여기서 공통 포맷으로 바꾼다.
"""
from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,
    PermissionDenied,
    ValidationError,
    NotFound,
)
from rest_framework import status


def _stringify(detail):
    """DRF ErrorDetail의 중첩 dict/list 구조를 사람이 읽을 문자열 하나로 합친다."""
    if isinstance(detail, dict):
        parts = [f"{key}: {_stringify(value)}" for key, value in detail.items() if value]
        return "; ".join(parts)
    if isinstance(detail, list):
        return "; ".join(_stringify(item) for item in detail if item)
    return str(detail)


def _flatten_errors(detail):
    """최상위는 {field: "message"} 형태를 유지하고, 필드 안쪽은 문자열로 합친다.

    serializer.is_valid(raise_exception=True)로 발생한 ValidationError는
    항상 최상위가 dict(필드명 또는 non_field_errors 키)다. 방어적으로 dict가
    아닌 경우(직접 raise한 경우 등)는 non_field_errors 하나로 감싼다.
    """
    if isinstance(detail, dict):
        return {key: _stringify(value) for key, value in detail.items()}
    return {"non_field_errors": _stringify(detail)}


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

    # 입력 검증 실패: 400
    elif isinstance(exc, ValidationError):
        response.data = {
            "code": "INVALID_INPUT",
            "message": "입력값을 확인해주세요.",
            "errors": _flatten_errors(exc.detail),
        }

    # 리소스 없음: 404. DRF 제네릭 뷰의 get_object()는 django.http.Http404를
    # 던지므로(rest_framework.exceptions.NotFound가 아니다) 둘 다 잡는다.
    # 뷰에서 code를 직접 지정하는 404(PROFILE_NOT_FOUND 등)는 Response()를
    # 바로 반환하므로 예외 처리기를 거치지 않아 여기와 겹치지 않는다.
    elif isinstance(exc, (Http404, NotFound)):
        response.data = {
            "code": "NOT_FOUND",
            "message": "요청한 리소스를 찾을 수 없습니다.",
        }

    return response