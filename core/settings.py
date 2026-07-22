import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    
    
    # Local apps
    'apps.health',
    'apps.users',
    'apps.tournaments',
    'apps.players',
    'apps.analytics',
    'apps.community',
    'apps.payments',
    'apps.notifications',
    'apps.chat',
    'apps.ai',
    'apps.teams',
    'apps.sponsors',
    'apps.achievements',
    'apps.schedules',
    'apps.streaming',
    'apps.content',
    'apps.newsletter',
    'apps.feedback',
    'apps.audit',
    'apps.legal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'apexafrika_db'),
        'USER': os.getenv('DB_USER', 'apexafrika_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'apexafrika_pass'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_SECRET_KEY', ''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
]
CORS_ALLOW_CREDENTIALS = True

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@apexafrika.com')

# Frontend URL
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== PAYSTACK CONFIGURATION ====================
PAYSTACK = {
    'SECRET_KEY': os.getenv('PAYSTACK_SECRET_KEY', ''),
    'PUBLIC_KEY': os.getenv('PAYSTACK_PUBLIC_KEY', ''),
    'MERCHANT_EMAIL': os.getenv('PAYSTACK_MERCHANT_EMAIL', ''),
    'ENVIRONMENT': os.getenv('PAYSTACK_ENVIRONMENT', 'test'),  # 'test' or 'live'
    'BASE_URL': 'https://api.paystack.co',
    'INITIALIZE_URL': 'https://api.paystack.co/transaction/initialize',
    'VERIFY_URL': 'https://api.paystack.co/transaction/verify/',
}

# ==================== GROQ AI ====================
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama3-70b-8192')

# ==================== TWO-FACTOR AUTH ====================
TWO_FACTOR_FORCE_VERIFICATION = os.getenv('TWO_FACTOR_FORCE', 'False') == 'True'
TWO_FACTOR_VERIFICATION_REQUIRED = False
TWO_FACTOR_REMEMBER_DEVICE = True
TWO_FACTOR_REMEMBER_DURATION = 30

# ==================== CHANNELS (WebSocket) ====================
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.getenv('REDIS_HOST', '127.0.0.1'), 6379)],
        },
    },
}

# DRF Spectacular (Swagger) Configuration
INSTALLED_APPS += [
    'drf_spectacular',
]

REST_FRAMEWORK.update({
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
})

SPECTACULAR_SETTINGS = {
    'TITLE': 'ApexAfrika API',
    'DESCRIPTION': '''
ApexAfrika - Game Operations Platform for African Esports

A comprehensive API for tournament management, player analytics, community engagement,
payments, and content management for the African gaming ecosystem.

Features:
- Tournament Management
- Player Analytics and Leaderboards
- Community and Social Features
- Paystack Payment Integration
- AI-Powered Predictions (Groq)
- JWT Authentication + Google OAuth
- Analytics and Reporting
- Content and Education
- Team Management
- Achievements and Badges
- Scheduling and Calendar
- Live Streaming
- Newsletters
- Feedback and Surveys
- Audit Logs
- Legal and Compliance

Authentication:
Most endpoints require JWT authentication. Include the token in the Authorization header:
Authorization: Bearer <your_access_token>

Rate Limits:
- Anonymous: 100 requests/day
- Authenticated: 1000 requests/day

Base URL:
https://apexafrika.com/api/v1/

Contact:
- Website: apexafrika.com
- Email: support@apexafrika.com
''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0',
    'SWAGGER_UI_FAVICON_HREF': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/favicon-32x32.png',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'displayRequestDuration': True,
        'filter': True,
        'requestSnippetsEnabled': True,
        'tryItOutEnabled': True,
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'docExpansion': 'none',
        'syntaxHighlight': {
            'activated': True,
            'theme': 'agate',
        },
    },
    'REDOC_SETTINGS': {
        'hideHostname': False,
        'theme': {
            'colors': {
                'primary': {
                    'main': '#FFB300',
                },
                'secondary': {
                    'main': '#FFB300',
                },
            },
            'typography': {
                'fontSize': '14px',
                'lineHeight': '1.5',
            },
        },
    },
    'TAGS': [
        {'name': 'auth', 'description': 'Authentication endpoints (Register, Login, OAuth, 2FA)'},
        {'name': 'profile', 'description': 'User profile management'},
        {'name': 'tournaments', 'description': 'Tournament management (CRUD, registration, brackets)'},
        {'name': 'players', 'description': 'Player analytics, stats, and leaderboards'},
        {'name': 'community', 'description': 'Community posts, comments, and likes'},
        {'name': 'payments', 'description': 'Paystack payment integration'},
        {'name': 'notifications', 'description': 'User notifications and preferences'},
        {'name': 'chat', 'description': 'Real-time chat (WebSocket)'},
        {'name': 'ai', 'description': 'AI-powered predictions and chat (Groq)'},
        {'name': 'teams', 'description': 'Team management and invitations'},
        {'name': 'achievements', 'description': 'Achievements and badges'},
        {'name': 'schedules', 'description': 'Match scheduling and calendar'},
        {'name': 'streaming', 'description': 'Live streaming management'},
        {'name': 'content', 'description': 'Content articles, guides, and learning paths'},
        {'name': 'newsletter', 'description': 'Newsletter subscriptions and campaigns'},
        {'name': 'feedback', 'description': 'User feedback and surveys'},
        {'name': 'analytics', 'description': 'Platform analytics and reporting'},
        {'name': 'audit', 'description': 'Audit logs (admin only)'},
        {'name': 'legal', 'description': 'Terms, Privacy, and Cookie consent'},
        {'name': 'admin', 'description': 'Admin operations'},
        {'name': 'health', 'description': 'Health checks for monitoring'},
    ],
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': True,
    'ENABLE_DJANGO_DEPRECATED_WARNINGS': False,
}
