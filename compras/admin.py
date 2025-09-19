from django.contrib import admin
from .models import Compra

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('correlativo', 'proveedor', 'descripcion', 'cantidad', 'costo_total', 'fecha_ingreso', 'fecha_aprobacion')
    search_fields = ('proveedor__nombre', 'descripcion')
    list_filter = ('fecha_ingreso', 'fecha_aprobacion', 'proveedor')
    date_hierarchy = 'fecha_ingreso'
    readonly_fields = ('correlativo',)
