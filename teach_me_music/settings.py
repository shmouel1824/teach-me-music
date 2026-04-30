"""
Django settings for Teach Me Music project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-teach-me-music-change-in-production-xyz123'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'recognition',
    'exercises',
    'dashboard',
    'accounts',
]

# Auth redirects
LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/play/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'teach_me_music.urls'

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

WSGI_APPLICATION = 'teach_me_music.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Asia/Jerusalem'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── ML Model paths ──────────────────────────────────────────
ML_MODELS_DIR = BASE_DIR / 'recognition' / 'ml_models'
NOTE_CLASSIFIER_PATH = ML_MODELS_DIR / 'note_classifier.keras'
LABEL_ENCODER_PATH   = ML_MODELS_DIR / 'label_encoder.pkl'
FEATURE_CONFIG_PATH  = ML_MODELS_DIR / 'feature_config.json'

# ── Audio settings ───────────────────────────────────────────
AUDIO_SAMPLE_RATE = 22050
AUDIO_DURATION    = 1.5   # seconds recorded from browser

# ── Exercise progression ─────────────────────────────────────
# Each level unlocks more notes (DO3 → DO6)
LEVEL_NOTE_RANGES = {
    1: ('DO3', 'DO6'),
    2: ('DO3', 'DO6'),
    3: ('DO3', 'DO6'),
    4: ('DO3', 'DO6'),
}
LEVEL_UP_THRESHOLD = 0.80   # 80% success rate to advance
LEVEL_UP_MIN_EXERCISES = 10 # minimum exercises before leveling up

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}