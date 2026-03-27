from django.urls import path
from .views import pdf_presupuesto

urlpatterns = [
    path('presupuesto/<int:pk>/pdf/', pdf_presupuesto, name='pdf_presupuesto'),
]