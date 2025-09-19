from django.contrib import admin
from .models import Proveedor

# Registrar el modelo Proveedor en el admin
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
            'correlativo',
            'nombre_empresa',
            'descripcion',
            'nombre_contacto',
             )
    readonly_fields = ('correlativo',)