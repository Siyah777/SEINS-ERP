from django.urls import path
from django.urls import include
from . import views



urlpatterns = [
    path('equipo/<int:equipo_id>/pdf/', views.equipo_pdf, name='equipo_pdf'),
    path('herramienta/<int:herramienta_id>/pdf/', views.herramienta_pdf, name='herramienta_pdf'),
]