from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from model_bakery import baker

from authentication.middleware import KeyCloakAuthMiddleware, TermsAcceptedMiddleware
from authentication.models import SocialLogin

User = get_user_model()


@pytest.mark.django_db
class TestTermsAcceptedMiddleware:
    def setup_method(self):
        self.factory = RequestFactory()
        self.m_get_response = mock.Mock()

    def test_user_has_accepted_the_terms(self):
        self.m_get_response.return_value = HttpResponse()
        request = self.factory.get("api/endpoint")
        user = baker.make(User)
        baker.make(SocialLogin, user=user, extra_data={"accepted_terms_at": "2022-08-05"})
        request.user = user
        middleware = TermsAcceptedMiddleware(self.m_get_response)
        response = middleware(request)

        assert response.status_code == 200

    def test_user_has_not_accepted_the_terms(self):
        self.m_get_response.return_value = HttpResponse()
        request = self.factory.get("api/endpoint")
        user = baker.make(User)
        baker.make(SocialLogin, user=user)
        request.user = user
        middleware = TermsAcceptedMiddleware(self.m_get_response)
        response = middleware(request)

        assert response.status_code == 403

    def test_user_has_no_social_login(self):
        self.m_get_response.return_value = HttpResponse()
        request = self.factory.get("api/endpoint")
        user = baker.make(User)
        request.user = user
        middleware = TermsAcceptedMiddleware(self.m_get_response)
        response = middleware(request)

        assert response.status_code == 403

    def test_free_access_to_v1_config_endpoint(self):
        self.m_get_response.return_value = HttpResponse()
        request = self.factory.get("/v1/config")
        user = baker.make(User)
        baker.make(SocialLogin, user=user, extra_data={})
        request.user = user
        middleware = TermsAcceptedMiddleware(self.m_get_response)
        response = middleware(request)

        assert response.status_code == 200

    def test_free_access_to_v1_terms_endpoint(self):
        self.m_get_response.return_value = HttpResponse()
        request = self.factory.get("/v1/terms")
        user = baker.make(User)
        baker.make(SocialLogin, user=user, extra_data={})
        request.user = user
        middleware = TermsAcceptedMiddleware(self.m_get_response)
        response = middleware(request)

        assert response.status_code == 200

    @override_settings(TERMS_ACCEPTED_FREE_PATHS_REGEX="/api/free/*")
    def test_free_paths(self):
        self.m_get_response.return_value = HttpResponse()

        request = self.factory.get("/api/free/v1")
        middleware = TermsAcceptedMiddleware(self.m_get_response)
        response = middleware(request)

        assert response.status_code == 200


class TestKeyCloakMiddleware:
    def setup_method(self):
        self.factory = RequestFactory()
        self.m_get_response = mock.Mock()
        self.p_KeyCloakAuthProvider = mock.patch("authentication.middleware.KeyCloakAuthProvider")
        self.m_KeyCloakAuthProvider = self.p_KeyCloakAuthProvider.start()

    def teardown_method(self):
        self.p_KeyCloakAuthProvider.stop()

    @mock.patch("authentication.middleware.auth_login")
    def test_receive_valid_token(self, m_auth_login):
        self.m_get_response.return_value = HttpResponse()
        m_provider = mock.Mock(decoded_token="decoded token", token="keycloak token")
        self.m_KeyCloakAuthProvider.build.return_value = m_provider
        m_provider.validate.return_value = (True, None)

        authorization = "Bearer abc123"
        request = self.factory.get("api/endpoint", HTTP_Authorization=authorization)
        middleware = KeyCloakAuthMiddleware(self.m_get_response)
        response = middleware(request)

        m_provider.validate.assert_called_once_with(authorization)
        m_provider.complete_login.assert_called_once_with()
        assert request.decoded_token == "decoded token"
        assert request.keycloak_token == "keycloak token"
        assert response.status_code == 200

    def test_receive_invalid_token(self):
        self.m_get_response.return_value = HttpResponse()
        m_provider = mock.Mock()
        self.m_KeyCloakAuthProvider.build.return_value = m_provider
        m_provider.validate.return_value = (False, "error-message")

        authorization = "Bearer invalid"
        request = self.factory.get("api/endpoint", HTTP_Authorization=authorization)
        middleware = KeyCloakAuthMiddleware(self.m_get_response)
        response = middleware(request)

        m_provider.validate.assert_called_once_with(authorization)
        assert response.status_code == 403

    @override_settings(KEYCLOAK_FREE_PATHS_REGEX="/api/free/*")
    def test_free_paths(self):
        self.m_get_response.return_value = HttpResponse()

        request = self.factory.get("/api/free2/v1")
        middleware = KeyCloakAuthMiddleware(self.m_get_response)
        response = middleware(request)

        self.m_KeyCloakAuthProvider.build.return_value.validate.assert_not_called()
        assert response.status_code == 200
