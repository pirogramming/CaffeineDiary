from django.db import models
from django.conf import settings

# Create your models here.
class Drink(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="drinks",
    )
    caffeine_mg = models.FloatField()                       # 1회 제공량 기준 카페인
    is_favorite = models.BooleanField(default=False)          # 즐겨찾기 음료 여부
    is_recent = models.BooleanField(default=False)            # 최근 섭취 음료 여부
    type = models.CharField(max_length=50, blank=True)  # 커피/차/탄산/에너지드링크
    brand = models.CharField(max_length=100, blank=True)      
    name = models.CharField(max_length=100)    
    size = models.CharField(max_length=50, blank=True)  # 용량/사이즈 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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