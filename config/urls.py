"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from core.views import (
    ExtraAllNodesRelationshipsEndpoint,
    ExtraGraphNodeDetailEndpoint,
    ExtraNodeRelationshipsEndpoint,
    SearchOnGraphEndpoint,
    accept_terms,
    config,
    version,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("healthz/", include("health_check.urls")),
    path("v1/terms", csrf_exempt(accept_terms), name="accept-terms"),
    path("v1/config", config),
    path("v1/node/<uuid:uuid>", ExtraGraphNodeDetailEndpoint.as_view()),
    path("v1/node/<uuid:uuid>/relationships", ExtraNodeRelationshipsEndpoint.as_view()),
    path("v1/relationships", ExtraAllNodesRelationshipsEndpoint.as_view()),
    path("v1/search", SearchOnGraphEndpoint.as_view(), name="search"),
    path("v1/", include("urlid_graph.urls")),
    path("v1/", include("dataset.urls", namespace="dataset")),
    path("django-rq/", include("django_rq.urls")),
    path("version", version),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
