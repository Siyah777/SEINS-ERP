from django.urls import path
from .views import generar_pdf_orden_trabajo

app_name = 'actividades'

urlpatterns = [
    path('actividades/pdf/<int:orden_id>/', generar_pdf_orden_trabajo, name='generar_pdf_orden_trabajo'),
]
