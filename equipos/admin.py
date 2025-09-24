from django.contrib import admin
from .models import Equipo, HistorialMantenimiento
from django.db.models import Sum
from django.utils.html import format_html
from .models import Herramienta

class HistorialMantenimientoInline(admin.StackedInline): #admin.TabularInline admin.StackedInline
    model = HistorialMantenimiento
    extra = 1

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    inlines = [HistorialMantenimientoInline]
    readonly_fields = ('mostrar_costo_total_acumulado',)
    
    def mostrar_costo_total_acumulado(self, obj):
        resultado =  obj.calcular_costo_total_mantenimientos()
        return f"${resultado:,.2f}" if resultado is not None else "$0.00"
    
    mostrar_costo_total_acumulado.short_description = "Costo Total Acumulado"
    
@admin.register(HistorialMantenimiento)
class HistorialMantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        'fecha_mant',
        'descripcion_mant',
        'mot_mant',
        'repuestos',
        'proveedor_repuestos',
        'proveedor_mantenimiento',
        'costo_mano_obra',
        'costo_repuestos',
        'costo_total',
        'indicacion_odometro',
        'unidad_odometro',
        'tiempo_falla',
        'tiempo_reparacion',
        'proximo_mant',
        'notas',
        'usuario_asignado',)
    list_filter = ('fecha_mant', 'descripcion_mant', 'proximo_mant',)
    search_fields = ('descripcion_mant',)
    
    def changelist_view(self, request, extra_context=None):
        total_costo = HistorialMantenimiento.objects.aggregate(total=Sum('costo_total'))['total'] or 0
        extra_context = extra_context or {}
        extra_context['title'] = f"Historial de Mantenimientos (Costo Total: ${total_costo:,.2f})"
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('codigo_interno', 'nombre', 'categoria', 'cantidad', 'modelo', 'marca', 'estado')
    list_filter = ('estado', 'categoria', 'marca')
    search_fields = ('nombre', 'modelo', 'serie', 'marca')