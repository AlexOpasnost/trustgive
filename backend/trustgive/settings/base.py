"""Base settings for TrustGive — values shared by development and production."""
from __future__ import annotations

import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    SENTRY_TRACES_SAMPLE_RATE=(float, 0.0),
    APP_VERSION=(str, "1.0.0-dev"),
    POSTHOG_HOST=(str, "https://eu.i.posthog.com"),
)

env_path = BASE_DIR / ".env"
if env_path.exists():
    environ.Env.read_env(str(env_path))
elif (PROJECT_ROOT / ".env").exists():
    environ.Env.read_env(str(PROJECT_ROOT / ".env"))

# --- Core ---
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("DJANGO_CSRF_TRUSTED_ORIGINS")
APP_VERSION = env("APP_VERSION")

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "cachalot",
    "apps.core",
    "apps.charities",
    "apps.ingestion",
    "apps.events",
    "apps.i18n",
    "apps.seo",
]

MIDDLEWARE = [
    "apps.core.middleware.RequestIDMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.CacheControlMiddleware",
]

# --- CORS (REVIEW H-003 fix) ---
CORS_ALLOWED_ORIGINS = env(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)
CORS_ALLOW_CREDENTIALS = False  # No auth → no cookies needed cross-origin
CORS_PREFLIGHT_MAX_AGE = 60 * 60 * 24
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "accept-language",
    "content-type",
    "x-request-id",
]

ROOT_URLCONF = "trustgive.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "trustgive.wsgi.application"
ASGI_APPLICATION = "trustgive.asgi.application"

# --- Database ---
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/trustgive"),
}
DATABASES["default"]["CONN_MAX_AGE"] = 300

# --- Auth (defence-in-depth — no auth in MVP per ADR-002, but good defaults if added later) ---
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18n ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "donation_redirect": "10/min",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "TrustGive API",
    "DESCRIPTION": "Public, anonymous, read-mostly API for the TrustGive charity discovery platform.",
    "VERSION": APP_VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/",
    "TAGS": [
        {"name": "catalog", "description": "Charity browse + filter + detail"},
        {"name": "taxonomy", "description": "Cause taxonomy"},
        {"name": "seo", "description": "SEO landing-page payloads"},
        {"name": "feed", "description": "RSS feed"},
        {"name": "events", "description": "Outbound-click logging"},
        {"name": "ops", "description": "Health + schema"},
    ],
    "SERVERS": [
        {"url": "https://api.trustgive.org", "description": "Production"},
        {"url": "http://localhost:8000", "description": "Local development"},
    ],
}

# --- Cache (per ADR-007) ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "trustgive-default",
        "TIMEOUT": 3600,
        "OPTIONS": {"MAX_ENTRIES": 5000},
    }
}
CACHALOT_ENABLED = True
CACHALOT_TIMEOUT = 60 * 60
CACHALOT_DATABASES = ["default"]
# Per KB-BACKEND-TRUSTGIVE-008: use db_table names, NOT model labels
CACHALOT_UNCACHABLE_TABLES = (
    "ingestion_ingestionlog",
    "events_donationredirectevent",
    "auth_user",
    "django_session",
)

# Per KB-BACKEND-TRUSTGIVE-009: keyed on URL name
CACHE_CONTROL_MAP = {
    "health": "no-store",
    "charity-list": "public, s-maxage=3600, stale-while-revalidate=86400",
    "charity-detail": "public, s-maxage=3600, stale-while-revalidate=86400",
    "charity-source-documents": "public, s-maxage=86400, stale-while-revalidate=86400",
    "charity-compare": "public, s-maxage=3600",
    "cause-list": "public, s-maxage=86400",
    "rss-feed": "public, s-maxage=3600",
    "seo-charity": "public, s-maxage=3600, stale-while-revalidate=86400",
    "donation-redirect": "no-store",
    "schema": "public, s-maxage=3600",
    "swagger-ui": "public, s-maxage=3600",
}

# --- Logging (structured JSON per ADR-008) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(request_id)s %(charity_slug)s %(path)s %(method)s %(status_code)s %(duration_ms)s",
        },
    },
    "filters": {
        "request_id": {"()": "apps.core.middleware.RequestIDLogFilter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.db.backends": {"level": "WARNING"},
        "django.request": {"level": "WARNING", "handlers": ["console"], "propagate": False},
    },
}

# --- External integrations ---
PROPUBLICA_API_BASE = env("PROPUBLICA_API_BASE", default="https://projects.propublica.org/nonprofits/api/v2")
EVERY_ORG_API_BASE = env("EVERY_ORG_API_BASE", default="https://partners.every.org/v0.2")
EVERY_ORG_PUBLIC_KEY = env("EVERY_ORG_PUBLIC_KEY", default="")
EVERY_ORG_PRIVATE_KEY = env("EVERY_ORG_PRIVATE_KEY", default="")
CHARITYBASE_API_BASE = env("CHARITYBASE_API_BASE", default="https://charitybase.uk/api")

POSTHOG_SERVER_KEY = env("POSTHOG_SERVER_KEY", default="")
POSTHOG_HOST = env("POSTHOG_HOST")

CF_API_TOKEN = env("CF_API_TOKEN", default="")
CF_ZONE_ID = env("CF_ZONE_ID", default="")

SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="development")
SENTRY_TRACES_SAMPLE_RATE = env("SENTRY_TRACES_SAMPLE_RATE")
RAILWAY_DEPLOYMENT_ID = env("RAILWAY_DEPLOYMENT_ID", default="local")
