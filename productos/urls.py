from django.urls import path
from django.urls import include
from . import views



urlpatterns = [
    path('producto/<int:id_producto>/pdf/', views.producto_pdf, name='producto_pdf'),
]