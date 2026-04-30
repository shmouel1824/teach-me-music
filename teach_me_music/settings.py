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
    # ── Jazzmin MUST come before django.contrib.admin ──────
    'jazzmin',

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

# ══════════════════════════════════════════════════════════════
#  JAZZMIN — Admin UI
#  Palette: deep navy + warm gold, matching the app exactly
# ══════════════════════════════════════════════════════════════
JAZZMIN_SETTINGS = {
    # ── Branding ───────────────────────────────────────────
    "site_title":        "Teach Me Music",
    "site_header":       "Teach Me Music",
    "site_brand":        "𝄞 Teach Me Music",
    "site_logo":         None,
    "site_logo_classes": "img-circle",
    "site_icon":         None,
    "welcome_sign":      "Bienvenue dans le panneau d'administration",
    "copyright":         "Teach Me Music — Sirius Academy",

    # ── Search ─────────────────────────────────────────────
    "search_model": ["auth.user", "exercises.exercise", "exercises.notestats"],

    # ── Top menu — contains the link back to the app ────────
    "topmenu_links": [
        {
            "name":       "🎹 Retour à l'app",
            "url":        "/play/",
            "new_window": False,
            "icon":       "fas fa-music",
        },
        {
            "name":       "📊 Tableau de bord",
            "url":        "/dashboard/",
            "new_window": False,
            "icon":       "fas fa-chart-bar",
        },
        {
            "name":       "🏠 Accueil admin",
            "url":        "admin:index",
            "icon":       "fas fa-home",
        },
    ],

    # ── User menu (top-right avatar dropdown) ───────────────
    "usermenu_links": [
        {
            "name":       "🎹 Ouvrir l'app",
            "url":        "/play/",
            "new_window": False,
            "icon":       "fas fa-music",
        },
        {"model": "auth.user"},
    ],

    # ── Sidebar ─────────────────────────────────────────────
    "show_sidebar":          True,
    "navigation_expanded":   True,
    "hide_apps":             [],
    "hide_models":           [],

    "order_with_respect_to": [
        "auth",
        "exercises",
        "recognition",
        "accounts",
        "dashboard",
    ],

    # Custom sidebar quick-links under the exercises section
    "custom_links": {
        "exercises": [
            {
                "name": "🎹 Ouvrir l'app",
                "url":  "/play/",
                "icon": "fas fa-music",
            },
            {
                "name": "📊 Tableau de bord élève",
                "url":  "/dashboard/",
                "icon": "fas fa-chart-line",
            },
        ],
    },

    # ── FontAwesome icons per model ─────────────────────────
    "icons": {
        "auth":                  "fas fa-users-cog",
        "auth.user":             "fas fa-user",
        "auth.Group":            "fas fa-users",
        "exercises":             "fas fa-music",
        "exercises.Session":     "fas fa-calendar-alt",
        "exercises.Exercise":    "fas fa-tasks",
        "exercises.NoteStats":   "fas fa-chart-bar",
        "recognition":           "fas fa-brain",
        "accounts":              "fas fa-user-lock",
    },
    "default_icon_parents":  "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # ── Misc UI ─────────────────────────────────────────────
    "related_modal_active":    True,
    "custom_css":              "admin/css/jazzmin_custom.css",
    "custom_js":               None,
    "use_google_fonts_cdn":    True,
    "show_ui_builder":         False,
    "changeform_format":       "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user":  "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text":        False,
    "footer_small_text":        False,
    "body_small_text":          False,
    "brand_small_text":         False,
    "brand_colour":             False,
    "accent":                   "accent-warning",
    "navbar":                   "navbar-dark",
    "no_navbar_border":         True,
    "navbar_fixed":             True,
    "layout_boxed":             False,
    "footer_fixed":             False,
    "sidebar_fixed":            True,
    "sidebar":                  "sidebar-dark-warning",
    "sidebar_nav_small_text":   False,
    "sidebar_disable_expand":   False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style":False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style":   False,
    "theme":                    "darkly",
    "dark_mode_theme":          "darkly",
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
}

# ══════════════════════════════════════════════════════════════
#  Rest of settings (unchanged from original)
# ══════════════════════════════════════════════════════════════

LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/play/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ML_MODELS_DIR        = BASE_DIR / 'recognition' / 'ml_models'
NOTE_CLASSIFIER_PATH = ML_MODELS_DIR / 'note_classifier.keras'
LABEL_ENCODER_PATH   = ML_MODELS_DIR / 'label_encoder.pkl'
FEATURE_CONFIG_PATH  = ML_MODELS_DIR / 'feature_config.json'

AUDIO_SAMPLE_RATE = 22050
AUDIO_DURATION    = 1.5

LEVEL_NOTE_RANGES = {
    1: ('DO3', 'DO6'),
    2: ('DO3', 'DO6'),
    3: ('DO3', 'DO6'),
    4: ('DO3', 'DO6'),
}
LEVEL_UP_THRESHOLD     = 0.80
LEVEL_UP_MIN_EXERCISES = 10

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
