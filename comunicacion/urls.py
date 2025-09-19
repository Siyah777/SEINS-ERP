from django.urls import path
from . import views

urlpatterns = [
    
    path('api/enviar-mensaje/', views.enviar_mensaje_api, name='enviar_mensaje_api'),
    

]
