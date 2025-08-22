from decouple import config
import os
from corsheaders.defaults import default_headers
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('WORK_MODE')
INSTALLED_APPS = [
    'vieZ',
    'smartnote',
    'vieclamvp',
    'django_filters',
    'company',
    'pheduyet_zalo',
    'rest_framework',
    'oauth2_provider',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24 * 15,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24 * 30,  # 7 ngày
    'ROTATE_REFRESH_TOKEN': True,            # mỗi lần refresh sẽ đổi refresh_token
}
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'core.urls'
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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4'",
        },
    }
}
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
GOOGLE_API_KEY= config('GOOGLE_API_KEY')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = False  # (dev local thôi)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5175",
    "http://localhost:4687",
    "http://10.100.1.50:3000",
    "https://vieclamvp.vn",
    "https://api.vieclamvp.vn",
    "https://hl-djc.vieclamvp.vn",
    "https://ipays.vn",
    "https://api.ipays.vn",
    'https://h5.zdn.vn',
    'zbrowser://h5.zdn.vn',
    'https://h5.zadn.vn',
    'zbrowser://h5.zadn.vn',
]
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '10.100.1.50',
    '10.100.1.10',
    'vieclamvp.vn',
    'api.vieclamvp.vn',
    'api.ipays.vn',
    'https://h5.zdn.vn',
    'zbrowser://h5.zdn.vn',
    'https://h5.zadn.vn',
    'zbrowser://h5.zadn.vn',
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    'authorization',
    'x-csrf-token',
    'access-control-allow-origin',
    'ApplicationKey',
    'Companykey',
    'StoreKey',
]
CSRF_TRUSTED_ORIGINS = [
    "https://api.ipays.vn",
    "https://www.ipays.vn",
]

CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(CORE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'
MEDIA_ROOT = f'{CORE_DIR}/uploads/'