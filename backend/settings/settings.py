"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 1.10.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

from backend.settings.project_config import *
from celery.schedules import crontab
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mkdocs Documentation Settings
DOCUMENTATION_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'aov_mkdocs'))
DOCUMENTATION_HTML_ROOT = DOCUMENTATION_ROOT + "/site/"
DOCUMENTATION_ACCESS_FUNCTION = lambda user: user.is_staff
DOCUMENTATION_XSENDFILE = not DEBUG

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&ovy=!!3@8s@68950+td&##!n!=(&vh_at@j71kti&pu^@2k%_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG
ADMINS = (
    ("Garrett", "garrett@artofvisuals.com"),
)

INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)

ALLOWED_HOSTS = ['*']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'corsheaders',
    'imagekit',
    'storages',
    'apps.account',
    'apps.analytic',
    'apps.communication',
    'apps.discover',
    'apps.marketplace', # Development halted
    'apps.podcast',
    'apps.photo.apps.PhotoConfig',
    'apps.quote',
    'apps.utils',
    'dbmail',
    'guardian',
    'push_notifications',
    'rest_framework',
    'rest_framework.authtoken',
    'social_django',
    'rest_framework_tracking',
    'fcm_django',
    'rangefilter',
    'aov_mkdocs',
]

# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']

SITE_ID = 1

MIDDLEWARE = list()

# if DEBUG:
#     MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'apps.common.middleware.UserSessionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'


# Admin

JET_DEFAULT_THEME = 'default'

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

JET_INDEX_DASHBOARD = 'apps.common.dashboard.AOVDashboard'

JET_SIDE_MENU_COMPACT = True

JET_SIDE_MENU_ITEMS = [
    {'label': 'Account',
    'app_label': 'account', 'items': [
        {'name': 'gear'},
        {'name': 'profile'},
        {'name': 'starreduser'},
        {'name': 'userinterest'},
        {'name': 'userlocation'},
        {'name': 'usersession'},
        {'name': 'user'},
    ]},
    {'app_label': 'authtoken', 'items': [
        {'name': 'token'},
    ]},
    {'app_label': 'auth', 'items': [
        {'name': 'group'},
    ]},
    {'app_label': 'communication', 'items': [
        {'name': 'conversation'},
        {'name': 'pushnotificationrecord'},
        {'name': 'pushmessage'},
    ]},
    {'app_label': 'discover', 'items': [
        {'name': 'downloader'},
        {'name': 'photographer'},
        {'name': 'sponsor'},
        {'name': 'statephotographer'},
        {'name': 'statephoto'},
        {'name': 'statesponsor'},
        {'name': 'state'},
    ]},
    {'app_label': 'fcm_django', 'items': [
        {'name': 'fcmdevice'},
    ]},
    {'app_label': 'guardian', 'items': [
        {'name': 'userobjectpermission'},
    ]},
    {'app_label': 'photo', 'items': [
        {'name': 'photofeedphoto'},
        {'name': 'photofeed'},
        {'name': 'flaggedphoto'},
        {'name': 'gallery'},
        {'name': 'photocomment'},
        {'name': 'photoclassification'},
        {'name': 'photo'},
        {'name': 'starredphoto'},
    ]},
    {'app_label': 'podcast', 'items': [
        {'name': 'camera'},
        {'name': 'episode'},
        {'name': 'getfeaturedrequest'},
        {'name': 'podcastimage'},
        {'name': 'requester'},
    ]},
    {'app_label': 'push_notifications', 'items': [
        {'name': 'apnsdevice'},
    ]},
    {'app_label': 'quote', 'items': [
        {'name': 'quotesubscriber'},
        {'name': 'quote'},
    ]},
    {'app_label': 'rest_framework_tracking', 'items': [
        {'name': 'apirequestlog'},
    ]},
    {'app_label': 'utils', 'items': [
        {'name': 'feedback'},
        {'name': 'useraction'},
    ]},
    {'app_label': 'dbmail', 'items': [
        {'name': 'MailTemplate'},
    ]}
]


# Templates
# Enable caching for staging and production

if TEMPLATE_OPTIONS['LOADERS']:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                'loaders': TEMPLATE_OPTIONS['LOADERS']
            },
        },
    ]
else:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

WSGI_APPLICATION = 'backend.wsgi.application'

# Social auth

SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email',
}

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_FACEBOOK_SECRET = SOCIAL_AUTH_FACEBOOK_SECRET

# Celery settings

BROKER_URL = BROKER_URL

CELERY_ACCEPT_CONTENT = ['json']

CELERY_RESULT_BACKEND = CELERY_RESULT_BACKEND

CELERYBEAT_SCHEDULE = {
    'send-push-messages': {
        'task': 'send_scheduled_push_notifications',
        'schedule': crontab()  # Executes every minute
    },
}

# Communication

DB_MAILER_SHOW_CONTEXT = True
DB_MAILER_ALLOWED_MODELS_ON_ADMIN = [
    'MailTemplate'
]

EMAIL_BACKEND = EMAIL['EMAIL_BACKEND']
EMAIL_USE_TLS = EMAIL['EMAIL_USE_TLS']
EMAIL_HOST = EMAIL['EMAIL_HOST']
EMAIL_PORT = EMAIL['EMAIL_PORT']
EMAIL_HOST_PASSWORD = EMAIL['EMAIL_HOST_PASSWORD']
EMAIL_HOST_USER = EMAIL['EMAIL_HOST_USER']
DEFAULT_FROM_EMAIL = EMAIL['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = EMAIL['SERVER_EMAIL']

CACHES = CACHES

FCM_DJANGO_SETTINGS = FCM_DJANGO_SETTINGS

PUSH_NOTIFICATIONS_SETTINGS = {
    'APNS_CERTIFICATE': APNS_CERTIFICATE,
    'APNS_ERROR_TIMEOUT': 0.4
}


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = DATABASES


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Boise'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'PAGE_SIZE': 12,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

CORS_ORIGIN_ALLOW_ALL = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATIC_ROOT = '/var/media/backend/static'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


# Image Storage

REMOTE_IMAGE_STORAGE = STORAGE['REMOTE_IMAGE_STORAGE']
REMOTE_AUDIO_STORAGE = STORAGE['REMOTE_AUDIO_STORAGE']

if REMOTE_AUDIO_STORAGE:
    AWS_AUDIO_BUCKET = STORAGE["AUDIO_BUCKET_NAME"]


if REMOTE_IMAGE_STORAGE:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = STORAGE['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = STORAGE['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = STORAGE['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_REGION_NAME = 'us-west-2'

    MEDIA_URL = 'http://{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
    ORIGINAL_MEDIA_URL = 'http://{}.s3.amazonaws.com/'.format(STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    ORIGINAL_MEDIA_URL = MEDIA_URL

# Misc

AUTH_USER_MODEL = 'account.User'
PROFILE_USER = PROFILE_USER
PROFILE_PASSWORD = PROFILE_PASSWORD
