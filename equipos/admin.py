from django.contrib import admin
from .models import Equipo, HistorialTrabajos, Herramienta
from django.db.models import Sum
from django.utils.html import format_html
from django.urls import reverse 

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('codigo_interno', 'cliente', 'nombre', 'descripcion', 'ubicacion', 'categoria', 'equipo_pdf')
    search_fields = ('codigo_interno', 'cliente', 'nombre', 'categoria')
    list_filter = ('codigo_interno', 'cliente', 'nombre', 'categoria')
    
    def equipo_pdf(self, obj):
        url = reverse('equipo_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Hoja de equipo</a>', url)

    equipo_pdf.short_description = 'PDF'
    
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
    list_display = ('codigo_interno', 'nombre', 'categoria', 'cantidad', 'modelo', 'marca', 'estado', 'herramienta_pdf')
    list_filter = ('estado', 'categoria', 'marca')
    search_fields = ('nombre', 'modelo', 'serie', 'marca')
    list_per_page = 20
    
    def herramienta_pdf(self, obj):
        url = reverse('herramienta_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Hoja de herramienta</a>', url)

    herramienta_pdf.short_description = 'PDF'