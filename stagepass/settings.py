# stagepass/settings.py
from pathlib import Path
import os
import dj_database_url  # pip install dj-database-url

BASE_DIR = Path(__file__).resolve().parent.parent

USE_CLOUDINARY = bool(os.environ.get("CLOUDINARY_URL"))

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------
DEBUG = True  

if os.path.exists(Path(__file__).resolve().parent.parent / "env.py"):
    import env

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-rm(gh1k1ib25k-d@^lylz#cqeh5)^wsh6fgynl%!)*s$%m9@8+" 
)

ALLOWED_HOSTS = [
    ".herokuapp.com",
    "127.0.0.1",
    "localhost"
]
if os.environ.get("ALLOWED_HOSTS"):
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

CSRF_TRUSTED_ORIGINS = []
if os.environ.get("CSRF_TRUSTED_ORIGINS"):
    CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")

# -----------------------------------------------------------------------------
# Apps
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.sitemaps',
    "django.contrib.humanize",

    "crispy_forms",
    "crispy_bootstrap5",
    'cloudinary',
    'cloudinary_storage',

    # Local apps
    "core",
    "accounts",
    "events",
    "orders",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "stagepass.urls"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "orders.context_processors.cart_info",
            ],
        },
    },
]
BASE_DIR = Path(__file__).resolve().parent.parent
WSGI_APPLICATION = "stagepass.wsgi.application"

# -----------------------------------------------------------------------------
# Database (SQLite local, Postgres on Heroku)
# -----------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# MEDIA settings
MEDIA_URL = "/media/"
if not USE_CLOUDINARY:
    MEDIA_ROOT = BASE_DIR / "media"

if os.environ.get("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.config(
        default=os.environ["DATABASE_URL"],
        conn_max_age=600,
        ssl_require=True,
    )

# -----------------------------------------------------------------------------
# Passwords
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# I18N / TZ
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static files
# -----------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"
        if USE_CLOUDINARY
        else "django.core.files.storage.FileSystemStorage",
    },
}

# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "stagepass@example.com")

# -----------------------------------------------------------------------------
# Default PK
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

