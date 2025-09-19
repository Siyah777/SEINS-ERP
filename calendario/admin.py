from django.contrib import admin
from .models import Actividade

class ActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'usuario', 'creado_en')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_inicio', 'fecha_fin')

admin.site.register(Actividade, ActividadAdmin)

