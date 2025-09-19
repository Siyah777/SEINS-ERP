from django.contrib import admin
from .models import Ordendetrabajo
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Ordendetrabajo)
class TrabajoAdmin(admin.ModelAdmin):
    list_display = (
        'correlativo',
        'cliente',
        'fecha_inicio',
        'fecha_fin',
        'estatus',
        #'horas_hombre_estimadas',
        #'equipo_funcionando',
        #'mostrar_herramientas_necesarias',
        #'horarios_actividad',
        #'mostrar_documentos_necesarios',
        'mostrar_proveedores',
        'pdf_orden_trabajo',
        )
    
    list_per_page = 20
    
    readonly_fields = ('cliente', 'correlativo',) # Campos de solo lectura
    def mostrar_herramientas_necesarias(self, obj):
        return ", ".join([h.nombre for h in obj.herramientas_necesarias.all()])
    mostrar_herramientas_necesarias.short_description = "Herramientas"
    
    def mostrar_productos_necesarios(self, obj):
        return ", ".join([h.nombre for h in obj.productos_necesarios.all()])
    mostrar_productos_necesarios.short_description = "Productos"

    def mostrar_proveedores(self, obj):
        return ", ".join([p.nombre for p in obj.proveedores.all()])
    mostrar_proveedores.short_description = "Proveedores"

    def mostrar_documentos_necesarios(self, obj):
        return ", ".join([d.nombre for d in obj.documentos_necesarios.all()])
    mostrar_documentos_necesarios.short_description = "Documentos"

    def pdf_orden_trabajo(self, obj):
        url = reverse('actividades:generar_pdf_orden_trabajo', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Descargar O.T.</a>', url)
    pdf_orden_trabajo.short_description = 'PDF'
    
    list_filter = ('estatus', 'fecha_inicio', 'fecha_fin')
    #search_fields = ('cliente__nombre', 'correlativo') 
    filter_horizontal = ('personal_asignado',)  # Para seleccionar múltiples usuarios con un widget más cómodo
    date_hierarchy = 'fecha_inicio'
