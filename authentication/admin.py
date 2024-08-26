from django.contrib import admin

from authentication.models import SocialLogin


class SocialLoginAdmin(admin.ModelAdmin):
    readonly_fields = ("date_joined", "last_login")


admin.site.register(SocialLogin, SocialLoginAdmin)
