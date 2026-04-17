from django.urls import path
from .views import dashboard, dashboard_data, exportar_pdf
from . import views

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('api/', dashboard_data, name='dashboard_api'),
    path('pdf/', views.exportar_pdf, name='indicadores_pdf'),
]
