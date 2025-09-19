from django.contrib import admin
from .models import Activo, Infraestructura

@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'modelo', 'codigo_interno', 'estado_sistema', 'cantidad')
    search_fields = ('nombre', 'codigo_interno', 'categoria', 'modelo')
    list_filter = ('estado_sistema', 'categoria')

@admin.register(Infraestructura)
class InfraestructuraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_interno', 'encargado', 'ubicacion')
    search_fields = ('nombre', 'codigo_interno', 'encargado', 'ubicacion')
    list_filter = ('encargado',)