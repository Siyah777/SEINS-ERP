from decouple import Config, Csv, RepositoryEnv
from .base import *
from pathlib import Path
import os

# Cargar archivo .env.prod
env = Config(RepositoryEnv(BASE_DIR / '.env.prod'))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ["seinsv.com", "www.seinsv.com", "3.86.0.104", "127.0.0.1", "localhost"]

DATABASES = {
    #'dev': {  # Base de datos local SQLite
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / "db.sqlite3",
    #},
    'default': { # base de datos alojada en instanca EC2 de AWS
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),  # IP publica de EC2
        'PORT': config('DB_PORT'),
    }
}
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 14400  # 4 horas en segundos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Cierra sesiÃ³n al cerrar navegador
SESSION_SAVE_EVERY_REQUEST = True  # Renueva sesiÃ³n en cada solicitud

# Si es necesario, personaliza el estilo de los mensajes
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = False
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [
    'https://seinsv.com',
    'https://www.seinsv.com',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/errores.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Configuración API Hacienda
HACIENDA_USER = env('HACIENDA_USER')
HACIENDA_PASSWORD = env('HACIENDA_PASSWORD')
HACIENDA_API_TOKEN_URL = env('HACIENDA_API_TOKEN_URL')
HACIENDA_API_ENVIO_DTE = env('HACIENDA_API_ENVIO_DTE')
HACIENDA_API_ENVIO_DTE_LOTE =env('HACIENDA_API_ENVIO_DTE_LOTE')
HACIENDA_API_ANULACION_DTE = env('HACIENDA_API_ANULACION_DTE')
HACIENDA_API_CONTINGENCIA_DTE = env('HACIENDA_API_CONTINGENCIA_DTE') 

# Configuración firmador
FIRMADOR_URL = env('FIRMADOR_URL')
FIRMADOR_NIT = env('FIRMADOR_NIT')
FIRMADOR_PASSWORD = env('FIRMADOR_PASSWORD')

# Información de la empresa y ambiente DTE
AMBIENTE_DTE = env('AMBIENTE_DTE', default='01')  # '00' para pruebas, '01' para producción
EMPRESA_NIT = env('EMPRESA_NIT')            
EMPRESA_NRC = env('EMPRESA_NRC')
EMPRESA_NOMBRE = env('EMPRESA_NOMBRE')
EMPRESA_ACTIVIDAD_COD = env('EMPRESA_ACTIVIDAD_COD')
EMPRESA_ACTIVIDAD_DESC = env('EMPRESA_ACTIVIDAD_DESC')
EMPRESA_COD_ESTABLE = env('EMPRESA_COD_ESTABLE', default='0001')
EMPRESA_COD_ESTABLE_MH = env('EMPRESA_COD_ESTABLE_MH', default='S001')
EMPRESA_COD_PTO_VTA = env('EMPRESA_COD_PTO_VTA', default='0001')
EMPRESA_COD_PTO_VTA_MH = env('EMPRESA_COD_PTO_VTA_MH', default='P001')
EMPRESA_TELEFONO = env('EMPRESA_TELEFONO', default='75379826')
EMPRESA_CORREO = env('EMPRESA_CORREO', default='administracion@seinsv.com')
EMPRESA_DEPARTAMENTO = env('EMPRESA_DEPARTAMENTO', default='San Salvador')      
EMPRESA_MUNICIPIO = env('EMPRESA_MUNICIPIO', default='San Salvador Este')
EMPRESA_DISTRITO = env('EMPRESA_DISTRITO', default='Tonacatepeque')
EMPRESA_COMPLEMENTO = env('EMPRESA_COMPLEMENTO', default='Urb. Cumbres de San Bartolo, Senda Villa Toledo, Casa 31 Poligono 59')
EMPRESA_NOMBRE_COMERCIAL = env('EMPRESA_NOMBRE_COMERCIAL', default='Servicios Estrategicos Integrales de Ingeniería Salvadoreños (SEINSV)')