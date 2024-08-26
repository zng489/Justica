from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from freezegun import freeze_time
from model_bakery import baker

from authentication.models import SocialLogin

User = get_user_model()


class TestMainView(TestCase):
    def test_correct_response(self):
        url = reverse("core:ping")  # ping doesn't require authentication
        response = self.client.get(url)
        assert response.status_code == 200


class TestAcceptTermsView(TestCase):
    @override_settings(
        MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != "authentication.middleware.KeyCloakAuthMiddleware"]
    )
    @freeze_time("2022-08-05 12:00:00")
    def test_accept_terms(self):
        user = baker.make(User)
        self.client.force_login(user)
        social_login = baker.make(SocialLogin, user=user, extra_data={})
        url = reverse("accept-terms")

        response = self.client.post(url)
        social_login.refresh_from_db()

        assert response.status_code == 200
        assert social_login.extra_data["accepted_terms_at"] == "2022-08-05 12:00:00+00:00"

    @override_settings(
        MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != "authentication.middleware.KeyCloakAuthMiddleware"]
    )
    def test_accept_terms_get_method_not_allowed(self):
        user = baker.make(User)
        self.client.force_login(user)
        baker.make(SocialLogin, user=user, extra_data={})
        url = reverse("accept-terms")

        response = self.client.get(url)

        assert response.status_code == 405

    @override_settings(
        MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != "authentication.middleware.KeyCloakAuthMiddleware"]
    )
    def test_a_user_cannot_accept_another_user_terms(self):
        user = baker.make(User)
        social_login = baker.make(SocialLogin, user=user, extra_data={})

        another_user = baker.make(User)
        self.client.force_login(another_user)
        url = reverse("accept-terms")

        response = self.client.post(url)
        social_login.refresh_from_db()

        assert response.status_code == 404
        assert social_login.extra_data.get("accepted_terms_at") is None

    @override_settings(
        MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != "authentication.middleware.KeyCloakAuthMiddleware"]
    )
    @freeze_time("2022-08-05 12:00:00")
    def test_user_cannot_accept_terms_twice(self):
        user = baker.make(User)
        self.client.force_login(user)
        terms_accepted_date = "2022-01-01 12:00:00"
        social_login = baker.make(SocialLogin, user=user, extra_data={"accepted_terms_at": terms_accepted_date})
        url = reverse("accept-terms")

        response = self.client.post(url)
        social_login.refresh_from_db()

        assert response.status_code == 400
        assert social_login.extra_data["accepted_terms_at"] == terms_accepted_date

    @override_settings(
        MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != "authentication.middleware.KeyCloakAuthMiddleware"]
    )
    @freeze_time("2022-08-05 12:00:00")
    def test_user_has_no_social_login(self):
        # just in case: defensive programming
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse("accept-terms")

        response = self.client.post(url)

        assert response.status_code == 404


class TestZabbixView(TestCase):
    url_name = "core:zabbix"

    @mock.patch("core.views.run_checks")
    def test_get_correct_response(self, m_run_checks):
        m_run_checks.return_value = {"db": {"status": "ok"}}
        url = reverse(self.url_name)
        resp = self.client.get(url)
        expected = {"db": {"status": "ok"}}

        assert resp.status_code == 200
        assert resp.json() == expected
