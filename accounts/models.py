from django.db import models
from django.conf import settings

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    body_weight_kg = models.FloatField(null=True, blank=True)      
    target_sleeptime = models.TimeField(null=True, blank=True)         
    # 로그인 아이디(username)와 별도로, 마이페이지에서 표시·수정할 이름이다.
    # 생성 시에는 API가 username으로 채우며, 기존 프로필은 마이그레이션에서 보정한다.
    nickname = models.CharField(max_length=150, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True) 

    # TODO: 계산식 등 나중에 작성
    
    def __str__(self):
        return f"{self.user.username} UserProfile"
