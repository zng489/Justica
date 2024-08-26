import re

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from urlid_graph.models import ElementConfig

from authentication.models import SocialLogin
from authentication.providers import KeyCloakAuthProvider


class TermsAcceptedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def allow_free_pass(self, request):
        return (
            request.path.startswith(settings.STATIC_URL)
            or request.path.startswith("/django-rq")
            or request.path.startswith("/v1/config")
            or request.path.startswith("/v1/terms")
            or any(re.match(free_path, request.path) for free_path in settings.TERMS_ACCEPTED_FREE_PATHS_REGEX)
        )

    def __call__(self, request):
        if self.allow_free_pass(request):
            return self.get_response(request)

        if isinstance(request.user, AnonymousUser):
            return JsonResponse({"message": "terms-anonymous-user"}, status=403)

        social_login = SocialLogin.objects.filter(user=request.user).first()
        if social_login is None:
            return JsonResponse({"message": "terms-user-not-found"}, status=403)

        if social_login.extra_data.get("accepted_terms_at") is None:
            return JsonResponse({"message": "terms-not-accepted"}, status=403)
        return self.get_response(request)


class KeyCloakAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.provider = KeyCloakAuthProvider.build()

    def allow_free_pass(self, request):
        return (
            request.path.startswith(settings.STATIC_URL)
            or request.path.startswith("/django-rq")
            or any(re.match(free_path, request.path) for free_path in settings.KEYCLOAK_FREE_PATHS_REGEX)
        )

    def __call__(self, request):
        if self.allow_free_pass(request):
            return self.get_response(request)

        is_valid, message = self.provider.validate(request.headers.get("Authorization"))
        if not is_valid:
            detail = None
            if message == "keycloak-profile-unauthorized":
                detail_config = ElementConfig.objects.filter(
                    config_type=ElementConfig.CUSTOM_CONFIG, name="unauthorized-profile"
                ).first()
                if detail_config is not None:
                    detail = detail_config.data
            return JsonResponse({"message": message, "detail": detail}, status=403)

        social_login = self.provider.complete_login()
        auth_login(request, social_login.user)
        request.keycloak_token = self.provider.token
        request.decoded_token = self.provider.decoded_token
        return self.get_response(request)
