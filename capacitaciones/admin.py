from django.contrib import admin
from .models import Curso, Empleado, Inscripcion, Certificado

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'proveedor', 'modalidad')
    list_filter = ('modalidad', 'fecha_inicio')
    search_fields = ('nombre', 'proveedor')

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'puesto', 'email')
    search_fields = ('nombre_completo', 'puesto')

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'curso', 'fecha_inscripcion', 'aprobado', 'calificacion')
    list_filter = ('aprobado',)
    search_fields = ('empleado__nombre_completo', 'curso__nombre')

@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'fecha_emision')
    search_fields = ('inscripcion__empleado__nombre_completo', 'inscripcion__curso__nombre')
