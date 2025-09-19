from django.contrib import admin
from .models import AsientoContable, DetalleAsiento, DeclaracionFiscal, CreditoFiscal, Tributo

class DetalleAsientoInline(admin.TabularInline):
    model = DetalleAsiento
    extra = 1

@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'descripcion', 'creado_por')
    inlines = [DetalleAsientoInline]

@admin.register(DeclaracionFiscal)
class DeclaracionFiscalAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'fecha_presentacion', 'monto')

@admin.register(CreditoFiscal)
class CreditoFiscalAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'monto', 'fecha', 'relacionado_con')

@admin.register(Tributo)
class TributoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'monto', 'fecha_pago', 'relacionado_con')
