"""
Django settings for Teach Me Music project.
Production-ready for Railway deployment.
"""
import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-teach-me-music-change-in-production-xyz123'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1'
).split(',')

# ── Apps ──────────────────────────────────────────────────────
INSTALLED_APPS = [
    'jazzmin',   # MUST be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recognition',
    'exercises',
    'dashboard',
    'accounts',
]

# ── Jazzmin ───────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title":    "Teach Me Music",
    "site_header":   "Teach Me Music",
    "site_brand":    "𝄞 Teach Me Music",
    "site_logo":     None,
    "welcome_sign":  "Welcome to the Teach Me Music admin panel",
    "copyright":     "Teach Me Music — Sirius Academy",
    "search_model":  ["auth.user", "exercises.exercise", "exercises.notestats"],
    "topmenu_links": [
        {"name": "🎹 Back to App",   "url": "/play/",      "new_window": False, "icon": "fas fa-music"},
        {"name": "📊 Dashboard",      "url": "/dashboard/", "new_window": False, "icon": "fas fa-chart-bar"},
        {"name": "🏠 Admin Home",     "url": "admin:index", "icon": "fas fa-home"},
    ],
    "usermenu_links": [
        {"name": "🎹 Open App", "url": "/play/", "new_window": False, "icon": "fas fa-music"},
        {"model": "auth.user"},
    ],
    "show_sidebar":          True,
    "navigation_expanded":   True,
    "order_with_respect_to": ["auth", "exercises", "recognition", "accounts", "dashboard"],
    "custom_links": {
        "exercises": [
            {"name": "🎹 Open App",           "url": "/play/",      "icon": "fas fa-music"},
            {"name": "📊 Progress Dashboard", "url": "/dashboard/", "icon": "fas fa-chart-line"},
        ],
    },
    "icons": {
        "auth":                "fas fa-users-cog",
        "auth.user":           "fas fa-user",
        "auth.Group":          "fas fa-users",
        "exercises":           "fas fa-music",
        "exercises.Session":   "fas fa-calendar-alt",
        "exercises.Exercise":  "fas fa-tasks",
        "exercises.NoteStats": "fas fa-chart-bar",
        "recognition":         "fas fa-brain",
        "accounts":            "fas fa-user-lock",
    },
    "default_icon_parents":  "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "related_modal_active":  True,
    "custom_css":            "admin/css/jazzmin_custom.css",
    "use_google_fonts_cdn":  True,
    "show_ui_builder":       False,
    "changeform_format":     "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "accent":                   "accent-warning",
    "navbar":                   "navbar-dark",
    "no_navbar_border":         True,
    "navbar_fixed":             True,
    "sidebar_fixed":            True,
    "sidebar":                  "sidebar-dark-warning",
    "sidebar_nav_child_indent": True,
    "theme":                    "darkly",
    "dark_mode_theme":          "darkly",
}

# ── Auth ──────────────────────────────────────────────────────
LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/play/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ── Middleware ────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

# ── Database ──────────────────────────────────────────────────
# Railway sets DATABASE_URL automatically when PostgreSQL is added
# Locally falls back to SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = []

# ── Internationalisation ──────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Asia/Jerusalem'
USE_I18N      = True
USE_TZ        = True

# ── Static files ──────────────────────────────────────────────
STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── ML model paths ────────────────────────────────────────────
ML_MODELS_DIR        = BASE_DIR / 'recognition' / 'ml_models'
NOTE_CLASSIFIER_PATH = ML_MODELS_DIR / 'note_classifier.keras'
LABEL_ENCODER_PATH   = ML_MODELS_DIR / 'label_encoder.pkl'
FEATURE_CONFIG_PATH  = ML_MODELS_DIR / 'feature_config.json'

# ── Audio ─────────────────────────────────────────────────────
AUDIO_SAMPLE_RATE = 22050
AUDIO_DURATION    = 1.5

# ── Exercise progression ──────────────────────────────────────
LEVEL_NOTE_RANGES      = {1:('DO3','DO6'), 2:('DO3','DO6'), 3:('DO3','DO6'), 4:('DO3','DO6')}
LEVEL_UP_THRESHOLD     = 0.80
LEVEL_UP_MIN_EXERCISES = 10

# ── CSRF — critical for Railway ───────────────────────────────
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000'
).split(',')

# ── Cookie security ───────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE   = not DEBUG
CSRF_COOKIE_SECURE      = not DEBUG

# ── Logging ───────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root':     {'handlers': ['console'], 'level': 'INFO'},
}