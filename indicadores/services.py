from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth

from actividades.models import Ordendetrabajo
from cotizaciones.models import Cotizacion


def obtener_ots(mes=None, anio=None):
    qs = Ordendetrabajo.objects.filter(
        estatus='terminado'
    )

    if anio:
        qs = qs.filter(fecha_fin__year=anio)

    if mes:
        qs = qs.filter(fecha_fin__month=mes)

    return qs


def obtener_cotizaciones(mes=None, anio=None):
    qs = Cotizacion.objects.filter(
        estatus='aprobada'
    )

    if anio:
        qs = qs.filter(fecha__year=anio)

    if mes:
        qs = qs.filter(fecha__month=mes)

    return qs


# ========================
# KPI
# ========================
def resumen_kpis(mes=None, anio=None):

    ots = obtener_ots(mes, anio)
    cot = obtener_cotizaciones(mes, anio)

    return {
        "total_ots": ots.count(),

        "facturacion_total":
        cot.aggregate(total=Sum('total_iva'))['total'] or 0,

        "preventivos":
        ots.filter(
            tipo_actividad='mantenimiento_preventivo'
        ).count(),

        "correctivos":
        ots.filter(
            tipo_actividad='mantenimiento_correctivo'
        ).count(),
    }


# ========================
# CLIENTES TOP
# ========================
def clientes_top(mes=None, anio=None):

    ots = obtener_ots(mes, anio)

    return list(
        ots.values(
            'cliente__nombre_empresa'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]
    )


# ========================
# TIPOS ACTIVIDAD
# ========================
def tipos_actividad(mes=None, anio=None):

    ots = obtener_ots(mes, anio)

    return list(
        ots.values(
            'tipo_actividad'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
    )


# ========================
# COSTOS CLIENTES
# ========================
def costos_clientes(mes=None, anio=None):

    cot = obtener_cotizaciones(mes, anio)

    return list(
        cot.values(
            'cliente__nombre_empresa'
        ).annotate(
            total=Sum('total_iva')
        ).order_by('-total')[:10]
    )


# ========================
# COMPARATIVO MENSUAL
# ========================
def comparativo_mensual(anio):

    return list(
        Cotizacion.objects.filter(
            estatus='aprobada',
            fecha__year=anio
        ).annotate(
            mes=ExtractMonth('fecha')
        ).values('mes').annotate(
            total=Sum('total_iva')
        ).order_by('mes')
    )


# ========================
# TENDENCIA
# ========================
def tendencia_mantenimiento(anio):

    ots = Ordendetrabajo.objects.filter(
        estatus='terminado',
        fecha_fin__year=anio
    )

    preventivos = list(
        ots.filter(
            tipo_actividad='mantenimiento_preventivo'
        ).annotate(
            mes=ExtractMonth('fecha_fin')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')
    )

    correctivos = list(
        ots.filter(
            tipo_actividad='mantenimiento_correctivo'
        ).annotate(
            mes=ExtractMonth('fecha_fin')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')
    )

    return {
        "preventivos": preventivos,
        "correctivos": correctivos
    }
    
# ========================
# EQUIPOS CON MÁS OTs
# ========================
def equipos_top_ots(mes=None, anio=None):

    ots = obtener_ots(mes, anio)

    return list(
        ots.values(
            'equipo__codigo_interno',
            'equipo__nombre'
        ).annotate(
            total=Count('id')
        ).exclude(
            equipo__id__isnull=True
        ).order_by('-total')[:10]
    )


# ========================
# EQUIPOS CON MÁS COSTOS
# ========================
def equipos_top_costos(mes=None, anio=None):

    cot = obtener_cotizaciones(mes, anio)

    return list(
        cot.values(
            'equipo__codigo_interno',
            'equipo__nombre'
        ).annotate(
            total=Sum('total_iva')
        ).exclude(
            equipo__id__isnull=True
        ).order_by('-total')[:10]
    )