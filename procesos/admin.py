from django.contrib import admin
from .models import Proceso

@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_del_proceso',
        'formula_proceso',
        'resultado', 'unidades_resultado',
        
    )
    readonly_fields = ['resultado']
    search_fields = ['nombre_del_proceso']
    
    def save_model(self, request, obj, form, change):
        obj.resultado = obj.calcular_resultado()  # fuerza el cálculo del resultado
        super().save_model(request, obj, form, change)
