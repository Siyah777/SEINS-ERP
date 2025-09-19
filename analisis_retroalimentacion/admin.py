from django.contrib import admin
from .models import Analisis, Retroalimentacion, PlanAccion

class AnalisisAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descripcion', 'fecha_creacion', 'fecha_analisis', 'resultado')
    search_fields = ('tipo', 'descripcion')
    list_filter = ('tipo',)

class RetroalimentacionAdmin(admin.ModelAdmin):
    list_display = ('analisis', 'comentario', 'estado', 'fecha_retroalimentacion')
    list_filter = ('estado',)
    search_fields = ('comentario',)

class PlanAccionAdmin(admin.ModelAdmin):
    list_display = ('retroalimentacion', 'descripcion_accion', 'estado', 'fecha_inicio', 'fecha_limite')
    list_filter = ('estado',)
    search_fields = ('descripcion_accion',)

admin.site.register(Analisis, AnalisisAdmin)
admin.site.register(Retroalimentacion, RetroalimentacionAdmin)
admin.site.register(PlanAccion, PlanAccionAdmin)
