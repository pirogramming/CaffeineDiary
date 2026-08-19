"""accounts 앱 테스트.

회원가입(/auth/signup/) API와 UserProfile API(/users/me/profile/)의 계약을
고정한다. 회원가입 쪽은 특히 신뢰 경계(중복 아이디, 비밀번호 정책) 검증이
회귀하면 500 크래시로 이어지므로 반드시 지킨다.
"""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from diary.models import Drink

from .models import UserProfile

User = get_user_model()


class SignupAPITests(APITestCase):
    """POST /auth/signup/ 계약."""

    def setUp(self):
        self.url = reverse("signup")

    def _body(self, **overrides):
        body = {
            "username": "coffeelover",
            "password": "Str0ng-Pass!",
            "password_confirm": "Str0ng-Pass!",
        }
        body.update(overrides)
        return body

    def test_signup_creates_user_and_logs_in(self):
        """유효한 입력으로 가입하면 201, 세션이 생성되고 has_profile은 false다."""
        res = self.client.post(self.url, self._body(), format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertFalse(res.data["has_profile"])
        self.assertEqual(res.data["next"], "/signup/profile")
        self.assertTrue(User.objects.filter(username="coffeelover").exists())

        session_res = self.client.get(reverse("session"))
        self.assertTrue(session_res.data["is_authenticated"])

    def test_signup_requires_username(self):
        """username이 없으면 400."""
        res = self.client.post(self.url, self._body(username=""), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["code"], "INVALID_INPUT")

    def test_signup_requires_password(self):
        """password가 없으면 400."""
        body = self._body()
        del body["password"]
        res = self.client.post(self.url, body, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_rejects_password_mismatch(self):
        """password와 password_confirm이 다르면 400."""
        res = self.client.post(
            self.url, self._body(password_confirm="Different-1"), format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", res.data["errors"])

    def test_signup_rejects_weak_password(self):
        """비밀번호 정책(최소 길이 등)을 위반하면 400."""
        res = self.client.post(
            self.url, self._body(password="123", password_confirm="123"), format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", res.data["errors"])

    def test_signup_duplicate_username_rejected(self):
        """이미 있는 아이디로 가입하면 409, 새 계정이 생기지 않는다."""
        User.objects.create_user(username="coffeelover", password="pw12345!")
        res = self.client.post(self.url, self._body(), format="json")
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data["code"], "USERNAME_ALREADY_EXISTS")
        self.assertEqual(User.objects.filter(username="coffeelover").count(), 1)


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
        self.assertEqual(res.data["nickname"], "tester")
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

    def test_duplicate_profile_blocked_at_db_level(self):
        """UserProfile.user는 OneToOneField라 DB 차원에서 유일하다.

        존재 확인(exists 체크)과 생성 사이의 경합에서 view의 try/except가
        기대는 바로 이 제약이다.
        """
        self._create_profile()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserProfile.objects.create(
                    user=self.user, target_sleeptime=timezone.now().time(), body_weight_kg=60
                )

    def test_post_requires_body_weight_kg(self):
        """체중이 없으면 400 (명세 PROF-001: 생성 시 필수)."""
        res = self.client.post(
            self.url,
            {"target_bedtime": "23:30", "drinks": [{"name": "a", "caffeine_mg": 100}]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("body_weight_kg", res.data["errors"])

    def test_post_rejects_out_of_range_body_weight(self):
        """비현실적인 체중(음수 등)은 400."""
        res = self._create_profile(body_weight_kg=-5)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("body_weight_kg", res.data["errors"])

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

    def test_patch_nickname_keeps_username_unchanged(self):
        """닉네임은 아이디와 독립적으로 변경할 수 있다."""
        self._create_profile()
        res = self.client.patch(self.url, {"nickname": "커피러버"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["nickname"], "커피러버")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "tester")

    def test_patch_bedtime_change_recomputes_cutoff(self):
        """target_bedtime을 바꾸면 CALC-002가 재계산되어 cutoff_at이 채워진다.

        old_bedtime(기본값 23:30 KST)의 마감시각이 이미 지났으면 "tomorrow" 분기로
        빠지므로(PROF-002), 실행 시각(KST)에 좌우되지 않도록 09:00 KST로 고정해
        old_bedtime의 마감시각이 항상 아직 남아있는 상태에서 검증한다.
        """
        self._create_profile()  # target_bedtime 기본값 23:30
        fixed_local_now = timezone.localtime(timezone.now()).replace(
            hour=9, minute=0, second=0, microsecond=0
        )
        fixed_now = fixed_local_now.astimezone(timezone.UTC)
        future_bedtime = (fixed_local_now + timedelta(hours=5)).strftime("%H:%M")

        with patch("accounts.views.timezone.now", return_value=fixed_now):
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
