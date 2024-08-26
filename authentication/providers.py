from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakGetError
from loguru import logger

from authentication.exceptions import AuthenticationError
from authentication.models import SocialLogin

User = get_user_model()


class KeyCloakAuthProvider:
    provider_name = "keycloak"

    def __init__(self, server_url, realm_name, client_id, client_secret_key):
        self.server_url = server_url
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret_key = client_secret_key
        self.keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret_key=client_secret_key,
        )
        self._userinfo = None

    @property
    def userinfo(self):
        if self._userinfo is None:
            raise AuthenticationError(_("User must be logged in."))
        return self._userinfo

    @classmethod
    def build(cls):
        server_url = settings.KEYCLOAK_SERVER_URL
        realm_name = settings.KEYCLOAK_REALM_NAME
        client_id = settings.KEYCLOAK_CLIENT_ID
        client_secret_key = settings.KEYCLOAK_CLIENT_SECRET_KEY
        return cls(server_url, realm_name, client_id, client_secret_key)

    def get_token(self, authorization):
        try:
            _, token = authorization.split("Bearer")
            token = token.strip()
        except ValueError:
            token = None

        return token

    def login(self, token):
        self._userinfo = self.keycloak_openid.userinfo(token)
        return self._userinfo

    def validate(self, authorization):
        message = None
        if authorization is None:
            message = "keycloak-no-token"
            return False, message

        is_valid = False
        token = self.get_token(authorization)

        # First, try to authenticate
        try:
            userinfo = self.login(token)
            logger.info(f"User '{userinfo['preferred_username']}' successfully logged in using {self.provider_name}")
            is_valid = True
        except KeycloakAuthenticationError:
            logger.info(f"Error authenticating user with {self.provider_name}")
        except KeycloakGetError as err:
            logger.error(f"Error while comunicating with {self.provider_name} service {err!r}")
            message = "keycloak-integration-error"

        self.token = token  # append this token to request object
        if not is_valid:
            message = "keycloak-forbidden"
            return False, message

        # Then, check permissions
        authorized = False
        message = "keycloak-profile-unauthorized"
        decoded = self.keycloak_openid.decode_token(
            token,
            key="",
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
            },
        )
        self.decoded_token = decoded
        if not settings.KEYCLOAK_CHECK_USER_PROFILE:
            return True, message

        user_profiles = decoded.get("corporativo", []) or []
        for profile in user_profiles:
            profile_name = str(profile.get("dsc_perfil") or "").lower().strip()
            system = str(profile.get("dsc_sistema") or "").lower().strip()
            if system == "sniper" and profile_name in settings.ALLOWED_PROFILES:
                authorized = True
                message = None
                break
        return authorized, message

    def extract_common_fields(self, data):
        username = str(data.get("preferred_username") or "").strip()
        email = data.get("email")
        if not email:
            email = f"{username}@user.sniper.pdpj.jus.br"
        return dict(
            email=email,
            username=username,
            name=data.get("name"),
            first_name=data.get("given_name"),
            last_name=data.get("family_name"),
            user_id=data.get("user_id"),
            uid=data.get("sub"),
        )

    def populate_user(self, user, data):
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        name = data.get("name")
        user.email = data.get("email")
        name_parts = (name or "").partition(" ")
        setattr(user, "first_name", first_name or name_parts[0])
        setattr(user, "last_name", last_name or name_parts[2])
        return user

    def complete_login(self):
        common_fields = self.extract_common_fields(self.userinfo)
        if not common_fields.get("username"):
            raise AuthenticationError(_("Username information is missing"))
        user, user_created = User.objects.get_or_create(username=common_fields["username"])
        if user_created:
            logger.info(f"Saving '{user.username}' to Users model")
            user = self.populate_user(user, common_fields)
        user.save()

        social_login, created = SocialLogin.objects.get_or_create(
            user=user,
            provider=self.provider_name,
            defaults={"extra_data": self.userinfo, "uid": common_fields["uid"]},
        )
        social_login.save()
        return social_login
