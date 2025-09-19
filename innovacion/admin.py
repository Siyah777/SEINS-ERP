from django.contrib import admin
from .models import Innovacion

@admin.register(Innovacion)
class InnovacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'fecha_inicio', 'fecha_fin', 'responsable')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'descripcion', 'responsable')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ['fecha_inicio']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct
