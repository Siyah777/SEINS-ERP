from django.urls import path
from django.urls import include
from . import views



urlpatterns = [
    path('compra/<int:compra_id>/pdf/', views.compra_pdf, name='compra_pdf'),
]