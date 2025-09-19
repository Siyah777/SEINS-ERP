import csv
import os
from django.conf import settings


_actividades_cache = None

def cargar_actividades():
    global _actividades_cache
    if _actividades_cache is None:
        ruta = os.path.join(settings.BASE_DIR, 'data', 'ACTIVIDADES-ECONÓMICAS.csv')
        _actividades_cache = []
        
        with open(ruta, mode='r', encoding='utf-8-sig') as archivo_csv:
            lector = csv.DictReader(archivo_csv, delimiter=';')
            lector.fieldnames = [h.strip() for h in lector.fieldnames]  # Limpia encabezados
            for fila in lector:
                codigo = fila['CODIGO'].strip()
                nombre = fila['ACTIVIDADES ECONOMICAS'].strip()
                _actividades_cache.append((codigo, nombre))  # Usas el nombre como opción
    return _actividades_cache

def obtener_codigo_actividad(nombre_actividad):
    global _actividades_cache
    if _actividades_cache is None:
        cargar_actividades()
    for codigo, nombre in _actividades_cache:
        if nombre == nombre_actividad:
            return codigo     
    return None  # si no se encuentra
