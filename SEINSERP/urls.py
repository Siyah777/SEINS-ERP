"""
URL configuration for plataformaSEINS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from usuarios.views import CustomAdminLoginView 
#from comunicacion.admin import admin_site
from . import views

admin.site.site_header = "Panel de administración Plataforma SEINS"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Bienvenido al Panel de Administración de SEINS"



urlpatterns = [
    path("admin/login/", CustomAdminLoginView.as_view(), name="admin_login"),
    path('admin/', admin.site.urls),
    #path('admin/', admin_site.urls),
    path('', views.react_app, name='react_app'),  # Página principal con React
    path('', include('comunicacion.urls')), 
    path('', include('notificaciones.urls')), 
    path('cotizaciones/', include('cotizaciones.urls')),
    path('actividades/', include('actividades.urls', namespace='actividades')),
    path('facturacion/', include('facturacion.urls', namespace='facturacion')),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),

]

