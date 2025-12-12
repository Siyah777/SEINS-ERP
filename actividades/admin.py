from django.contrib import admin
from .models import Ordendetrabajo
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import DateFieldListFilter

@admin.register(Ordendetrabajo)
class TrabajoAdmin(admin.ModelAdmin):
    list_display = (
        'correlativo',
        'cliente',
        'mostrar_equipo',
        'descripcion',
        'mostrar_personal_asignado',
        'horarios_actividad',
        'fecha_inicio',
        'hora_inicio',
        'fecha_fin',
        'hora_fin',
        'estatus_coloreado',
        'prioridad_coloreado',
        'mostrar_proveedores',
        'pdf_orden_trabajo',
        )
    
    class Media:
        js = ('js/firma.js',)
        
    list_per_page = 20
    
    readonly_fields = ('cliente',
        'correlativo',
        'descripcion',
        'equipo',
        'detalleplan',
        ) # Campos de solo lectura
    
    def estatus_coloreado(self, obj):
        colores = {
            'en_proceso': 'orange',
            'programado': 'blue',
            'terminado': 'green',
            'pendiente': 'red',
        }
        color = colores.get(obj.estatus, 'black')
        return format_html(f'<strong style="color: {color};">{obj.get_estatus_display()}</strong>')
    
    def prioridad_coloreado(self, obj):
        colores = {
            'baja': 'green',
            'media': 'yellow',
            'alta': 'orange',
            'critica': 'red',
        }
        color = colores.get(obj.prioridad, 'black')
        return format_html(f'<strong style="color: {color};">{obj.get_prioridad_display()}</strong>')
    
    def mostrar_herramientas_necesarias(self, obj):
        return ", ".join([h.nombre for h in obj.herramientas_necesarias.all()])
    mostrar_herramientas_necesarias.short_description = "Herramientas"
    
    def mostrar_productos_necesarios(self, obj):
        return ", ".join([h.nombre for h in obj.productos_necesarios.all()])
    mostrar_productos_necesarios.short_description = "Productos"

    def mostrar_proveedores(self, obj):
        return ", ".join([p.nombre_empresa for p in obj.proveedores.all()])
    mostrar_proveedores.short_description = "Proveedores"

    def mostrar_documentos_necesarios(self, obj):
        return ", ".join([d.nombre for d in obj.documentos_necesarios.all()])
    mostrar_documentos_necesarios.short_description = "Documentos"
    
    def mostrar_personal_asignado(self, obj):
        return ", ".join([str(c) for c in obj.personal_asignado.all()])
    mostrar_personal_asignado.short_description = "personal asignado"
    
    def mostrar_equipo(self, obj):
        return ", ".join([str(c) for c in obj.equipo.all()])
    mostrar_equipo.short_description = "equipo"

    def pdf_orden_trabajo(self, obj):
        url = reverse('actividades:generar_pdf_orden_trabajo', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Descargar O.T.</a>', url)
    pdf_orden_trabajo.short_description = 'PDF'
    
    def resumen_actividades(self, request):
        actividades = Ordendetrabajo.objects.all()
        resumen_actividades = {
            'pendientes': actividades.filter(estado='pendiente').count(),
            'en_proceso': actividades.filter(estado='en_proceso').count(),
            'completadas': actividades.filter(estado='completada').count(),
        }
        context = {
            'resumen_actividades': resumen_actividades,
            'actividades': actividades,
        }
        return 

    
    list_filter = ('estatus',
    ('fecha_inicio', DateFieldListFilter),
    'fecha_fin',
    ("personal_asignado", admin.RelatedOnlyFieldListFilter),
    ("proveedores", admin.RelatedOnlyFieldListFilter),
    ("equipo", admin.RelatedOnlyFieldListFilter),
    'horarios_actividad',
    'cliente',
    'prioridad',
    )
    search_fields = ('correlativo',) 
    filter_horizontal = ('personal_asignado',)  # Para seleccionar múltiples usuarios con un widget más cómodo
    date_hierarchy = 'fecha_inicio'
