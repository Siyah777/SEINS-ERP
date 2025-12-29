from django.contrib import admin
from .models import Documentacion, PasoProcedimiento, ActividadFinal

class PasoProcedimientoInline(admin.TabularInline):
    model = PasoProcedimiento
    extra = 1
    ordering = ['orden']

class ActividadFinalInline(admin.TabularInline):
    model = ActividadFinal
    extra = 1

@admin.register(Documentacion)
class ProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('codigo_documento', 'titulo', 'categoria', 'descripcion', 'mostrar_equipo')
    search_fields = ('codigo_documento', 'titulo')
    list_filter = ('categoria', 'activo')
    inlines = [PasoProcedimientoInline, ActividadFinalInline]
    
    def mostrar_equipo(self, obj):
        return ", ".join([str(c) for c in obj.equipo.all()])
    mostrar_equipo.short_description = "equipo"
