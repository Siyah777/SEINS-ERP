from django.shortcuts import render
from actividades.models import Ordendetrabajo

def react_app(request):
    # Conteo de órdenes por estado
    resumen_actividades = {
        'pendiente': Ordendetrabajo.objects.filter(estatus='pendiente').count(),
        'programado': Ordendetrabajo.objects.filter(estatus='programado').count(),
        'en_proceso': Ordendetrabajo.objects.filter(estatus='en_proceso').count(),
    }

    # Renderiza el template y envía el contexto
    return render(request, 'admin/index.html', {
        'resumen_actividades': resumen_actividades
    })

