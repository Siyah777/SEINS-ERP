from django.contrib import admin
from .models import Cliente, Seguimiento
from .forms import ClienteForm

class SeguimientoInline(admin.StackedInline):  
    model = Seguimiento
    extra = 0  # No mostrar formularios vacíos adicionales
    fields = ('fecha_contacto', 'medio_contacto', 'asunto', 'cotizaciones', 'estado_cotizacion', 'responsable')
    readonly_fields = ('fecha_contacto',)  # Opcional: hacer campos de solo lectura

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('correlativo', 'nombre_empresa', 'correo', 'telefono_contacto', 'nombre_contacto', 'sub_area', 'municipio', 'departamento')
    list_per_page = 20
    search_fields = ('nombre_empresa', 'nombre_contacto')
    readonly_fields = ('correlativo', 'actividad_codigo', 'actividad_descripcion')
    inlines = [SeguimientoInline]
    form = ClienteForm
