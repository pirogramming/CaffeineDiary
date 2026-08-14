"""diary 앱 테스트.

섭취기록(CaffeineLog) API의 계약을 고정한다. 특히 신뢰 경계 관련 동작
(스냅샷 박제, 소유권 격리)은 회귀하면 데이터 위조로 이어지므로 반드시 지킨다.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CaffeineLog, Drink

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
