from django.contrib import admin
from .models import Equipo, HistorialTrabajos, Herramienta
from django.db.models import Sum
from django.utils.html import format_html

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('codigo_interno', 'nombre', 'descripcion', 'ubicacion', 'categoria')
    search_fields = ('codigo_interno', 'nombre', 'categoria')
    
@admin.register(HistorialTrabajos)
class HistorialTrabajos(admin.ModelAdmin):
    list_display = (
        'equipo',
        'mostrar_ordenes_trabajo',
        'fecha_registro',
        'notas',
        )
    
    def mostrar_ordenes_trabajo(self, obj):
        return ", ".join([h.correlativo for h in obj.ordenes_trabajo.all()])
    mostrar_ordenes_trabajo.short_description = "Trabajos Realizados"

@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('codigo_interno', 'nombre', 'categoria', 'cantidad', 'modelo', 'marca', 'estado')
    list_filter = ('estado', 'categoria', 'marca')
    search_fields = ('nombre', 'modelo', 'serie', 'marca')
    list_per_page = 20