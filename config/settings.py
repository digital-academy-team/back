import os
from datetime import timedelta
from pathlib import Path
import environ



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("DJANGO_SECRET", '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

# Nginx uzatayotgan protokollarni tanish uchun
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ALLOWED_HOSTS = ['api.yoqubaxmedov.xyz', 'localhost', '127.0.0.1']

ALLOWED_HOSTS = [
    "api.digital-academy.live",
    "127.0.0.1",
    "localhost",
]

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #3th apps
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'rest_framework_simplejwt',

    #locale apps
    'apps.user',
    'apps.quiz',
    'apps.course',
    'apps.order',
    'apps.comments',


]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'common.middleware.block_ip_middleware.BlockIPMiddleware',
    'common.middleware.global_handler.GlobalExceptionLoggingMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CORS_ALLOW_CREDENTIALS = True

# WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}



REST_FRAMEWORK = {

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_RENDERER_CLASSES": [
        "common.renderers.CustomJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "apps.admins.authentication.AdminJWTAuthentication",
        "apps.user.authentication.UserJWTAuthentication",  # oddiy userlar uchun
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'Digital Academy API',
    'DESCRIPTION': 'User va Teacher API hujjatlari',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # ← shu qatorni qo'shing
    'SERVERS': [
        {'url': 'https://api.digital-academy.live', 'description': 'Production server'},
    ],

    'COMPONENT_SPLIT_PATCH': False,
    'APPEND_COMPONENTS': {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    'SECURITY': [
        {
            'Bearer': [],
        }
    ],
}
# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))

# STATIC_URL = '/static/'
# STATIC_ROOT = '/var/www/course_projects/back/static/'
#
# MEDIA_URL = '/media/'
# MEDIA_ROOT = '/var/www/course_projects/back/media/'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
UNHANDLED_ERROR_LOG_FILE = BASE_DIR / "logs" / "unhandled_errors.json"


CSRF_TRUSTED_ORIGINS = [
    'https://api.digital-academy.live',
    'https://www.digital-academy.live',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://api.digital-academy.live",
    "https://edueyesio.digital-academy.live",

]

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-requested-with',
]

AUTH_USER_MODEL = 'user.User'

#jazzmin sozlamalari
JAZZMIN_SETTINGS = {
    "site_title": "Digital Academy Admin",
    "site_header": "Digital Academy",
    "site_brand": "Digital Academy",
    "welcome_sign": "Xush kelibsiz, admin!",
    "copyright": "© Digital Academy",
    "show_ui_builder": True,  # UI builder’ni yoqadi
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cerulean",   # boshqa variantlar: darkly, cerulean, cosmo, minty ...
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "show_ui_builder": True,
}

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)



SITE_URL = os.getenv("SITE_URL")

BASE_URL = os.getenv("BASE_BACKEND_URL")



