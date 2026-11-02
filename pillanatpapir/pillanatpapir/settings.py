"""
Django settings for pillanatpapir project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# --- Alapok ---

# Fejlesztéshez van egy alapértelmezett kulcs. Élesben környezeti változóból jöjjön.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or 'dev-only-change-this-key-before-deployment'

# Élesben: DJANGO_DEBUG=0
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'

ALLOWED_HOSTS = [] if DEBUG else os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
if not DEBUG and not os.environ.get('DJANGO_SECRET_KEY'):
    raise RuntimeError('DJANGO_SECRET_KEY környezeti változó szükséges éles módban.')


# --- Alkalmazások ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hitelugyintezo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pillanatpapir.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'pillanatpapir.wsgi.application'


# --- Adatbázis ---

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- Jelszavak ---

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Az Argon2 a legerősebb, a régi PBKDF2 hash-ek is működnek tovább.
# Kell hozzá: pip install argon2-cffi
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

PASSWORD_RESET_TIMEOUT = 60 * 60            # a visszaállító link 1 óráig érvényes


# --- Bejelentkezés ---

LOGIN_URL = 'index'
LOGIN_REDIRECT_URL = 'dokumentumok_listaja'
LOGOUT_REDIRECT_URL = 'index'

SESSION_COOKIE_AGE = 60 * 60 * 24 * 14      # 14 nap
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')


# --- E-mail (Django 6.1: MAILERS) ---
# Fejlesztés közben a levelek a terminálban jelennek meg.
# Az EMAIL_BACKEND-et NEM szabad megadni, amíg a MAILERS definiálva van.

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

DEFAULT_FROM_EMAIL = 'Pillanatpapír <noreply@pillanatpapir.hu>'


# --- Nyelv és idő ---

LANGUAGE_CODE = 'hu'
TIME_ZONE = 'Europe/Budapest'
USE_I18N = True
USE_TZ = True


# --- Statikus fájlok ---

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Éles környezet ---

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000

TESSERACT_CMD = os.environ.get('TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b')
