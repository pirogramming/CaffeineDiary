"""diary 앱 테스트.

섭취기록(CaffeineLog)·수면기록(SleepLog)·메인피드 계산(FeedStatusView) API의
계약을 고정한다. 특히 신뢰 경계 관련 동작(스냅샷 박제, 소유권 격리)은
회귀하면 데이터 위조로 이어지므로 반드시 지킨다.
"""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserProfile
from allnight.models import AllNightSession

from .models import CaffeineLog, Drink, SleepLog

User = get_user_model()


class CaffeineLogAPITests(APITestCase):
    """/caffeine-logs/ 엔드포인트의 생성/조회/수정/삭제 계약."""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw12345!")
        self.other = User.objects.create_user(username="other", password="pw12345!")

        self.drink = Drink.objects.create(
            user=self.user, caffeine_mg=150, name="아메리카노", size="Tall"
        )
        self.other_drink = Drink.objects.create(
            user=self.other, caffeine_mg=99, name="남의커피"
        )

        self.list_url = reverse("diary:log-list")
        self.client.force_authenticate(self.user)

    def detail_url(self, pk):
        return reverse("diary:log-detail", args=[pk])

    # ------------------------------------------------------------------ 생성

    def test_create_from_drink_snapshots_server_side(self):
        """한잔 기록은 클라이언트가 보낸 caffeine_mg/name을 무시하고 서버가 박제한다."""
        res = self.client.post(
            self.list_url,
            {"drink_id": self.drink.id, "caffeine_mg": 5, "name": "위조"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["caffeine_mg"], 150.0)
        self.assertEqual(res.data["name"], "아메리카노")
        self.assertEqual(res.data["drink_id"], self.drink.id)

    def test_create_custom(self):
        """커스텀 기록은 drink 없이 caffeine_mg와 name을 직접 받는다."""
        res = self.client.post(
            self.list_url,
            {"caffeine_mg": 80, "name": "직접입력 콜라"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data["drink_id"])
        self.assertEqual(res.data["name"], "직접입력 콜라")

    def test_create_custom_requires_fields(self):
        """커스텀은 caffeine_mg가 없으면 400."""
        res = self.client.post(self.list_url, {"name": "이름만"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("caffeine_mg", res.data)

    def test_create_custom_rejects_out_of_range(self):
        """카페인량이 범위(1~1000)를 벗어나면 400."""
        res = self.client.post(
            self.list_url, {"caffeine_mg": 5000, "name": "과다"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("caffeine_mg", res.data)

    def test_cannot_log_with_others_drink(self):
        """타인 소유 drink_id로는 기록할 수 없다(후보군에서 제외되어 400)."""
        res = self.client.post(
            self.list_url, {"drink_id": self.other_drink.id}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(CaffeineLog.objects.filter(drink=self.other_drink).exists())

    def test_create_marks_drink_recent(self):
        """기록하면 참조한 음료가 '최근'으로 표시된다."""
        self.assertFalse(self.drink.is_recent)
        self.client.post(self.list_url, {"drink_id": self.drink.id}, format="json")
        self.drink.refresh_from_db()
        self.assertTrue(self.drink.is_recent)

    def test_user_injected_from_request(self):
        """user는 클라이언트가 정할 수 없고 요청 사용자로 주입된다."""
        res = self.client.post(
            self.list_url,
            {"caffeine_mg": 50, "name": "x", "user": self.other.id},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        log = CaffeineLog.objects.get(id=res.data["id"])
        self.assertEqual(log.user, self.user)

    # ------------------------------------------------------------------ 조회

    def test_list_only_own_logs(self):
        """목록은 본인 기록만 반환한다."""
        CaffeineLog.objects.create(user=self.user, caffeine_mg=100, name="내것")
        CaffeineLog.objects.create(user=self.other, caffeine_mg=100, name="남것")

        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["name"], "내것")

    def test_list_pagination(self):
        """page_size로 페이지 크기를 조절할 수 있다."""
        for i in range(3):
            CaffeineLog.objects.create(user=self.user, caffeine_mg=100, name=f"log{i}")

        res = self.client.get(self.list_url, {"page": 1, "page_size": 2})
        self.assertEqual(res.data["count"], 3)
        self.assertEqual(len(res.data["results"]), 2)

    def test_list_date_filter_excludes_out_of_range(self):
        """미래 start_date로 필터하면 0건."""
        CaffeineLog.objects.create(user=self.user, caffeine_mg=100, name="오늘")
        res = self.client.get(self.list_url, {"start_date": "2099-01-01"})
        self.assertEqual(res.data["count"], 0)

    def test_requires_authentication(self):
        """비로그인 요청은 거부된다."""
        self.client.force_authenticate(None)
        res = self.client.get(self.list_url)
        self.assertIn(
            res.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    # ------------------------------------------------------------ 수정/삭제

    def test_patch_updates_custom_value(self):
        """커스텀 기록의 caffeine_mg를 수정할 수 있다."""
        log = CaffeineLog.objects.create(user=self.user, caffeine_mg=80, name="콜라")
        res = self.client.patch(
            self.detail_url(log.id), {"caffeine_mg": 120}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        log.refresh_from_db()
        self.assertEqual(log.caffeine_mg, 120.0)

    def test_patch_does_not_resnapshot_without_drink(self):
        """drink를 다시 지정하지 않는 수정은 기존 스냅샷을 덮어쓰지 않는다."""
        log = CaffeineLog.objects.create(
            user=self.user, drink=self.drink, caffeine_mg=150, name="아메리카노"
        )
        # Drink 값을 바꿔도, drink를 재지정하지 않는 PATCH에는 반영되지 않아야 한다.
        self.drink.caffeine_mg = 999
        self.drink.save(update_fields=["caffeine_mg"])

        res = self.client.patch(
            self.detail_url(log.id), {"name": "메모수정"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        log.refresh_from_db()
        self.assertEqual(log.caffeine_mg, 150.0)  # 스냅샷 유지

    def test_cannot_access_others_log(self):
        """타인의 기록에 접근하면 404."""
        log = CaffeineLog.objects.create(user=self.other, caffeine_mg=100, name="남것")
        res = self.client.get(self.detail_url(log.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_log(self):
        """본인 기록을 삭제할 수 있다."""
        log = CaffeineLog.objects.create(user=self.user, caffeine_mg=100, name="삭제대상")
        res = self.client.delete(self.detail_url(log.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CaffeineLog.objects.filter(id=log.id).exists())

    def test_cannot_delete_others_log(self):
        """타인의 기록은 삭제할 수 없다(404)."""
        log = CaffeineLog.objects.create(user=self.other, caffeine_mg=100, name="남것")
        res = self.client.delete(self.detail_url(log.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(CaffeineLog.objects.filter(id=log.id).exists())


class SleepLogAPITests(APITestCase):
    """/sleep-logs/ 엔드포인트의 생성/조회/수정/삭제 계약.

    반감기 5h를 이용해, 취침 5시간 전에 마신 100mg은 취침시각에 정확히
    절반(50mg)만 남는다는 성질을 잔류량 계산 검증에 활용한다.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw12345!")
        self.other = User.objects.create_user(username="other", password="pw12345!")

        self.list_url = reverse("diary:sleep-log-list")
        self.client.force_authenticate(self.user)

    def detail_url(self, pk):
        return reverse("diary:sleep-log-detail", args=[pk])

    def _log_caffeine_at(self, user, caffeine_mg, taken_at):
        """taken_at 시각에 마신 것으로 간주하는 CaffeineLog를 만든다.

        created_at은 auto_now_add라 생성 시점에 값을 줄 수 없으므로,
        생성 후 queryset.update()로 직접 덮어쓴다(save()를 거치지 않아
        auto_now_add를 우회한다).
        """
        log = CaffeineLog.objects.create(user=user, caffeine_mg=caffeine_mg, name="테스트음료")
        CaffeineLog.objects.filter(id=log.id).update(created_at=taken_at)
        return log

    # ------------------------------------------------------------------ 생성 · 잔류량 계산

    def test_create_without_bedtime_has_no_residual(self):
        """actual_bedtime 없이 생성하면 residual_mg_at_sleep은 null."""
        res = self.client.post(self.list_url, {"sleep_quality": 3}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data["residual_mg_at_sleep"])

    def test_create_computes_residual_from_caffeine_logs(self):
        """취침 5시간 전 100mg 섭취 -> 반감기(5h)만큼 지나 50mg만 남는다."""
        bedtime = timezone.now()
        self._log_caffeine_at(self.user, 100, bedtime - timedelta(hours=5))

        res = self.client.post(
            self.list_url, {"actual_bedtime": bedtime.isoformat()}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(res.data["residual_mg_at_sleep"], 50.0, delta=0.5)

    def test_create_ignores_logs_outside_lookback_window(self):
        """48시간을 훌쩍 넘긴(100시간 전) 섭취는 계산 대상에서 제외된다."""
        bedtime = timezone.now()
        self._log_caffeine_at(self.user, 500, bedtime - timedelta(hours=100))

        res = self.client.post(
            self.list_url, {"actual_bedtime": bedtime.isoformat()}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["residual_mg_at_sleep"], 0.0)

    def test_create_ignores_others_caffeine_logs(self):
        """잔류량 계산은 본인 섭취기록만 반영한다."""
        bedtime = timezone.now()
        self._log_caffeine_at(self.other, 100, bedtime - timedelta(hours=1))

        res = self.client.post(
            self.list_url, {"actual_bedtime": bedtime.isoformat()}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["residual_mg_at_sleep"], 0.0)

    def test_residual_mg_at_sleep_is_read_only(self):
        """클라이언트가 residual_mg_at_sleep을 직접 지정해도 무시된다."""
        res = self.client.post(
            self.list_url, {"residual_mg_at_sleep": 9999}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data["residual_mg_at_sleep"])

    # ------------------------------------------------------------ 하루 1회 제한

    def test_second_post_same_day_rejected(self):
        """같은 서비스일에 두 번째로 POST하면 409 DAILY_LOG_ALREADY_EXISTS."""
        first = self.client.post(self.list_url, {"sleep_quality": 3}, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(self.list_url, {"sleep_quality": 4}, format="json")
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(second.data["code"], "DAILY_LOG_ALREADY_EXISTS")
        self.assertEqual(SleepLog.objects.filter(user=self.user).count(), 1)

    def test_second_post_does_not_block_other_users(self):
        """하루 1회 제한은 사용자별로 독립적이다."""
        self.client.post(self.list_url, {"sleep_quality": 3}, format="json")

        self.client.force_authenticate(self.other)
        res = self.client.post(self.list_url, {"sleep_quality": 3}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_response_includes_personalization_progress(self):
        """생성 응답에 갱신된 θ·설문 누적 수·가중치가 함께 실린다."""
        bedtime = timezone.now()
        self._log_caffeine_at(self.user, 100, bedtime - timedelta(hours=5))

        res = self.client.post(
            self.list_url,
            {"actual_bedtime": bedtime.isoformat(), "sleep_quality": 2},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("threshold_mg", res.data)
        self.assertEqual(res.data["daily_log_count"], 1)
        self.assertGreater(res.data["personalization_weight"], 0)

    # ------------------------------------------------------------------ 검증

    def test_sleep_quality_out_of_range_rejected(self):
        """수면질은 1~5 범위를 벗어나면 400."""
        res = self.client.post(self.list_url, {"sleep_quality": 7}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sleep_quality", res.data)

    def test_wakeup_before_bedtime_rejected(self):
        """기상 시각이 취침 시각보다 앞서면 400."""
        now = timezone.now()
        res = self.client.post(
            self.list_url,
            {
                "actual_bedtime": now.isoformat(),
                "wakeup_time": (now - timedelta(hours=1)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("wakeup_time", res.data)

    def test_future_bedtime_rejected(self):
        """미래 시각의 actual_bedtime은 400."""
        future = timezone.now() + timedelta(hours=1)
        res = self.client.post(
            self.list_url, {"actual_bedtime": future.isoformat()}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("actual_bedtime", res.data)

    def test_patch_future_bedtime_rejected(self):
        """수정 시에도 미래 actual_bedtime은 400."""
        log = SleepLog.objects.create(user=self.user, sleep_quality=3)
        future = timezone.now() + timedelta(hours=1)
        res = self.client.patch(
            self.detail_url(log.id), {"actual_bedtime": future.isoformat()}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ 조회

    def test_list_only_own_logs(self):
        """목록은 본인 기록만 반환한다."""
        SleepLog.objects.create(user=self.user, sleep_quality=3)
        SleepLog.objects.create(user=self.other, sleep_quality=3)

        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_list_pagination(self):
        """page_size로 페이지 크기를 조절할 수 있다."""
        for _ in range(3):
            SleepLog.objects.create(user=self.user, sleep_quality=3)

        res = self.client.get(self.list_url, {"page": 1, "page_size": 2})
        self.assertEqual(res.data["count"], 3)
        self.assertEqual(len(res.data["results"]), 2)

    def test_list_date_filter_excludes_out_of_range(self):
        """미래 start_date로 필터하면 0건."""
        SleepLog.objects.create(user=self.user, sleep_quality=3)
        res = self.client.get(self.list_url, {"start_date": "2099-01-01"})
        self.assertEqual(res.data["count"], 0)

    def test_requires_authentication(self):
        """비로그인 요청은 거부된다."""
        self.client.force_authenticate(None)
        res = self.client.get(self.list_url)
        self.assertIn(
            res.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    # ------------------------------------------------------------ 수정/삭제

    def test_patch_sleep_quality_does_not_recompute_residual(self):
        """bedtime을 건드리지 않는 수정은 기존 잔류량 스냅샷을 보존한다."""
        bedtime = timezone.now()
        self._log_caffeine_at(self.user, 100, bedtime - timedelta(hours=5))
        created = self.client.post(
            self.list_url, {"actual_bedtime": bedtime.isoformat()}, format="json"
        )
        original_residual = created.data["residual_mg_at_sleep"]

        res = self.client.patch(
            self.detail_url(created.data["id"]), {"sleep_quality": 4}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["residual_mg_at_sleep"], original_residual)

    def test_patch_bedtime_recomputes_residual(self):
        """actual_bedtime을 새로 지정하면 잔류량이 다시 계산된다."""
        log = SleepLog.objects.create(user=self.user)
        bedtime = timezone.now()
        self._log_caffeine_at(self.user, 100, bedtime - timedelta(hours=5))

        res = self.client.patch(
            self.detail_url(log.id), {"actual_bedtime": bedtime.isoformat()}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(res.data["residual_mg_at_sleep"], 50.0, delta=0.5)

    def test_cannot_access_others_log(self):
        """타인의 기록에 접근하면 404."""
        log = SleepLog.objects.create(user=self.other, sleep_quality=3)
        res = self.client.get(self.detail_url(log.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_log(self):
        """본인 기록을 삭제할 수 있다."""
        log = SleepLog.objects.create(user=self.user, sleep_quality=3)
        res = self.client.delete(self.detail_url(log.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SleepLog.objects.filter(id=log.id).exists())

    def test_cannot_delete_others_log(self):
        """타인의 기록은 삭제할 수 없다(404)."""
        log = SleepLog.objects.create(user=self.other, sleep_quality=3)
        res = self.client.delete(self.detail_url(log.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(SleepLog.objects.filter(id=log.id).exists())


class FeedStatusAPITests(APITestCase):
    """/feed-status/(명세상 GET /feed)의 계산 결과 계약.

    target_sleeptime을 항상 "지금부터 5시간 뒤"로 두어, 실행 시각과 무관하게
    자정 넘김 등을 resolve_next_occurrence가 알아서 처리하게 만든다 — 테스트가
    몇 시에 돌아도 bedtime이 always now+5h가 되도록 하는 트릭이다.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw12345!")
        self.url = reverse("diary:feed-status")
        self.client.force_authenticate(self.user)

    def _create_profile(self, body_weight_kg=65.0):
        bedtime = (timezone.now() + timedelta(hours=5)).time()
        return UserProfile.objects.create(
            user=self.user, target_sleeptime=bedtime, body_weight_kg=body_weight_kg
        )

    def test_requires_profile(self):
        """프로필이 없으면 404 PROFILE_NOT_FOUND."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data["code"], "PROFILE_NOT_FOUND")

    def test_requires_authentication(self):
        """비로그인 요청은 거부된다."""
        self.client.force_authenticate(None)
        res = self.client.get(self.url)
        self.assertIn(
            res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    def test_defaults_with_no_history(self):
        """기록이 전혀 없으면 θ_pop(80.0) 기준값과 초기상태(0mg)로 내려온다.

        기준음료(ref_dose_mg) 폴백값(180mg)에서, bedtime 시점 잔류량이 0이므로
        theta_pop(80mg) 전부가 남는다. cutoff는 이미 지난 시각으로 계산되어
        CUTOFF_EXCEEDED 경고가 함께 뜬다 (80/180 비율로는 5시간 뒤 취침 전에
        마감시각이 지나가 버리는 계산 결과다 — calcs/cutoff.py CALC-002 그대로).
        """
        self._create_profile()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["threshold_mg"], 80.0)
        self.assertEqual(res.data["current_mg"], 0.0)
        self.assertEqual(res.data["remaining_mg"], 80.0)
        self.assertEqual(res.data["remaining_cups"], 0)
        self.assertEqual(res.data["today_total_mg"], 0.0)
        self.assertEqual(res.data["today_log_count"], 0)
        self.assertIsNotNone(res.data["cutoff_at"])
        self.assertIn("CUTOFF_EXCEEDED", [w["code"] for w in res.data["warnings"]])
        self.assertFalse(res.data["night_session_active"])
        self.assertFalse(res.data["sleep_survey_required"])  # 가입 당일

    def test_today_caffeine_logs_are_counted(self):
        """오늘 남긴 CaffeineLog가 today_total_mg/today_log_count에 반영된다."""
        self._create_profile()
        CaffeineLog.objects.create(user=self.user, caffeine_mg=100, name="테스트")
        res = self.client.get(self.url)
        self.assertEqual(res.data["today_total_mg"], 100.0)
        self.assertEqual(res.data["today_log_count"], 1)
        self.assertGreater(res.data["current_mg"], 0)

    def test_night_session_active_reflects_allnightsession(self):
        """활성 AllNightSession이 있으면 night_session_active가 true."""
        self._create_profile()
        now = timezone.now()
        AllNightSession.objects.create(
            user=self.user,
            status=AllNightSession.Status.ACTIVE,
            started_at=now,
            target_time=now + timedelta(hours=8),
        )
        res = self.client.get(self.url)
        self.assertTrue(res.data["night_session_active"])

    def test_compact_omits_drinks_and_graph(self):
        """compact=true는 drinks/graph를 생략한다."""
        self._create_profile()
        res = self.client.get(self.url, {"compact": "true"})
        self.assertNotIn("drinks", res.data)
        self.assertNotIn("graph", res.data)

        res = self.client.get(self.url)
        self.assertIn("drinks", res.data)
        self.assertIn("graph", res.data)

    def test_sleep_survey_required_false_when_already_submitted_today(self):
        """가입일과 무관하게, 오늘자 SleepLog가 이미 있으면 설문을 다시 띄우지 않는다."""
        self._create_profile()
        User.objects.filter(id=self.user.id).update(
            date_joined=timezone.now() - timedelta(days=5)
        )
        self.user.refresh_from_db()  # force_authenticate가 쥔 in-memory user도 갱신
        SleepLog.objects.create(user=self.user, sleep_quality=3)
        res = self.client.get(self.url)
        self.assertFalse(res.data["sleep_survey_required"])

    def test_sleep_survey_required_true_when_applicable(self):
        """가입 당일도 아니고, 05:00 이후이며, 오늘자 SleepLog가 없으면 설문이 필요하다."""
        self._create_profile()
        User.objects.filter(id=self.user.id).update(
            date_joined=timezone.now() - timedelta(days=5)
        )
        self.user.refresh_from_db()  # force_authenticate가 쥔 in-memory user도 갱신
        fixed_now = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        with patch("diary.views.timezone.now", return_value=fixed_now):
            res = self.client.get(self.url)
        self.assertTrue(res.data["sleep_survey_required"])
