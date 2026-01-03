from django.contrib import admin
from .models import Producto
from django.utils.html import format_html
from django.urls import reverse 

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('correlativo', 'nombre', 'proveedor', 'mostrar_equipo', 'marca', 'serie', 'modelo', 'existencia', 'precio_unitario', 'producto_pdf')
    list_per_page = 20
    search_fields = ('categoria', 'marca', 'modelo', 'serie')
    list_filter = ('categoria', 'marca', ("equipo", admin.RelatedOnlyFieldListFilter), 'proveedor', )
    readonly_fields = ('correlativo',)
    
    def mostrar_equipo(self, obj):
        return ", ".join([str(c) for c in obj.equipo.all()])
    mostrar_equipo.short_description = "equipo"
    
    def producto_pdf(self, obj):
        url = reverse('producto_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">ficha del producto</a>', url)

    producto_pdf.short_description = 'PDF'

