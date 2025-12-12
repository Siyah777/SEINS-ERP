from datetime import timedelta
from django.utils import timezone
from actividades.models import Ordendetrabajo


def generar_ots(detalle, cantidad=1):
    """
    Genera múltiples OTs basadas en un DetallePlanMantenimiento.
    Combina datos de:
    - COTIZACIÓN
    - PLAN DE MANTENIMIENTO
    - DETALLE DEL PLAN

    'cantidad' define cuántas OTs generar hacia adelante.
    """

    cot = detalle.cotizacion
    plan = detalle.plan

    if not cot:
        return []

    if not detalle.fechainicio:
        return []

    ots_creadas = []
    fecha = detalle.fechainicio

    # límite: evitar crear OTs más allá de 1 año
    hoy = timezone.now().date()
    limite = hoy + timedelta(days=365)

    for _ in range(cantidad):

        # no generar más allá del límite
        if fecha > limite:
            break

        # evitar duplicados por cotización + fecha
        existe = Ordendetrabajo.objects.filter(
            cotizacion=cot,
            fecha_inicio=fecha
        ).exists()

        if not existe:
            # ------------------------------------------------------------
            # CREAR OT
            # ------------------------------------------------------------
            ot = Ordendetrabajo.objects.create(
                cotizacion=cot,
                cliente=cot.cliente,
                descripcion=f"{cot.Descripcion} — Generado por Plan: {plan.codigo_plan}",
                fecha_inicio=fecha,
                estatus="programado",
                prioridad="media",
                tipo_actividad="mantenimiento_preventivo",
                horarios_actividad=detalle.horarios_actividad,
                horas_hombre_estimadas=getattr(detalle, "horas_estimadas", 0),
                detalleplan=detalle  # ← ENLACE TRAZABLE DEL PLAN A LA OT
            )

            # ------------------------------------------------------------
            # RELACIONES M2M
            # ------------------------------------------------------------

            # 1. Equipos desde la cotización
            if hasattr(cot, "equipo") and cot.equipo.exists():
                ot.equipo.set(cot.equipo.all())

            # 2. Repuestos
            if hasattr(cot, "repuestos") and cot.repuestos.exists():
                ot.repuestos.set(cot.repuestos.all())

            # 3. Herramientas definidas en el plan
            if hasattr(detalle, "herramientas_necesarias") and detalle.herramientas_necesarias.exists():
                ot.herramientas_necesarias.set(detalle.herramientas_necesarias.all())

            # 4. Documentos del detalle del plan
            if hasattr(detalle, "documentos") and detalle.documentos.exists():
                ot.documentos.set(detalle.documentos.all())

            # ------------------------------------------------------------
            # ACTIVIDADES ASOCIADAS (si tu modelo las tiene)
            # ------------------------------------------------------------
            if hasattr(detalle, "detalles"):
                for det in detalle.detalles.all():
                    ot.detalles.create(
                        actividad=det.actividad,
                        duracion_estimada=det.duracion_estimada,
                        materiales=det.materiales,
                        herramientas_adicionales=list(det.herramientas.all())
                    )

            ots_creadas.append(ot)

        # ------------------------------------------------------------
        # CALCULAR LA SIGUIENTE FECHA
        # ------------------------------------------------------------

        frecuencia = detalle.frecuencia

        if frecuencia == "cada_8_horas":
            fecha += timedelta(hours=8)
        elif frecuencia == "diario":
            fecha += timedelta(days=1)
        elif frecuencia == "semanal":
            fecha += timedelta(days=7)
        elif frecuencia == "quincenal":
            fecha += timedelta(days=15)
        elif frecuencia == "mensual":
            fecha += timedelta(days=30)
        elif frecuencia == "bimensual":
            fecha += timedelta(days=60)
        elif frecuencia == "trimestral":
            fecha += timedelta(days=90)
        elif frecuencia == "semestral":
            fecha += timedelta(days=180)
        elif frecuencia == "anual":
            fecha += timedelta(days=365)
        elif frecuencia == "personalizado":
            fecha += timedelta(days=detalle.dias_personalizados)

    # ------------------------------------------------------------
    # ACTUALIZAR PROXIMA FECHA DEL DETALLE
    # ------------------------------------------------------------
    detalle.proxima_fecha = fecha
    detalle.save()

    return ots_creadas




