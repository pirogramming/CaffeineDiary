"""accounts 앱 테스트.

UserProfile API(/users/me/profile/)의 계약을 고정한다.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from diary.models import Drink

from .models import UserProfile

User = get_user_model()


class UserProfileAPITests(APITestCase):
    """/users/me/profile/ 엔드포인트의 생성/조회/수정 계약."""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw12345!")
        self.url = reverse("user-profile")
        self.client.force_authenticate(self.user)

    def _create_profile(self, target_bedtime="23:30", body_weight_kg=65.0, drinks=None):
        if drinks is None:
            drinks = [{"name": "아이스아메리카노", "caffeine_mg": 180}]
        return self.client.post(
            self.url,
            {"target_bedtime": target_bedtime, "body_weight_kg": body_weight_kg, "drinks": drinks},
            format="json",
        )

    # ------------------------------------------------------------------ 생성

    def test_post_creates_profile_and_drinks(self):
        """프로필 생성 시 함께 보낸 음료가 사용자 소유 Drink로 만들어진다."""
        res = self._create_profile(
            drinks=[
                {"name": "아이스아메리카노", "caffeine_mg": 180},
                {"name": "동네 카페 콜드브루", "caffeine_mg": 180},
            ]
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["target_bedtime"], "23:30")
        self.assertEqual(len(res.data["drinks"]), 2)
        self.assertEqual(Drink.objects.filter(user=self.user, is_favorite=True).count(), 2)

    def test_post_requires_at_least_one_drink(self):
        """음료 없이 생성하면 400."""
        res = self._create_profile(drinks=[])
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_rejects_duplicate_drink_names(self):
        """같은 이름의 음료가 중복되면 400."""
        res = self._create_profile(
            drinks=[
                {"name": "아메리카노", "caffeine_mg": 150},
                {"name": "아메리카노", "caffeine_mg": 200},
            ]
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_conflict_when_profile_exists(self):
        """이미 프로필이 있으면 두 번째 POST는 409."""
        self._create_profile()
        res = self._create_profile()
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    # ------------------------------------------------------------------ 조회

    def test_get_without_profile_404(self):
        """프로필 생성 전 조회는 404."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data["code"], "PROFILE_NOT_FOUND")

    def test_get_returns_profile_with_theta_and_drinks(self):
        """설문 기록이 없으면 threshold_mg는 θ_pop(80.0) 기본값이다."""
        self._create_profile()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["threshold_mg"], 80.0)
        self.assertEqual(res.data["daily_log_count"], 0)
        self.assertEqual(len(res.data["drinks"]), 1)

    def test_get_requires_authentication(self):
        """비로그인 요청은 거부된다."""
        self.client.force_authenticate(None)
        res = self.client.get(self.url)
        self.assertIn(
            res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    # ------------------------------------------------------------------ 수정

    def test_patch_without_profile_404(self):
        """프로필 생성 전 수정은 404."""
        res = self.client.patch(self.url, {"body_weight_kg": 70}, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_body_weight_only_does_not_touch_bedtime_calc(self):
        """target_bedtime을 건드리지 않는 수정은 오늘 적용으로 표시되고 cutoff는 계산하지 않는다."""
        self._create_profile()
        res = self.client.patch(self.url, {"body_weight_kg": 70.5}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["body_weight_kg"], 70.5)
        self.assertEqual(res.data["applied_from"], "today")
        self.assertIsNone(res.data["cutoff_at"])

    def test_patch_bedtime_change_recomputes_cutoff(self):
        """target_bedtime을 바꾸면 CALC-002가 재계산되어 cutoff_at이 채워진다."""
        self._create_profile()
        future_bedtime = (timezone.now() + timedelta(hours=5)).strftime("%H:%M")
        res = self.client.patch(self.url, {"target_bedtime": future_bedtime}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["target_bedtime"], future_bedtime)
        self.assertEqual(res.data["applied_from"], "today")
        self.assertIsNotNone(res.data["cutoff_at"])

    def test_patch_updates_underlying_model(self):
        """PATCH 결과가 실제로 DB에 반영된다."""
        self._create_profile()
        self.client.patch(self.url, {"body_weight_kg": 72}, format="json")
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.body_weight_kg, 72)
