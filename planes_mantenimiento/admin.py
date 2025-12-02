from django.contrib import admin
from .models import PlanMantenimiento, DetallePlanMantenimiento

class DetallePlanMantenimientoInline(admin.StackedInline):
    model = DetallePlanMantenimiento
    extra = 1

@admin.register(PlanMantenimiento)
class PlanMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'codigo_plan', 'descripcion')
    search_fields = ('equipo__nombre', 'codigo_plan')
    inlines = [DetallePlanMantenimientoInline]

@admin.register(DetallePlanMantenimiento)
class DetallePlanMantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        'plan', 'actividad', 'frecuencia', 'especialidad', 'proveedores', 'herramientas', 'cantidad_personas')
    list_filter = ('frecuencia', 'especialidad', 'proveedores')
    search_fields = ('plan__equipo__nombre', 'actividad', 'especialista')
   
