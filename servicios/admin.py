from django.contrib import admin
from .models import Servicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('correlativo', 'nombre', 'especialidad', 'precio_unitario')
    list_per_page = 20
    search_fields = ('nombre', 'especialidad')
    list_filter = ('nombre',)
    readonly_fields = ('correlativo',)
