from django.contrib import admin
from .models import Empleado, DetalleCompetenciaUsuario

class DetalleCompetenciaUsuarioInline(admin.StackedInline): 
    model = DetalleCompetenciaUsuario
    extra = 1

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo', 'fecha_ingreso', 'sueldo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'cargo')
    list_filter = ('cargo', 'fecha_ingreso')
    inlines = [DetalleCompetenciaUsuarioInline]


