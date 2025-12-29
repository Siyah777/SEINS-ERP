from django.urls import path
from .views import documentacion_pdf

urlpatterns = [
    path(
        'documentacion/<int:documentacion_id>/pdf/',
        documentacion_pdf,
        name='documentacion_pdf'
    ),
]
