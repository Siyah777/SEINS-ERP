from django.urls import path
from . import views
from .views import resumen_plan_pdf

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
    
    path('resumen_pdf/<int:plan_id>/', resumen_plan_pdf, name='resumen_plan_pdf'),
]
