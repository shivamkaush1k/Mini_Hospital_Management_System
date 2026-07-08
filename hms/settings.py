from pathlib import Path
from decouple import config, Csv
import os

# ======================================================
# BASE DIRECTORY
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ======================================================
# SECURITY
# ======================================================
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
# Empty ALLOWED_HOSTS was causing the CSRF failure whenever the site was
# accessed via anything other than exactly "localhost"/"127.0.0.1".
# Add any host/IP/tunnel domain you actually use to access the site.
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=Csv()
)


# ======================================================
# APPLICATIONS
# ======================================================
INSTALLED_APPS = [

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third Party Apps
    "rest_framework",
    'crispy_forms',
    'crispy_bootstrap5',
    "cloudinary",
    "cloudinary_storage",

    # Local Apps
    "accounts.apps.AccountsConfig",
    "doctors",
    "patients",
    "appointments",
    "prescriptions",
]


# ======================================================
# MIDDLEWARE
# ======================================================
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


# ======================================================
# URLS
# ======================================================
ROOT_URLCONF = "hms.urls"


# ======================================================
# TEMPLATES
# ======================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
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


# ======================================================
# WSGI
# ======================================================
WSGI_APPLICATION = "hms.wsgi.application"


# ======================================================
# DATABASE
# ======================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ======================================================
# PASSWORD VALIDATORS
# ======================================================
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


# ======================================================
# INTERNATIONALIZATION
# ======================================================
LANGUAGE_CODE = "en-us"

TIME_ZONE = config("TIME_ZONE", default="Asia/Kolkata")

USE_I18N = True

USE_TZ = True


# ======================================================
# STATIC FILES
# ======================================================
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# ======================================================
# MEDIA FILES
# ======================================================
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# ======================================================
# DEFAULT PRIMARY KEY
# ======================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ======================================================
# CUSTOM USER MODEL
# ======================================================


# ======================================================
# LOGIN / LOGOUT
# ======================================================
LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = "accounts:dashboard"

LOGOUT_REDIRECT_URL = "accounts:home"


# ======================================================
# DJANGO REST FRAMEWORK
# ======================================================
REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


# ======================================================
# EMAIL
# ======================================================
EMAIL_BACKEND = config("EMAIL_BACKEND")

EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)

EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

EMAIL_SERVICE_URL = config("EMAIL_SERVICE_URL")
# ======================================================
# CSRF
# ======================================================
# Empty CSRF_TRUSTED_ORIGINS is the other half of the CSRF failure: if you
# access the site over HTTPS through any proxy/tunnel (Codespaces, ngrok,
# Replit, a custom domain, etc.), Django 4+ requires that origin listed here
# or the POST gets rejected regardless of ALLOWED_HOSTS.
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://127.0.0.1:8000,http://localhost:8000",
    cast=Csv()
)

# Only needed if you access the site over plain HTTP locally (default dev
# server). If you switch to HTTPS in production, set these to True there.
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# If you ever put this behind a reverse proxy (nginx, Codespaces, ngrok,
# Render, etc.) that terminates HTTPS for you, uncomment these so Django
# correctly detects the original request was secure:
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# USE_X_FORWARDED_HOST = True


# ======================================================
# SESSION
# ======================================================
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1 day


# ======================================================
# FILE UPLOADS
# ======================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")

GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")

GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI")

GOOGLE_SCOPES = config("GOOGLE_SCOPES").split(",")

LOG_LEVEL = config("LOG_LEVEL", default="INFO")

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
}