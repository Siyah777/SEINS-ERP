from django.shortcuts import render
from .models import Actividad
from django.utils.timezone import localtime

def calendario(request):
    actividades = Actividad.objects.all()

    # Preparamos los datos de las actividades en formato de calendario
    eventos = []
    for actividad in actividades:
        evento = {
            'title': actividad.nombre,
            'start': localtime(actividad.fecha_inicio).isoformat(),
            'end': localtime(actividad.fecha_fin).isoformat(),
            'description': actividad.descripcion,
        }
        eventos.append(evento)

    return render(request, 'calendario/calendario.html', {'eventos': eventos})
