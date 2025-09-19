from .base import *
from decouple import Config, Csv, RepositoryEnv
from pathlib import Path
import os

# Cargar archivo .env.dev
env = Config(RepositoryEnv(BASE_DIR / '.env.dev'))

ENV_TYPE = env('ENV_TYPE', default='local')

if ENV_TYPE == 'docker':
    DB_HOST = 'db'
else:
    DB_HOST = '127.0.0.1' if ENV_TYPE == 'local' else 'db'

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', cast=bool, default=True)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', cast=Csv(), default='127.0.0.1,localhost')

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
 #  'default': {  # Base de datos local SQLite
 #      'ENGINE': 'django.db.backends.sqlite3',
 #      'NAME': BASE_DIR / "db.sqlite3",
 #  },
    'default': { 
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': DB_HOST,  
        'PORT': env('DB_PORT'),  
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

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
AMBIENTE_DTE = env('AMBIENTE_DTE', default='00')  # '00' para pruebas, '01' para producción
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