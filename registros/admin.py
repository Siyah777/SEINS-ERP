from django.contrib import admin
from .models import Atestado, DescripcionesPuesto

@admin.register(Atestado)
class AtestadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion', 'enlace_archivo')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_creacion',)

@admin.register(DescripcionesPuesto)
class DescripcionesPuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre_puesto', 'salario_base', 'pago_adicional', 'jefe_inmediato')
    search_fields = ('nombre_puesto', 'jefe_inmediato', 'competencias_requeridas')
    list_filter = ('jefe_inmediato',)

