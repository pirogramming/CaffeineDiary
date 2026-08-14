from django.conf import settings
from django.db import models

from .constants import Brand, DrinkType


class Drink(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="drinks",
    )
    caffeine_mg = models.PositiveSmallIntegerField()   # 1회 제공량 기준

    type = models.CharField(
        max_length=20, choices=DrinkType.choices, default=DrinkType.COFFEE
    )
    brand = models.CharField(
        max_length=20, choices=Brand.choices, default=Brand.CUSTOM
    )
    custom_brand_name = models.CharField(max_length=100, blank=True)  # brand=custom일 때만 사용하는 자유 입력 브랜드명
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50, blank=True)  # 브랜드별 라벨, 검증은 serializer

    is_favorite = models.BooleanField(default=False)
    is_recent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)       # 소프트 삭제
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "brand", "custom_brand_name", "name", "size"],
                condition=models.Q(is_active=True),
                name="uniq_active_drink_per_user",
            )
        ]

class CaffeineLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="caffeine_logs",
    )
    drink = models.ForeignKey(
        Drink,
        on_delete=models.SET_NULL,   # Drink 삭제돼도 아래 스냅샷은 유지
        null=True, blank=True,
        related_name="logs",
    )
    name = models.CharField(max_length=100, blank=True)  # 스냅샷: 기록 시점 음료명(커스텀/Drink 삭제 대비)
    caffeine_mg = models.FloatField()        # 스냅샷: 기록 시점 카페인량

    created_at = models.DateTimeField(auto_now_add=True)

class SleepLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sleep_logs",
    )
    sleep_quality = models.PositiveSmallIntegerField(null=True, blank=True)  # 수면질 1~5 설문
    actual_bedtime = models.DateTimeField(null=True, blank=True)
    wakeup_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)