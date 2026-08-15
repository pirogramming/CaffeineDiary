# allnight/serializers.py
"""allnight 앱 시리얼라이저.

AllNightSession(밤샘모드) 응답은 매번 calcs 엔진(CALC-001·004·006) 계산
결과를 조합한 커스텀 페이로드라 ModelSerializer로 그대로 노출하지 않는다.
여기서는 입력값 검증만 담당하고, 조합된 응답은 views.py에서 직접 만든다.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

MAX_SESSION_HOURS = 24


class NightSessionStartSerializer(serializers.Serializer):
    """밤샘모드 시작 입력(NIGHT-001).

    깨어있어야 하는 목표 시각(target_awake_until) 하나만 받는다. 하한·상한
    농도(C_min/C_max)와 일일 상한은 서버 상수라 클라이언트가 정하지 않는다.
    """

    target_awake_until = serializers.DateTimeField()

    def validate_target_awake_until(self, value):
        """과거 시각과 24시간을 초과하는 목표 시각을 막는다.

        Args:
            value (datetime): 목표 시각

        Returns:
            datetime: 검증을 통과한 값

        Raises:
            serializers.ValidationError: 과거이거나 24시간을 초과한 경우
        """
        now = timezone.now()
        if value <= now:
            raise serializers.ValidationError("목표 시각은 현재 이후여야 합니다.")
        if value - now > timedelta(hours=MAX_SESSION_HOURS):
            raise serializers.ValidationError("목표 시각은 현재부터 24시간 이내여야 합니다.")
        return value


class NightSessionEndSerializer(serializers.Serializer):
    """밤샘모드 종료 입력(NIGHT-003). status는 "ended"만 허용한다."""

    status = serializers.CharField()

    def validate_status(self, value):
        if value != "ended":
            raise serializers.ValidationError("status는 ended만 허용됩니다.")
        return value
