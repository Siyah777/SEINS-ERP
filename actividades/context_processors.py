from actividades.models import Ordendetrabajo

def resumen_actividades(request):
    try:
        return {
            'resumen_actividades': {
                'pendiente': Ordendetrabajo.objects.filter(estatus='pendiente').count(),
                'programado': Ordendetrabajo.objects.filter(estatus='programado').count(),
                'en_proceso': Ordendetrabajo.objects.filter(estatus='en_proceso').count(),
            }
        }
    except Exception:
        # En caso de que la BD no esté lista (por ejemplo, durante migraciones)
        return {'resumen_actividades': {'pendiente': 0, 'programado': 0, 'en_proceso': 0}}
