from django.urls import path
from django.urls import include
from . import views



urlpatterns = [
    path('inventario/<int:inventario_id>/pdf/', views.inventario_pdf, name='inventario_pdf'),
]
