from django.contrib import admin
from .models import Documentacion

@admin.register(Documentacion)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'version', 'categoria', 'fecha_actualizacion', 'documento')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'fecha_actualizacion')
