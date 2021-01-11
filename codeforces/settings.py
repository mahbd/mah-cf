import os
from pathlib import Path

from corsheaders.defaults import default_headers
from django.core.management.utils import get_random_secret_key
from jwcrypto import jwk
import django_heroku

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = os.path.dirname(__file__)
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = ['http://mah-cf.herokuapp.com/', 'http://127.0.0.1:8000/']

INSTALLED_APPS = [
    'external',
    'api',
    # Built in
    'corsheaders',  #
    'rest_framework',  #
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Enable one of three
    'common.NoCsrfMiddleWare',
    # 'common.JwtCsrfMiddleWare',
    # 'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'codeforces.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'cf_front')],
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

WSGI_APPLICATION = 'codeforces.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'psac',
        'NAME': 'cf',
        'PASSWORD': '1234',
        'TEST': {
            'NAME': 'test_cf',
        },
    },
}

AUTHENTICATION_BACKENDS = ['common.ModelBackendWithJwt']

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Rest framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'common.RestAuthenticateWithJwt',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}

# Heroku
django_heroku.settings(locals())

# Cors Header
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-auth-token',
]

AUTH_USER_MODEL = 'api.User'

# Extra url
# noinspection PyUnresolvedReferences
STATIC_ROOT = os.path.join(PROJECT_DIR, "static/")
# noinspection PyUnresolvedReferences
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
SAFE_URL = ['/api/login/', '/api/register/']
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'cf_front', 'build', 'static'),  # update the STATICFILES_DIRS
)
