"""allnight 앱 테스트.

밤샘모드(AllNightSession) API(NIGHT-001~003)의 계약을 고정한다.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserProfile
from diary.models import CaffeineLog

from .models import AllNightSession

User = get_user_model()


class NightSessionStartAPITests(APITestCase):
    """POST /night-sessions/ 계약."""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw12345!")
        self.url = reverse("allnight:night-session-start")
        self.client.force_authenticate(self.user)

    def _create_profile(self):
        return UserProfile.objects.create(
            user=self.user, target_sleeptime=timezone.now().time(), body_weight_kg=65.0
        )

    def test_requires_profile(self):
        """프로필이 없으면 404 PROFILE_NOT_FOUND."""
        target = (timezone.now() + timedelta(hours=5)).isoformat()
        res = self.client.post(self.url, {"target_awake_until": target}, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data["code"], "PROFILE_NOT_FOUND")

    def test_start_creates_active_session(self):
        """유효한 목표시각으로 시작하면 201, 활성 세션이 생성된다."""
        self._create_profile()
        target = (timezone.now() + timedelta(hours=5)).isoformat()
        res = self.client.post(self.url, {"target_awake_until": target}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "active")
        self.assertTrue(
            AllNightSession.objects.filter(
                user=self.user, status=AllNightSession.Status.ACTIVE
            ).exists()
        )

    def test_start_rejects_past_target(self):
        """과거 목표시각은 400."""
        self._create_profile()
        target = (timezone.now() - timedelta(hours=1)).isoformat()
        res = self.client.post(self.url, {"target_awake_until": target}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_rejects_over_24h(self):
        """24시간을 초과하는 목표시각은 400."""
        self._create_profile()
        target = (timezone.now() + timedelta(hours=25)).isoformat()
        res = self.client.post(self.url, {"target_awake_until": target}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_conflict_when_already_active(self):
        """이미 활성 세션이 있으면 두 번째 시작은 409."""
        self._create_profile()
        target = (timezone.now() + timedelta(hours=5)).isoformat()
        first = self.client.post(self.url, {"target_awake_until": target}, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(self.url, {"target_awake_until": target}, format="json")
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(second.data["code"], "NIGHT_SESSION_ALREADY_ACTIVE")
        self.assertEqual(
            AllNightSession.objects.filter(
                user=self.user, status=AllNightSession.Status.ACTIVE
            ).count(),
            1,
        )

    def test_duplicate_active_session_blocked_at_db_level(self):
        """uniq_active_session_per_user 제약 확인.

        존재 확인(filter 체크)과 생성 사이의 경합에서 view의 try/except가
        기대는 바로 이 제약이다.
        """
        self._create_profile()
        now = timezone.now()
        AllNightSession.objects.create(
            user=self.user,
            status=AllNightSession.Status.ACTIVE,
            started_at=now,
            target_time=now + timedelta(hours=5),
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AllNightSession.objects.create(
                    user=self.user,
                    status=AllNightSession.Status.ACTIVE,
                    started_at=now,
                    target_time=now + timedelta(hours=6),
                )

    def test_requires_authentication(self):
        """비로그인 요청은 거부된다."""
        self.client.force_authenticate(None)
        target = (timezone.now() + timedelta(hours=5)).isoformat()
        res = self.client.post(self.url, {"target_awake_until": target}, format="json")
        self.assertIn(
            res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )


class NightSessionCurrentAPITests(APITestCase):
    """GET/PATCH /night-sessions/current/ 계약.

    체중을 W_ref(65kg)로 맞춰 default_band()가 (c_min=100, c_max=200)이
    되도록 한다 — Δs가 정확히 반감기(5h)로 고정되는 성질을 이용해 목표시각을
    "지금부터 5시간 뒤"로 두면 스케줄이 정확히 1회차가 되는 결정론적 상황을
    만들 수 있다.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw12345!")
        UserProfile.objects.create(
            user=self.user, target_sleeptime=timezone.now().time(), body_weight_kg=65.0
        )
        self.start_url = reverse("allnight:night-session-start")
        self.current_url = reverse("allnight:night-session-current")
        self.client.force_authenticate(self.user)

    def _start_session(self, hours=5):
        target = (timezone.now() + timedelta(hours=hours)).isoformat()
        res = self.client.post(self.start_url, {"target_awake_until": target}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return AllNightSession.objects.get(id=res.data["session_id"])

    def test_get_without_active_session_404(self):
        """활성 세션이 없으면 404 NIGHT_SESSION_NOT_FOUND."""
        res = self.client.get(self.current_url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data["code"], "NIGHT_SESSION_NOT_FOUND")

    def test_get_returns_schedule_for_active_session(self):
        """목표시각까지 6시간이면 스케줄이 2회차(현재 1회 + 다음 1회)가 된다.

        첫 회차는 "지금 마셔야 할" 시점(s1=now)이라 done=true로 잡히고,
        두 번째 회차(now+5h, Δs=반감기)가 next_dose로 남는다.
        """
        self._start_session(hours=6)
        res = self.client.get(self.current_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "active")
        self.assertEqual(res.data["c_min"], 100.0)
        self.assertEqual(res.data["c_max"], 200.0)
        self.assertEqual(len(res.data["schedule"]), 2)
        self.assertTrue(res.data["schedule"][0]["done"])
        self.assertFalse(res.data["schedule"][1]["done"])
        self.assertEqual(res.data["next_dose_mg"], 100.0)
        self.assertEqual(res.data["total_mg"], 200.0)
        self.assertFalse(res.data["in_target_range"])  # 아직 아무것도 안 마셔서 0mg

    def test_get_auto_terminates_when_target_passed(self):
        """목표시각이 지난 뒤 조회하면 자동종료되고 reached_target=true."""
        now = timezone.now()
        session = AllNightSession.objects.create(
            user=self.user,
            status=AllNightSession.Status.ACTIVE,
            started_at=now - timedelta(hours=6),
            target_time=now - timedelta(minutes=1),
        )
        CaffeineLog.objects.create(user=self.user, caffeine_mg=120, name="테스트")

        res = self.client.get(self.current_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "ended")
        self.assertTrue(res.data["reached_target"])
        self.assertEqual(res.data["total_intake_mg"], 120.0)

        session.refresh_from_db()
        self.assertEqual(session.status, AllNightSession.Status.COMPLETED)
        self.assertIsNotNone(session.ended_at)

    def test_get_requires_authentication(self):
        """비로그인 요청은 거부된다."""
        self.client.force_authenticate(None)
        res = self.client.get(self.current_url)
        self.assertIn(
            res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    def test_patch_ends_active_session(self):
        """수동종료는 200, reached_target=false, 세션은 ABORTED로 저장된다."""
        session = self._start_session(hours=5)
        res = self.client.patch(self.current_url, {"status": "ended"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "ended")
        self.assertFalse(res.data["reached_target"])

        session.refresh_from_db()
        self.assertEqual(session.status, AllNightSession.Status.ABORTED)
        self.assertIsNotNone(session.ended_at)

    def test_patch_without_active_session_404(self):
        """활성 세션이 없으면 404."""
        res = self.client.patch(self.current_url, {"status": "ended"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_rejects_invalid_status(self):
        """status가 ended가 아니면 400."""
        self._start_session(hours=5)
        res = self.client.patch(self.current_url, {"status": "aborted"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_after_manual_end_is_404(self):
        """수동종료 후에는 다시 조회해도 활성 세션이 없으므로 404."""
        self._start_session(hours=5)
        self.client.patch(self.current_url, {"status": "ended"}, format="json")
        res = self.client.get(self.current_url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
