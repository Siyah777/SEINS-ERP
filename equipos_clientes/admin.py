from django.contrib import admin
from .models import EquipoCliente, HistorialMantenimiento

class HistorialMantenimientoInline(admin.StackedInline):
    model = HistorialMantenimiento
    extra = 1

@admin.register(EquipoCliente)
class EquipoClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    inlines = [HistorialMantenimientoInline]

@admin.register(HistorialMantenimiento)
class HistorialMantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        'fecha_mant',
        #'descripcion_mant',
        #'mot_mant',
        #'repuestos',
        #'orden_trabajo',
        #'tiempo_falla',
        #'tiempo_reparacion',
        'proximo_mant',
        'notas',
        'usuario_asignado')
    filter_horizontal = ('ordenes_trabajo',)
    list_filter = ('fecha_mant',) #'descripcion_mant', 'proximo_mant',)
    search_fields = ('fecha_mant',)