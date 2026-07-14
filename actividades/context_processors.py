from django.utils import timezone
from actividades.models import Ordendetrabajo
from cotizaciones.models import Cotizacion



def resumen_actividades(request):
    try:
        base_queryset = Ordendetrabajo.objects.filter(
            estatus__in=['pendiente', 'en_proceso', 'programado']
        )
        criticas = base_queryset.filter(prioridad='critica').count()
        altas = base_queryset.filter(prioridad='alta').count()
        medias = base_queryset.filter(prioridad='media').count()

        pendientes = Ordendetrabajo.objects.filter(estatus='pendiente').count()
        en_proceso = Ordendetrabajo.objects.filter(estatus='en_proceso').count()
        programadas = Ordendetrabajo.objects.filter(estatus='programado').count()
        cotizaciones_pendientes = Cotizacion.objects.filter(
            estatus='pendiente'
        ).count()

        return {
            'resumen_actividades': {
                'pendiente': pendientes,
                'programado': programadas,
                'en_proceso': en_proceso,
                'cotizaciones_pendientes': cotizaciones_pendientes,
                'criticas': criticas,
                'altas': altas,
                'medias': medias,
            },
        }

    except Exception as e:
        print("ERROR context processor:", e)

        return {
            'resumen_actividades': {
                'pendiente': 0,
                'programado': 0,
                'en_proceso': 0,
                'cotizaciones_pendientes': 0,
                'criticas': 0,
                'altas': 0,
            },
        }