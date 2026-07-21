"""
Django settings for leravi_api project.
"""

from pathlib import Path
import os 
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 1. SEGURIDAD Y ENTORNO (Render / Local)
# ==========================================
# Se extrae de variables de entorno, con un respaldo para desarrollo local
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-uu0r2&!*9)l==ic#@a!zsxf$%gyje!mn+20z(v-yd#f1ma1z$t')

# DEBUG será True en tu computadora, pero al subir a Render debes configurarlo como False
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Se lee la URL de Render desde el entorno, permitiendo localhost por defecto
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'nucleo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # OBLIGATORIO: Para servir estáticos en Render
    'corsheaders.middleware.CorsMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'leravi_api.urls'

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

WSGI_APPLICATION = 'leravi_api.wsgi.application'


# ==========================================
# 2. BASE DE DATOS (Aiven MySQL)
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'leravi_db'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASS', 'tu_password_seguro'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            # Aplica el certificado SSL solo si estamos en producción (DEBUG=False)
            # Esto evita que Docker local falle al intentar usar SSL, pero cumple con Aiven
            'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'} if not DEBUG else {}
        }
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==========================================
# 3. INTERNACIONALIZACIÓN Y ZONA HORARIA
# ==========================================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Hermosillo' # Zona horaria configurada para el estado de Sonora
USE_I18N = True
USE_TZ = True


# ==========================================
# 4. ARCHIVOS ESTÁTICOS (Render)
# ==========================================
STATIC_URL = 'static/'
# Directorio donde Render recopilará los archivos del panel de administrador
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# ==========================================
# 5. CONFIGURACIÓN DE CORS (Vercel)
# ==========================================
CORS_ALLOW_ALL_ORIGINS = False
# Lista blanca estricta: Solo permite peticiones desde tu Vercel y tu servidor local
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173'
).split(',')


# ==========================================
# 6. CONFIGURACIÓN DE JWT
# ==========================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',
}

# ==========================================
# 7. MODELO DE USUARIO PERSONALIZADO
# ==========================================
AUTH_USER_MODEL = 'nucleo.Usuario'
