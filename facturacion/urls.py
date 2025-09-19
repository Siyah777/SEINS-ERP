from django.urls import path
from facturacion.views.views_factura import (prueba_firma_dte,
firmar_factura_admin, 
descargar_factura_pdf, 
DescargarJSONView)

app_name = 'facturacion'

urlpatterns = [
    path('factura/<int:factura_id>/pdf/', descargar_factura_pdf, name='descargar_factura_pdf'),
    path('prueba-firma/<int:factura_id>/', prueba_firma_dte, name='prueba_firma_dte'),
    path('firmar-factura/<int:factura_id>/', firmar_factura_admin, name='firmar_factura'),
    path('factura/<int:pk>/descargar-json/', DescargarJSONView.as_view(), name='descargar_factura_json'),
]