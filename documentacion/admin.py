from django.contrib import admin
from .models import Documentacion, PasoProcedimiento, ActividadFinal
from django.utils.html import format_html
from django.urls import reverse 

class PasoProcedimientoInline(admin.StackedInline):
    model = PasoProcedimiento
    extra = 1
    ordering = ['orden']

class ActividadFinalInline(admin.StackedInline):
    model = ActividadFinal
    extra = 1

@admin.register(Documentacion)
class ProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('codigo_documento', 'titulo', 'categoria', 'descripcion', 'mostrar_equipos', 'documentacion_pdf')
    search_fields = ('codigo_documento', 'titulo')
    list_filter = ('categoria', 'activo')
    inlines = [PasoProcedimientoInline, ActividadFinalInline]
    
    def mostrar_equipos(self, obj):
        return ", ".join([str(c) for c in obj.equipos.all()])
    mostrar_equipos.short_description = "equipos"
    
    def documentacion_pdf(self, obj):
        url = reverse('documentacion_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Documento en PDF</a>', url)

    documentacion_pdf.short_description = 'PDF'
    
   
