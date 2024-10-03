import os
from pathlib import Path
import mimetypes

mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/html", ".html", True)
mimetypes.add_type("text/javascript", ".js", True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_URL = '/app/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "./app/static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

SECRET_KEY = 'django-insecure-@3a$e2qzq3(9-f(-%^7x$f1uznmpwqp9wp6-&st$3wrak#p02h'

DEBUG = False

ASGI_APPLICATION = 'app.asgi.application'


ALLOWED_HOSTS = [
    'www.42transcendence.com',
    '42transcendence.com',
    'localhost'
]

ALLOWED_HOSTS.append(os.getenv('LOCALHOST'))

SECURE_SSL_REDIRECT  =  True 
SESSION_COOKIE_SECURE  =  True 
CSRF_COOKIE_SECURE  =  True 
CSRF_TRUSTED_ORIGINS = ['https://42transcendence.com', 'https://42transcendence.com:8443', os.getenv('REDIRECT_URI')]

AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_AVATAR_BUCKET= os.getenv('AWS_AVATAR_BUCKET')

INSTALLED_APPS = [
    'app',
	'daphne',
	'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    
    'app.middleware.AddTokenMiddleware'
    # 'livesync.core.middleware.DjangoLiveSyncMiddleware',
    # 'django_livesync.middleware.DjangoLiveSyncMiddleware',
]

ROOT_URLCONF = 'app.urls'

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

# WSGI_APPLICATION = 'app.wsgi.application'
ASGI_APPLICATIOn = 'app.asgi.application'

CHANNEL_LAYERS = {
	'default': {
		"BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv('SQL_DATABASE'),
#         'USER': os.getenv('SQL_USER'),
#         'PASSWORD': os.getenv('SQL_PASSWORD'),
#         'HOST': os.getenv('SQL_HOST'),
#         'PORT': os.getenv('SQL_PORT'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('SQL_DATABASE'),
        'USER': os.getenv('SQL_USER'),
        'PASSWORD': os.getenv('SQL_PASSWORD'),
        'HOST': os.getenv('SQL_HOST'),
        'PORT': os.getenv('SQL_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [f'redis://{os.getenv("REDIS_HOST", "redis")}:6379'],
        },
    },
}
