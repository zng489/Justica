from django.urls import path

from core.views import MainView, PingView, zabbix_view

app_name = "core"
urlpatterns = [
    path("", MainView.as_view(), name="main"),
    path("ping", PingView.as_view(), name="ping"),
    path("zabbix", zabbix_view, name="zabbix"),
]
