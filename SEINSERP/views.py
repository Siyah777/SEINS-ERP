from django.shortcuts import render
from actividades.models import Ordendetrabajo
from django.http import JsonResponse
import os
from django.conf import settings
from django.http import HttpResponse

def resumen_actividades_api(request):
    # Conteo de órdenes por estado
    resumen_actividades = {
        'pendiente': Ordendetrabajo.objects.filter(estatus='pendiente').count(),
        'programado': Ordendetrabajo.objects.filter(estatus='programado').count(),
        'en_proceso': Ordendetrabajo.objects.filter(estatus='en_proceso').count(),
    }

    return JsonResponse(resumen_actividades)

def react_app(request):
    # Lee index.html de tu build de React
    index_file = os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html')
    with open(index_file, 'r', encoding='utf-8') as file:
        content = file.read()
    return HttpResponse(content)