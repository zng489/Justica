from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakGetError
from model_bakery import baker

from authentication.exceptions import AuthenticationError
from authentication.models import SocialLogin
from authentication.providers import KeyCloakAuthProvider

User = get_user_model()


@pytest.mark.django_db
class TestKeyCloakAuthProvider:
    def test_userinfo_property(self):
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = {"data": 1}

        assert provider.userinfo == {"data": 1}

    def test_userinfo_property_user_not_logged_in(self):
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = None

        with pytest.raises(AuthenticationError):
            provider.userinfo

    def test_get_token_from_authorization(self):
        token = "abc123"
        authorization = f"Bearer {token}"

        provider = KeyCloakAuthProvider.build()

        assert provider.get_token(authorization) == token

    def test_invalid_authorization_header(self):
        token = "abc123"
        authorization = f"Anything {token}"

        provider = KeyCloakAuthProvider.build()

        assert provider.get_token(authorization) is None

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_token_valid(self, m_KeycloakOpenID):
        token = "abc123"
        authorization = f"Bearer {token}"

        provider = KeyCloakAuthProvider.build()
        provider.validate(authorization)

        m_KeycloakOpenID.assert_called_once_with(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=settings.KEYCLOAK_REALM_NAME,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET_KEY,
        )
        m_KeycloakOpenID.return_value.userinfo.assert_called_once_with(token)
        # assert response is True

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_token_invalid(self, m_KeycloakOpenID):
        m_KeycloakOpenID.return_value.userinfo.side_effect = KeycloakAuthenticationError
        token = "abc123"
        authorization = f"Bearer {token}"

        provider = KeyCloakAuthProvider.build()
        response, message = provider.validate(authorization)

        m_KeycloakOpenID.return_value.userinfo.assert_called_once_with(token)
        assert response is False
        assert message == "keycloak-forbidden"

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_authorization_is_none(self, m_KeycloakOpenID):
        m_KeycloakOpenID.return_value.userinfo.side_effect = KeycloakAuthenticationError
        authorization = None

        provider = KeyCloakAuthProvider.build()
        response, message = provider.validate(authorization)

        m_KeycloakOpenID.return_value.userinfo.assert_not_called()
        assert response is False
        assert message == "keycloak-no-token"

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_keycloak_integration_error(self, m_KeycloakOpenID):
        m_KeycloakOpenID.return_value.userinfo.side_effect = KeycloakGetError
        token = "abc123"
        authorization = f"Bearer {token}"

        provider = KeyCloakAuthProvider.build()
        response, message = provider.validate(authorization)

        m_KeycloakOpenID.return_value.userinfo.assert_called_once_with(token)
        assert response is False
        assert message == "keycloak-forbidden"

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_complete_login(self, m_KeycloakOpenID):
        sub = "12345"
        response = {
            "preferred_username": "username",
            "given_name": "user",
            "family_name": "name",
            "email": "user@example.com",
            "sub": sub,
        }
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = response

        user_social_login = provider.complete_login()
        social_login = SocialLogin.objects.all()
        users = User.objects.all()

        assert social_login.count() == 1
        assert social_login[0].user == users[0]
        assert social_login[0] == user_social_login
        assert social_login[0].provider == provider.provider_name
        assert social_login[0].uid == sub
        assert social_login[0].extra_data == response
        assert users.count() == 1
        assert users[0].username == "username"
        assert users[0].first_name == "user"
        assert users[0].last_name == "name"
        assert users[0].email == "user@example.com"

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_complete_login_raise_error_when_username_is_empty(self, m_KeycloakOpenID):
        sub = "12345"
        response = {
            "preferred_username": "",
            "given_name": "user",
            "family_name": "name",
            "email": "user@example.com",
            "sub": sub,
        }
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = response

        with pytest.raises(AuthenticationError):
            provider.complete_login()
        social_login = SocialLogin.objects.all()

        assert social_login.count() == 0

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_complete_login_raise_error_when_username_is_empty_space(self, m_KeycloakOpenID):
        sub = "12345"
        response = {
            "preferred_username": " ",
            "given_name": "user",
            "family_name": "name",
            "email": "user@example.com",
            "sub": sub,
        }
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = response

        with pytest.raises(AuthenticationError):
            provider.complete_login()
        social_login = SocialLogin.objects.all()

        assert social_login.count() == 0

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_complete_login_raise_error_when_username_is_integer(self, m_KeycloakOpenID):
        sub = "12345"
        response = {
            "preferred_username": 42,
            "given_name": "user",
            "family_name": "name",
            "email": "user@example.com",
            "sub": sub,
        }
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = response

        provider.complete_login()
        social_login = SocialLogin.objects.all()
        users = User.objects.all()

        assert social_login.count() == 1
        assert users.count() == 1
        assert users[0].username == "42"

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_complete_login_raise_error_when_username_is_none(self, m_KeycloakOpenID):
        sub = "12345"
        response = {
            "preferred_username": None,
            "given_name": "user",
            "family_name": "name",
            "email": "user@example.com",
            "sub": sub,
        }
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = response

        with pytest.raises(AuthenticationError):
            provider.complete_login()
        social_login = SocialLogin.objects.all()

        assert social_login.count() == 0

    @mock.patch("authentication.providers.KeycloakOpenID")
    def test_complete_login_user_already_exists(self, m_KeycloakOpenID):
        username = "username"
        sub = "12345"
        baker.make(User, username=username)
        response = {
            "preferred_username": username,
            "given_name": "user",
            "family_name": "name",
            "email": "user@example.com",
            "sub": sub,
        }
        provider = KeyCloakAuthProvider.build()
        provider._userinfo = response

        user_social_login = provider.complete_login()
        social_login = SocialLogin.objects.all()
        users = User.objects.all()

        assert social_login.count() == 1
        assert social_login[0].user == users[0]
        assert social_login[0] == user_social_login
        assert social_login[0].provider == provider.provider_name
        assert social_login[0].uid == sub
        assert users.count() == 1
        assert users[0].username == username
