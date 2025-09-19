from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('correlativo', 'categoria', 'marca', 'serie', 'modelo', 'existencia', 'precio_unitario')
    list_per_page = 20
    search_fields = ('categoria', 'marca', 'modelo', 'serie')
    list_filter = ('categoria', 'marca')
    readonly_fields = ('correlativo',)
