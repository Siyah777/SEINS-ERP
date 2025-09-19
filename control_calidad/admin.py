from django.contrib import admin
from .models import Proceso, Auditoria, NoConformidad, AccionCorrectiva

@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('proceso', 'fecha', 'responsable')
    list_filter = ('fecha', 'proceso')
    search_fields = ('responsable',)

@admin.register(NoConformidad)
class NoConformidadAdmin(admin.ModelAdmin):
    list_display = ('auditoria', 'gravedad', 'estatus', 'fecha_detectada')
    list_filter = ('gravedad', 'estatus')
    search_fields = ('descripcion',)

@admin.register(AccionCorrectiva)
class AccionCorrectivaAdmin(admin.ModelAdmin):
    list_display = ('no_conformidad', 'responsable', 'fecha_compromiso', 'fecha_cierre')
    list_filter = ('fecha_compromiso', 'fecha_cierre')
    search_fields = ('descripcion', 'responsable')
