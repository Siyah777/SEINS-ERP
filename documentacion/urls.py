from django.urls import path
from .views import procedimiento_pdf

urlpatterns = [
    path(
        'procedimiento/<int:procedimiento_id>/pdf/',
        procedimiento_pdf,
        name='procedimiento_pdf'
    ),
]
