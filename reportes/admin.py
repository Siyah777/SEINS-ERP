from django.contrib import admin
from .models import Reporte

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = (
        'cliente', 'categoria', 'descripcion', 'cantidad', 
        'usuario', 'fecha_inicio', 'fecha_finalizacion', 'enlace_documento'
    )
    search_fields = ('cliente__nombre', 'categoria', 'usuario__username')
    list_filter = ('categoria', 'fecha_inicio', 'fecha_finalizacion')
    date_hierarchy = 'fecha_inicio'
    
