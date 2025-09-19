from django.contrib import admin
from .models import Planificacion

class PlanificacionAdmin(admin.ModelAdmin):
    list_display = (
        'descripcion',
        'cantidad_personas',
        'especialidad_display',
        'horas_estimadas',
        'equipo_funcionando',
        'herramientas_necesarias_display',  # Método para mostrar herramientas
        'documentos_necesarios_display',    # Método para mostrar documentos
        'proveedores_display',              # Método para mostrar proveedores
        'horarios_actividad',
        'notas',
    )
    
    # Mostrar las especialidades necesarias como lista separada por comas
    def especialidad_display(self, obj):
        return ", ".join([str(especialidad) for especialidad in obj.especialidad.all()])
    especialidad_display.short_description = 'Especialidades necesarias'
    
    # Mostrar herramientas necesarias como lista separada por comas
    def herramientas_necesarias_display(self, obj):
        return ", ".join([str(herramienta) for herramienta in obj.herramientas_necesarias.all()])
    herramientas_necesarias_display.short_description = 'Herramientas Necesarias'
    
    # Mostrar documentos necesarios como lista separada por comas
    def documentos_necesarios_display(self, obj):
        return ", ".join([str(doc) for doc in obj.documentos_necesarios.all()])
    documentos_necesarios_display.short_description = 'Documentos Necesarios'
    
    # Mostrar proveedores como lista separada por comas
    def proveedores_display(self, obj):
        return ", ".join([str(proveedor) for proveedor in obj.proveedores.all()])
    proveedores_display.short_description = 'Proveedores'
    
    # Mostrar el estado del equipo
    def equipo_funcionando(self, obj):
        return obj.get_equipo_funcionando_display()
    equipo_funcionando.short_description = 'Equipo Funcionando'
    
    # Horarios para la realización de los mantenimientos
    def horarios_actividad(self, obj):
        return obj.get_horarios_actividad_display()
    horarios_actividad.short_description = 'Horarios Actividad'

    search_fields = ['servicio__nombre', 'especialidad__nombre']  # Buscar por nombre de servicio o especialidad
    list_filter = ('equipo_funcionando', 'especialidad')  # Filtros por equipo o especialidad
    
    #readonly_fields = ('horarios_actividad',)  # Solo lectura para horarios de actividad si lo deseas

admin.site.register(Planificacion, PlanificacionAdmin)
