import json
import os
from datetime import timedelta
from pathlib import Path

from constance import config
import environ
from celery.schedules import crontab

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from test_install_chat.utils import lazy_constance_value

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("HOST", default=["*"])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if DEBUG:
    ALLOWED_HOSTS.append("*")

SITE_ID = 1

FRONTEND_URL = env.str("FRONTEND_URL", "http://localhost:3000")

# Application definition

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]


THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.apple",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.twitter_oauth2",
    # NOTE: we can still use linkedin oauth2 here
    "allauth.socialaccount.providers.linkedin_oauth2",
    "constance",
    "constance.backends.database",
    "django_celery_beat",
    "django_celery_results",
    "corsheaders",
    "django_extensions",
    "drf_yasg",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "oauth2_provider",
    "phonenumber_field",
    "phonenumbers",
]

LOCAL_APPS = [
    "core",
    "users",
]

INSTALLED_APPS += THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware","corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",]

ROOT_URLCONF = "test_install_chat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
        },
    },
]

WSGI_APPLICATION = "test_install_chat.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if env.str("DATABASE_URL", default=None):
    DATABASES = {"default": env.db()}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "users.validators.CommonPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = env.str("TIME_ZONE", "UTC")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "oauth2_provider.backends.OAuth2Backend",
)


# Logging
# https://docs.djangoproject.com/en/4.1/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": env.path(
                "ERROR_LOG_PATH", default=os.path.join(BASE_DIR, "error.log")
            ),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["mail_admins", "file"],
            "level": "ERROR",
        },
    },
}


# Email

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST", "smtp.gmail.com")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", False)
EMAIL_PORT = int(env.str("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", None)

# if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
#     EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Allauth

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_TEMPLATE_EXTENSION = "html"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_URL = reverse_lazy("admin:login")
LOGIN_REDIRECT_URL = "/"
OLD_PASSWORD_FIELD_ENABLED = True
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3


# REST Framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}


# REST Auth

# Use REST_AUTH starting in 2023
# https://dj-rest-auth.readthedocs.io/en/stable/configuration.html
REST_AUTH = {
    # Replace password reset serializer to fix 500 error
    "PASSWORD_RESET_SERIALIZER": "users.api.v1.serializers.PasswordResetSerializer",
    "USER_DETAILS_SERIALIZER": "users.api.v1.serializers.UserDetailSerializer",
    "REGISTER_SERIALIZER": "users.api.v1.serializers.CustomRegisterSerializer",
    "PASSWORD_CHANGE_SERIALIZER": "users.api.v1.serializers.CustomPasswordChangeSerializer",
    "OLD_PASSWORD_FIELD_ENABLED": True,
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "jwt-auth",
    "JWT_AUTH_REFRESH_COOKIE": "jwt-refresh-token",
    "JWT_AUTH_SECURE": True,
    "JWT_AUTH_HTTPONLY": True,
    "JWT_AUTH_SAMESITE": "Lax",
}

# JWT

REST_USE_JWT = True
JWT_AUTH_COOKIE = "jwt-auth"
JWT_AUTH_REFRESH_COOKIE = "jwt-refresh-token"
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}


# Swagger

SWAGGER_SETTINGS = {
    "DEFAULT_INFO": f"{ROOT_URLCONF}.api_info",
    "SECURITY_DEFINITIONS": {
        "ApiKey": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        },
    },
}

# Constance

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

# CORS

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://127.0.0.1:3000", "http://localhost:3000"],
)

CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", True)


# Celery

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_CACHE_BACKEND = "django-cache"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULE = {}

# OAUTH2

OAUTH2_PROVIDER = {
    "SCOPES": {
        "read": "Read scope",
        "write": "Write scope",
        "groups": "Access to your groups",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,  # 1 hour
    "REFRESH_TOKEN_EXPIRE_SECONDS": 86400,  # 1 day
}
# SOCIAL AUTH
# This fixes the issue with social sign-in for existing local user
# https://github.com/pennersr/django-allauth/issues/215
SOCIALACCOUNT_ADAPTER = "allauth.socialaccount.adapter.DefaultSocialAccountAdapter"
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = False
SOCIALACCOUNT_EMAIL_VERIFICATION = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": lazy_constance_value("GOOGLE_CLIENT_ID")(),
            "secret": lazy_constance_value("GOOGLE_CLIENT_SECRET")(),
            "key": lazy_constance_value("GOOGLE_KEY")(),
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
        "FETCH_USERINFO": True,
    },
    "facebook": {
        "METHOD": "oauth2",
        "APP": {
            "client_id": lazy_constance_value("FACEBOOK_CLIENT_ID")(),
            "secret": lazy_constance_value("FACEBOOK_CLIENT_SECRET")(),
        },
        # OPTIONAL if you want to override the default Facebook JavaScript SDK URL
        # "SDK_URL": "//connect.facebook.net/{locale}/sdk.js",
        "SCOPE": ["email", "public_profile"],
        "AUTH_PARAMS": {"auth_type": "reauthenticate"},
        "INIT_PARAMS": {"cookie": True},
        "FIELDS": [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "name",
            "name_format",
            "picture",
            "short_name",
        ],
        "EXCHANGE_TOKEN": True,
        "LOCALE_FUNC": "path.to.callable",
        "VERIFIED_EMAIL": False,
        "VERSION": "v13.0",
        "GRAPH_API_URL": "https://graph.facebook.com/v21.0",
    },
    "apple": {
        "APPS": [
            {
                # Your service identifier.
                "client_id": lazy_constance_value("APPLE_CLIENT_ID")(),
                # The Key ID (visible in the "View Key Details" page).
                "secret": lazy_constance_value("APPLE_SECRET")(),
                # Member ID/App ID Prefix -- you can find it below your name
                # at the top right corner of the page, or it’s your App ID
                # Prefix in your App ID.
                "key": lazy_constance_value("APPLE_KEY")(),
                "settings": lazy_constance_value("APPLE_SETTINGS")(),
            }
        ]
    },
    "github": {
        # https://docs.allauth.org/en/dev/socialaccount/providers/github.html
        "SCOPE": [
            "user",
            "repo",
            "read:org",
        ],
    },
    # X(Twitter) is setup via App database configuration through admin
    # via oauth2 https://docs.allauth.org/en/dev/socialaccount/providers/twitter_oauth2.html#app-database-configuration-through-admin
    # https://docs.allauth.org/en/dev/socialaccount/providers/twitter.html
    # NOTE: linkedin has deprecated oauth2 support and is now OIDC compliant
    # https://docs.allauth.org/en/dev/socialaccount/providers/linkedin.html
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "linkedin",
                "name": "LinkedIn",
                "client_id": "<insert-id>",
                "secret": "<insert-secret>",
                "settings": {
                    "server_url": "https://www.linkedin.com/oauth",
                },
            }
        ]
    },
}

# Unfold
UNFOLD = {
    "SITE_HEADER": "test-install-chat Admin",
    "SITE_TITLE": "test-install-chat Admin",
    "ENVIRONMENT": "test_install_chat.utils.environment_callback",
    "DASHBOARD_CALLBACK": "test_install_chat.views.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": _("Users & Groups"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": _("Celery Tasks"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Clocked"),
                        "icon": "hourglass_bottom",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_clockedschedule_changelist"
                        ),
                    },
                    {
                        "title": _("Crontabs"),
                        "icon": "update",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_crontabschedule_changelist"
                        ),
                    },
                    {
                        "title": _("Intervals"),
                        "icon": "arrow_range",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_intervalschedule_changelist"
                        ),
                    },
                    {
                        "title": _("Periodic tasks"),
                        "icon": "task",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_periodictask_changelist"
                        ),
                    },
                    {
                        "title": _("Solar events"),
                        "icon": "event",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_solarschedule_changelist"
                        ),
                    },
                ],
            },
        ],
    }
}

# Constance

CONSTANCE_CONFIG = {
    "FACEBOOK_URL": ("", "The URL of the Facebook page"),
    "LINKEDIN_URL": ("", "The URL of the LinkedIn profile"),
    "INSTAGRAM_URL": ("", "The URL of the Instagram profile"),
    "X_URL": ("", "The URL of the X profile"),
    "YOUTUBE_URL": ("", "The URL of the YouTube channel"),
    "TIKTOK_URL": ("", "The URL of the TikTok profile"),
    "GITHUB_URL": ("", "The URL of the GitHub repository/profile"),
    "GOOGLE_ANALYTICS_ID": (
        "",
        "The ID for Google Analytics tracking",
    ),
    "FACEBOOK_PIXEL_ID": ("", "The ID for Facebook Pixel tracking"),
    "META_KEYWORDS": (
        "",
        "Comma-separated list of strings of meta keywords for SEO",
    ),
    "META_DESCRIPTION": ("", "A brief description for SEO purposes"),
    "GOOGLE_CLIENT_ID": ("", "The client ID for Google OAuth"),
    "GOOGLE_CLIENT_SECRET": (
        "",
        "The client secret for Google OAuth",
    ),
    "GOOGLE_KEY": ("", "The API key for Google services"),
    "APPLE_CLIENT_ID": ("", "The client ID for Apple OAuth"),
    "APPLE_SECRET": ("", "The client secret for Apple OAuth"),
    "APPLE_KEY": ("", "The key provided for Apple services"),
    "APPLE_SETTINGS": (
        json.dumps({}),
        "The certificate key for Apple services",
    ),
    "FACEBOOK_CLIENT_ID": ("", "The client ID from Facebook"),
    "FACEBOOK_CLIENT_SECRET": (
        "",
        "The client secret from Facebook",
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Social Media Accounts": {
        "fields": {
            "FACEBOOK_URL",
            "LINKEDIN_URL",
            "INSTAGRAM_URL",
            "X_URL",
            "YOUTUBE_URL",
            "TIKTOK_URL",
            "GITHUB_URL",
        },
    },
    "Analytics": {
        "fields": {
            "GOOGLE_ANALYTICS_ID",
            "FACEBOOK_PIXEL_ID",
            "META_KEYWORDS",
            "META_DESCRIPTION",
        },
    },
    "Apple Social Authentication Keys and Secrets": {
        "APPLE_CLIENT_ID",
        "APPLE_SECRET",
        "APPLE_SETTINGS",
        "APPLE_KEY",
    },
    "Facebook Social Authentication Keys and Secrets": {
        "fields": {
            "FACEBOOK_CLIENT_ID",
            "FACEBOOK_CLIENT_SECRET",
        }
    },
    "Google Social Authentication Keys and Secrets": {
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_KEY",
    },
}

EXCLUDED_KEYS_FOR_API = [
    "GOOGLE_CLIENT_ID",
    "APPLE_CLIENT_ID",
    "APPLE_SECRET",
    "APPLE_SETTINGS",
    "FACEBOOK_CLIENT_ID",
    "FACEBOOK_CLIENT_SECRET",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_KEY",
    "APPLE_KEY",
]
