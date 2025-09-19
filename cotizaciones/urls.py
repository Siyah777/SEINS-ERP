from django.urls import path
from django.urls import include
from . import views



urlpatterns = [
    path('cotizacion/<int:cotizacion_id>/pdf/', views.cotizacion_pdf, name='cotizacion_pdf'),
]
