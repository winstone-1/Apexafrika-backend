import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "django-insecure-dev-key-change-in-production"
)
DEBUG = os.getenv("DEBUG", "True") == "True"

# ============================================
# ALLOWED_HOSTS - Fix for Render
# ============================================
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "apexafrika-backend.onrender.com",
    "apexafrika.onrender.com",
    "*.onrender.com",
] + os.getenv("ALLOWED_HOSTS", "").split(",")

# Remove empty strings
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "apps.health",
    "apps.users",
    "apps.tournaments",
    "apps.players",
    "apps.analytics",
    "apps.community",
    "apps.payments",
    "apps.notifications",
    "apps.chat",
    "apps.ai",
    "apps.teams",
    "apps.sponsors",
    "apps.achievements",
    "apps.schedules",
    "apps.streaming",
    "apps.content",
    "apps.newsletter",
    "apps.feedback",
    "apps.audit",
    "apps.legal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# ============================================
# Database Configuration with DATABASE_URL
# ============================================
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }  # noqa: E501
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "apexafrika_db"),
            "USER": os.getenv("DB_USER", "apexafrika_user"),
            "PASSWORD": os.getenv("DB_PASSWORD", "apexafrika_pass"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }  # noqa: E501

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_MIN_LENGTH = 3

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_SECRET_KEY", ""),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
    }  # noqa: E501
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://apexafrika.onrender.com",
    "https://apexafrika-backend.onrender.com",
    "https://*.onrender.com",
]
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@apexafrika.com")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================
# DRF Spectacular (Swagger) Configuration
# ============================================
SPECTACULAR_SETTINGS = {
    "TITLE": "ApexAfrika API",
    "DESCRIPTION": "ApexAfrika - Game Operations Platform for African Esports",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
    },
}

# ============================================
# Paystack Configuration
# ============================================
PAYSTACK = {
    "SECRET_KEY": os.getenv("PAYSTACK_SECRET_KEY", ""),
    "PUBLIC_KEY": os.getenv("PAYSTACK_PUBLIC_KEY", ""),
    "MERCHANT_EMAIL": os.getenv("PAYSTACK_MERCHANT_EMAIL", ""),
    "ENVIRONMENT": os.getenv("PAYSTACK_ENVIRONMENT", "test"),
    "BASE_URL": "https://api.paystack.co",
    "INITIALIZE_URL": "https://api.paystack.co/transaction/initialize",
    "VERIFY_URL": "https://api.paystack.co/transaction/verify/",
}

# ============================================
# GROQ AI Configuration
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# ============================================
# Channels (WebSocket)
# ============================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv("REDIS_HOST", "127.0.0.1"), 6379)],
        },
    },
}

# ============================================
# Django-Q (Lightweight Task Queue)
# ============================================

INSTALLED_APPS += [
    'django_q',
]

Q_CLUSTER = {
    'name': 'apexafrika',
    'workers': 2,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'Django Q',
    'redis': {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': 0,
        'password': os.getenv('REDIS_PASSWORD', ''),
    }
}

# Remove Celery from INSTALLED_APPS (if present)
# Remove 'celery', from INSTALLED_APPS
