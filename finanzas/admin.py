from django.contrib import admin
from .models import Presupuesto, Ingreso, Gasto, CuentaPorCobrar, CuentaPorPagar

class IngresoInline(admin.TabularInline):
    model = Ingreso
    extra = 1

class GastoInline(admin.TabularInline):
    model = Gasto
    extra = 1

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'total_ingresos', 'total_gastos', 'balance_total')
    inlines = [IngresoInline, GastoInline]

@admin.register(CuentaPorCobrar)
class CuentaPorCobrarAdmin(admin.ModelAdmin):
    list_display = ('factura', 'monto', 'fecha_creacion', 'fecha_caducidad', 'estatus')
    list_filter = ('estatus', 'fecha_caducidad')
    search_fields = ('factura__id',)
    date_hierarchy = 'fecha_creacion'

@admin.register(CuentaPorPagar)
class CuentaPorPagarAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'monto', 'fecha_creacion', 'fecha_vencimiento', 'estatus')
    list_filter = ('estatus', 'fecha_vencimiento')
    search_fields = ('proveedor__nombre',)
    date_hierarchy = 'fecha_creacion'
    
#admin.site.register(Ingreso)
#admin.site.register(Gasto)
