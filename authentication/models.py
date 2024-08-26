from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from dataset.formatting import clean_cpf


class SocialLogin(models.Model):
    class ProviderChoices(models.TextChoices):
        KEYCLOAK = "keycloak", "keycloak"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(verbose_name=_("provider"), max_length=30, choices=ProviderChoices.choices)
    uid = models.CharField(verbose_name=_("uid"), max_length=191)
    last_login = models.DateTimeField(verbose_name=_("last login"), auto_now=True)
    date_joined = models.DateTimeField(verbose_name=_("date joined"), auto_now_add=True)
    extra_data = models.JSONField(verbose_name=_("extra data"), default=dict)

    @property
    def cpf(self):
        return clean_cpf(self.extra_data.get("preferred_username", self.user.username))

    def __str__(self):
        return f"{self.user} - {self.provider}"
