"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from decouple import Csv, config
from dj_database_url import parse as db_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=False)
TESTING_ENV = config("TESTING_ENV", cast=bool, default=False)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis.geoip2"
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "health_check",
    "health_check.db",
    "urlid_graph",
    "django_rq",
    "opensearchpy",
    "opensearch_dsl"
]

INTERNAL_APPS = [
    "core",
    "users",
    "authentication",
    "dataset",
    "health",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + INTERNAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.CheckURLExistsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if DEBUG:
    MIDDLEWARE.append("utils.sqlprint.SqlPrintingMiddleware")  # TODO: may use https://pypi.org/project/sqlformatter/

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["config/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# The following 3 uppercase variables are needed by `urlid_graph`:
DATABASE_URL = config("DATABASE_URL")
DATABASE_CPF_URL = config("DATABASE_CPF_URL", default="")
DATABASE_CNPJ_URL = config("DATABASE_CNPJ_URL", default="")
GRAPH_DATABASE_URL = config("GRAPH_DATABASE_URL")
graph_config = config("GRAPH_DATABASE_URL", cast=db_url)
GRAPH_DATABASE = graph_config["NAME"]
DATABASES = {
    "default": config("DATABASE_URL", cast=db_url),
    GRAPH_DATABASE: graph_config,
}
DATABASE_ROUTERS = ["urlid_graph.db_router.RelationAndGraphDBRouter"]

AUTH_USER_MODEL = "users.User"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "pt-BR"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Mail config
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.cnj.jus.br")
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=25)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="naoresponda@cnj.jus.br")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = config("ADMINS", cast=Csv(), default="")
if ADMINS:
    ADMINS = [tuple([item.strip() for item in name_email.split("|")]) for name_email in ADMINS]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 24 * 3600,
        "MAX_ENTRIES": 1024,
    }
}

# Keycloak
KEYCLOAK_SERVER_URL = config("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM_NAME = config("KEYCLOAK_REALM_NAME")
KEYCLOAK_CLIENT_ID = config("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET_KEY = config("KEYCLOAK_CLIENT_SECRET_KEY")
KEYCLOAK_ENABLE_MIDDLEWARE = config("KEYCLOAK_ENABLE_MIDDLEWARE", cast=bool, default=not DEBUG)
KEYCLOAK_CHECK_USER_PROFILE = config("KEYCLOAK_CHECK_USER_PROFILE", cast=bool, default=True)
KEYCLOAK_FREE_PATHS_REGEX = [
    "^/admin/*",
    "^/healthz",
    "^/zabbix",
    "^/ping",
    "^/version",
    "^/$",
]

if KEYCLOAK_ENABLE_MIDDLEWARE:
    django_common_middleware = "django.middleware.common.CommonMiddleware"
    keycloak_middleware_position = MIDDLEWARE.index(django_common_middleware)
    MIDDLEWARE.insert(keycloak_middleware_position, "authentication.middleware.KeyCloakAuthMiddleware")

TERMS_ACCEPTED_ENABLE_MIDDLEWARE = config("TERMS_ACCEPTED_ENABLE_MIDDLEWARE", cast=bool, default=True)
TERMS_ACCEPTED_FREE_PATHS_REGEX = KEYCLOAK_FREE_PATHS_REGEX
if TERMS_ACCEPTED_ENABLE_MIDDLEWARE:
    django_auth_middleware = "django.contrib.auth.middleware.AuthenticationMiddleware"
    terms_middleware_position = MIDDLEWARE.index(django_auth_middleware) + 1
    MIDDLEWARE.insert(terms_middleware_position, "authentication.middleware.TermsAcceptedMiddleware")


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("config.permissions.CsrfExemptSessionAuthentication",),
}


REDIS_URL = config("REDIS_URL", default="redis://localhost:6379")
# django-rq config
RQ_QUEUES = {
    "default": {
        "URL": REDIS_URL,
        "DEFAULT_TIMEOUT": 500,
    }
}

CABECALHO_PROCESSUAL_API_URL = config("CABECALHO_PROCESSUAL_API_URL", default="")
CABECALHO_PROCESSUAL_TOKEN_URL = config("CABECALHO_PROCESSUAL_TOKEN_URL", default="")
CABECALHO_PROCESSUAL_CLIENT_ID = config("CABECALHO_PROCESSUAL_CLIENT_ID", default="")
CABECALHO_PROCESSUAL_CLIENT_SECRET = config("CABECALHO_PROCESSUAL_CLIENT_SECRET", default="")

SISBAJUD_API_URL = config("SISBAJUD_API_URL", default=None)
SISBAJUD_CONTAS_API_URL = config("SISBAJUD_CONTAS_API_URL", default=None)  # old value
SISBAJUD_ORDENS_API_URL = config("SISBAJUD_ORDENS_API_URL", default=None)  # old value
if not SISBAJUD_API_URL and (SISBAJUD_CONTAS_API_URL or SISBAJUD_ORDENS_API_URL):
    SISBAJUD_API_URL = (SISBAJUD_CONTAS_API_URL or SISBAJUD_ORDENS_API_URL).replace("ordem/", "").replace("relacionamento/", "")
SISBAJUD_API_USERNAME = config("SISBAJUD_USERNAME", default="username")
SISBAJUD_API_PASSWORD = config("SISBAJUD_PASSWORD", default="password")
SISBAJUD_API_CLIENT_ID = config("SISBAJUD_CLIENT_ID", default="12345")
SISBAJUD_API_CLIENT_SECRET = config("SISBAJUD_CLIENT_SECRET", default="secret")
MARKETPLACE_URL = config("MARKETPLACE_URL", default=None)
OPENID_AUTH_URL = config("OPENID_AUTH_URL", default=None)
INFOJUD_API_URL = config("INFOJUD_API_URL", default=None)

ALLOWED_PROFILES = config("ALLOWED_PROFILES", cast=Csv(), default="magistrado,servidor")
MAGISTRADO_PROFILES = config("MAGISTRADO_PROFILES", cast=Csv(), default="magistrado")

# Health check configs for zabbix
# `CABECALHO_PROCESSUAL_HEALTH_DOCUMENT` é o documento utilizado para fazer uma busca de processos. Nesse caso, usamos
# o CNPJ do CNJ.
CABECALHO_PROCESSUAL_HEALTH_USER = config("CABECALHO_PROCESSUAL_HEALTH_USER", default="1234567890")
CABECALHO_PROCESSUAL_HEALTH_DOCUMENT = config("CABECALHO_PROCESSUAL_HEALTH_DOCUMENT", default="07421906000129")
SISBAJUD_ORDENS_HEALTH_CPF = config("SISBAJUD_ORDENS_HEALTH_CPF", default="1234567890")
SISBAJUD_ORDENS_HEALTH_TRIBUNAL = config("SISBAJUD_ORDENS_HEALTH_TRIBUNAL", default="1")
SISBAJUD_CONTAS_HEALTH_CPF_SOLICITANTE = config("SISBAJUD_CONTAS_HEALTH_CPF_SOLICITANTE", default="1234567890")
SISBAJUD_CONTAS_HEALTH_DOCUMENT_ENTIDADE = config("SISBAJUD_CONTAS_HEALTH_DOCUMENT_ENTIDADE", default="1234567890")
SISBAJUD_CONTAS_HEALTH_TOKEN = config("SISBAJUD_CONTAS_HEALTH_TOKEN", default="token")

# Enable/Disable features
CABECALHO_PROCESSUAL_ENABLE = config("CABECALHO_PROCESSUAL_ENABLE", cast=bool, default=True)
SISBAJUD_CONTAS_ENABLE = config("SISBAJUD_CONTAS_ENABLE", cast=bool, default=True)
SISBAJUD_ORDENS_ENABLE = config("SISBAJUD_ORDENS_ENABLE", cast=bool, default=True)
INFOJUD_ENABLE = config("INFOJUD_ENABLE", cast=bool, default=True)

# Logging no OpenSearch
OPENSEARCH_URL = config("OPENSEARCH_URL", default="opensearch.pdpj.jus.br")
OPENSEARCH_PORT = config("OPENSEARCH_PORT", default="443")
OPENSEARCH_USER = config("OPENSEARCH_USER", default="sniper")
OPENSEARCH_PASSWORD = config("OPENSEARCH_PASSWORD", default="")

AUDITORIA_ENABLE = config("AUDITORIA_ENABLE", cast=bool, default=False)

GEOIP_PATH = config("GEOIP_PATH", default="static/db")
GEOIP_COUNTRY_PATH = config("GEOIP_COUNTRY_PATH", default="GeoLite2-Country.mmdb")
GEOIP_CITY_PATH = config("GEOIP_CITY_PATH", default="GeoLite2-City.mmdb")
