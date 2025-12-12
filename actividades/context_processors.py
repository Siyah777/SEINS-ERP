from actividades.models import Ordendetrabajo
from datetime import timedelta
from django.utils import timezone

from actividades.models import Ordendetrabajo
from datetime import timedelta
from django.utils import timezone

from actividades.models import Ordendetrabajo
from datetime import timedelta
from django.utils import timezone

def resumen_actividades(request):
    try:
        pendientes = Ordendetrabajo.objects.filter(estatus='pendiente').count()
        en_proceso = Ordendetrabajo.objects.filter(estatus='en_proceso').count()
        programadas = Ordendetrabajo.objects.filter(estatus='programado').count()

        return {
            'resumen_actividades': {
                'pendiente': pendientes,
                'programado': programadas,
                'en_proceso': en_proceso,
            },
        }

    except Exception:
        hoy = timezone.now().date()
        return {
            'resumen_actividades': {'pendiente': 0, 'programado': 0, 'en_proceso': 0},
            'inicio_mes': hoy.replace(day=1).strftime("%Y-%m-%d"),
            'fin_mes': hoy.strftime("%Y-%m-%d"),
        }

