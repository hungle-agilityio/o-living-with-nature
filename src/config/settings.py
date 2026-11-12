"""Django settings for Ở — Living with Nature.

Values that differ per environment come from environment variables; nothing secret is committed.
"""

import os
from pathlib import Path

# The repository root (db.sqlite3, staticfiles/); the code is in src/.
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes"}


DEBUG = env_bool("DJANGO_DEBUG", True)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is off")
    SECRET_KEY = "dev-only-not-secret"  # local development only

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# The public base URL of the site, in one place (canonical links, sitemap, hreflang).
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "http://localhost:8000").rstrip("/")

# The one switch that lets search engines in: on only when the value is exactly "1". It stays
# off until real photos replace the stand-ins.
INDEXING_ENABLED = os.environ.get("INDEXING_ENABLED", "") == "1"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # whitenoise serves the collected files in production; runserver serves them in development.
    *([] if DEBUG else ["whitenoise.middleware.WhiteNoiseMiddleware"]),
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "pages.context_processors.daypart",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # DJANGO_DB_NAME lets a check run on a throw-away database.
        "NAME": os.environ.get("DJANGO_DB_NAME") or BASE_DIR / "db.sqlite3",
    }
}

# Phase 1 is English only, at the site root; Vietnamese comes later under /vi/.
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English")]
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [SRC_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # The hashed manifest exists only after collectstatic, so development and tests skip it.
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # On by default; only a local run on plain http (the browser check) switches it off.
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]  # the host's health check calls plain HTTP
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
