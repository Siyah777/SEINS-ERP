from django.urls import path
from . import views
from notificaciones.views import notificaciones_admin

urlpatterns = [
    
    path("admin/notificaciones/", notificaciones_admin, name="notificaciones"),
    

]




