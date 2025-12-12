from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .utils import generar_ots
from .models import PlanMantenimiento, DetallePlanMantenimiento
from django.urls import reverse


def generar_ots_view(request, plan_id):
    """
    Genera varias OTs por cada detalle del plan según su configuración.
    """
    plan = get_object_or_404(PlanMantenimiento, id=plan_id)
    detalles = DetallePlanMantenimiento.objects.filter(plan=plan)

    ots_generadas = []

    for detalle in detalles:

        # cada detalle decide cuántas generar
        cantidad = getattr(detalle, "cantidad_autogenerada", 1)

        nuevas = generar_ots(detalle, cantidad=cantidad)

        ots_generadas.extend(nuevas)

    # Mensajes
    if ots_generadas:
        messages.success(
            request,
            f"Se generaron {len(ots_generadas)} OT(s) para el plan {plan.codigo_plan}."
        )
    else:
        messages.info(
            request,
            f"No se generaron nuevas OTs. Es posible que ya existan o no correspondan."
        )

    return redirect('planes_mantenimiento:detalle_plan', plan_id=plan.id)


def detalle_plan_view(request, plan_id):
    """
    Redirige al admin directamente.
    """
    url_admin = reverse("admin:planes_mantenimiento_planmantenimiento_changelist")
    return redirect(url_admin)

