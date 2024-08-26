from django.urls import path

from dataset.views import declaracao_renda_detalhe, declaracao_renda_lista, processos, sisbajud_contas, sisbajud_ordens, auditoria_logs

app_name = "dataset"
urlpatterns = [
    path("declaracao-renda-lista/", declaracao_renda_lista, name="declaracao-renda-lista"),
    path("declaracao-renda/<str:documento>/<int:ano>/", declaracao_renda_detalhe, name="declaracao-renda-detalhe"),
    path("processos/<uuid:object_uuid>", processos),
    path("sisbajud-contas/<uuid:object_uuid>", sisbajud_contas, name="sisbajud-contas"),
    path("sisbajud-ordens", sisbajud_ordens, name="sisbajud-ordens"),
    path("auditoria-logs", auditoria_logs, name="auditoria-logs"),
]
