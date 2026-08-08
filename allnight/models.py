from django.conf import settings
from django.db import models

class AllNightSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="allnight_sessions",
    )
    status = models.CharField(max_length=20, default="active")  # 세션상태: NULL/ACTIVE/ABORTED/COMPLETED 
    started_at = models.DateTimeField()                      # 시작 날짜
    ended_at = models.DateTimeField(null=True, blank=True)  # 종료 날짜
    target_time = models.DateTimeField(default=False)       # 목표 종료 시각
    is_active = models.BooleanField(default=False)  # 밤샘모드 여부

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.target_time:%m-%d %H:%M}"