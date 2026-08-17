from django.conf import settings
from django.db import models

class AllNightSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "진행중"
        COMPLETED = "completed", "종료"
        ABORTED = "aborted", "중단"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="allnight_sessions",
    )

    started_at = models.DateTimeField()                      # 시작 날짜
    ended_at = models.DateTimeField(null=True, blank=True)  # 종료 날짜
    target_time = models.DateTimeField()       # 목표 종료 시각

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status="active"),
                name="uniq_active_session_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user.username} | {self.target_time:%m-%d %H:%M}"