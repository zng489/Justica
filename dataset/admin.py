from django.contrib import admin

from dataset.models import Aeronave, BemDeclarado, Candidacy, Company, Embarcacao, Person, Sancao


class PersonAdmin(admin.ModelAdmin):
    pass


class CompanyAdmin(admin.ModelAdmin):
    pass


class CandidacyAdmin(admin.ModelAdmin):
    pass


class BemDeclaradoAdmin(admin.ModelAdmin):
    pass


class AeronaveAdmin(admin.ModelAdmin):
    pass


class EmbarcacaoAdmin(admin.ModelAdmin):
    pass


class SancaoAdmin(admin.ModelAdmin):
    pass


admin.site.register(Person, PersonAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Candidacy, CandidacyAdmin)
admin.site.register(BemDeclarado, BemDeclaradoAdmin)
admin.site.register(Aeronave, AeronaveAdmin)
admin.site.register(Embarcacao, EmbarcacaoAdmin)
admin.site.register(Sancao, SancaoAdmin)
