"""
Django settings for pizza project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from django.urls import reverse_lazy, reverse

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


root = lambda *paths: os.path.join(BASE_DIR, *paths)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'x_0rmr2450sbs@eb231qug=9ky%^6xm$5!_5fl)i#lhy8*^ht0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'rest_framework',
    'easy_thumbnails',
    'django_filters',
    'adminsortable2',
    'djcelery',
    'parler',

    'core',
    'users',
    'catalog',
    'cart',

    'rosetta',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.GeoLocationMiddleware'
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.categories_processor',
                'core.context_processors.location_list',
                'core.context_processors.site_config'
            ],
        },
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'sms': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pizza',
        'USER': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': 5432
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

RUSSIAN_LANG = 'ru'
ENGLISH_LANG = 'en'

LANGUAGE_CODE = RUSSIAN_LANG

LANGUAGES = (
    (ENGLISH_LANG, _("english")),
    (RUSSIAN_LANG, _("russian")),
)

PARLER_DEFAULT_LANGUAGE = RUSSIAN_LANG

PARLER_DEFAULT_LANGUAGE_CODE = RUSSIAN_LANG

PARLER_DEFAULT_ACTIVATE = True

PARLER_LANGUAGES = {
    None: (
        {'code': 'ru'},
        {'code': 'en'}
    ),
    'default': {
        'fallback': 'ru',
        'hide_untranslated': False,   # the default; let .active_translations() return fallbacks too.
    }
}

LANGUAGE_COOKIE_NAME = 'lang'

LOCALE_PATHS = (
    root('pizza', 'core', 'locale'),
)

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = root('static')
MEDIA_ROOT = root('media')

AUTH_USER_MODEL = 'users.AppUser'

THUMBNAIL_ALIASES = {
    '': {
        'preview': {'size': (150, 90), 'crop': False},
        'cart': {'size': (80, 40), 'crop': False},
        'special': {'size': (145, 91), 'crop': False},
    },
}

# sms service credentials
SMS_SERVICE_CREDENTIALS = (
    'login',
    'password'
)
SMS_SERVICE_SOURCE = 'Pizza Rally'
SMS_SERVICE_HOST = 'https://integrationapi.net/rest'
SMS_SERVICE_DEBUG = False
SMS_SERVICE_MAX_REPEAT = 5
SMS_SERVICE_COUNTDOWN_SEC = 5
SMS_SERVICE_TIMEOUT_SEC = 20

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.SmsCodeBackend'
]

PASSWORD_CHANGE_ATTEMPTS = 3
PASSWORD_CHANGE_TIMEOUTS = 60 * 5

LOGIN_URL = '/admin'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'sms': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': root('logs/sms.log'),
        },
    },
    'loggers': {
        'devino.client': {
            'handlers': ['sms'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
JET_THEMES = [
    {
        'theme': 'default', # theme folder name
        'color': '#47bac1', # color of the theme's button in user menu
        'title': 'Default' # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

JET_SIDE_MENU_COMPACT = True

JET_SIDE_MENU_ITEMS = [
    {'label': _("Config"),
     'permissions': ['core.siteconfiguration'],
     'items': [
        {'label': _('Translations'), 'url': '/admin/rosetta', 'permissions': ['core.siteconfiguration']},
        {'label': _("Site config"), 'name': 'core.siteconfiguration', 'permissions': ['core.siteconfiguration']},
        {'label': _("Social links"), 'name': 'core.sociallink', 'permissions': ['core.sociallink']},
        {'label': _("SMS templates"), 'name': 'core.smstemplate', 'permissions': ['core.smstemplate']},
        {'label': _("Locations"), 'name': 'core.location', 'permissions': ['core.location']},
    ]},
    {'label': _("General"),
     'permissions': ['users.appuser', 'auth.group', 'users.phoneverification', 'cart.order'],
     'items': [
        {'label': _("Users"), 'name': 'users.appuser', 'permissions': ['users.appuser']},
        {'label': _("Groups"), 'name': 'auth.group', 'permissions': ['auth.group']},
        {'label': _("Phone verifications"), 'name': 'users.phoneverification', 'permissions': ['users.phoneverification']},
        {'label': _("Orders"), 'name': 'cart.order', 'permissions': ['cart.order']}
    ]},
    {'label': _("Misc"),
     'permissions': ['core.action', 'catalog.category', 'catalog.product'],
     'items': [
        {'label': _("Actions"), 'name': 'core.action', 'permissions': ['core.action']},
        {'label': _("Categories"), 'name': 'catalog.category', 'permissions': ['catalog.category']},
        {'label': _("Products"), 'name': 'catalog.product', 'permissions': ['catalog.product']},
        {'label': _("Streets"), 'name': 'core.availablestreet', 'permissions': ['core.availablestreet']},
    ]}
]

MANAGER_GROUP_NAME = 'managers'

LOCATION_COOKIE_NAME = 'location'

DEFAULT_LOCATION_ID = 2

TELEGRAM_BOT_TOKEN = '388465077:AAFYzfBMr_K6APSHnsajfU3j7CpJ-M8iEGg'

try:
    from local_settings import *
except:
    pass

