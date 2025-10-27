from pathlib import Path
import os
import dj_database_url

# Charger dotenv localement
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECRET & DEBUG
# ========================
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-local')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    'e-commerce-8tpp.onrender.com'
).split(',')

# ========================
# INSTALLED APPS
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ecommerce_app',
    'rest_framework',
    'widget_tweaks',
    'axes',
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',  # Axes à la fin pour bien intercepter
]

# ========================
# AUTH BACKENDS
# ========================
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # nouveau nom Axes
    'django.contrib.auth.backends.ModelBackend',
]

# ========================
# EMAIL
# ========================
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'mba898127@gmail.com')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# ========================
# URLS & WSGI
# ========================
ROOT_URLCONF = 'e_commerce.urls'
WSGI_APPLICATION = 'e_commerce.wsgi.application'

# ========================
# TEMPLATES
# ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]},
    },
]

# ========================
# DATABASE (Local / Prod)
# ========================
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
POSTGRES_LOCALLY = False  # mets True si tu veux tester PostgreSQL localement

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if ENVIRONMENT == 'production' or POSTGRES_LOCALLY:
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        DATABASES['default'] = dj_database_url.parse(DATABASE_URL)
    else:
        print("⚠️ Attention : DATABASE_URL n'est pas défini, utilisation de SQLite par défaut.")

# ========================
# AUTH / LOGIN
# ========================
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'ecom_app:connexion'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# INTERNATIONALISATION
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========================
# STATIC & MEDIA
# ========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "ecommerce_app" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========================
# DEFAULT AUTO FIELD
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
