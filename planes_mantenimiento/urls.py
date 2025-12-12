from django.urls import path
from . import views

app_name = 'planes_mantenimiento'  # IMPORTANTE para namespacing

urlpatterns = [
    path(
        'generar-ots/<int:plan_id>/',
        views.generar_ots_view,
        name='generar_ots'
    ),

    path(
        'detalle/<int:plan_id>/',
        views.detalle_plan_view,
        name='detalle_plan'
    ),
]
