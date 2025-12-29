from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('correlativo', 'nombre', 'proveedor', 'mostrar_equipo', 'marca', 'serie', 'modelo', 'existencia', 'precio_unitario')
    list_per_page = 20
    search_fields = ('categoria', 'marca', 'modelo', 'serie')
    list_filter = ('categoria', 'marca', ("equipo", admin.RelatedOnlyFieldListFilter), 'proveedor')
    readonly_fields = ('correlativo',)
    
    def mostrar_equipo(self, obj):
        return ", ".join([str(c) for c in obj.equipo.all()])
    mostrar_equipo.short_description = "equipo"
