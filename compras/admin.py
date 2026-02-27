from django.contrib import admin
from .models import Compra, DetalleProductos, DetalleServicios
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse   
from .models import Compra
from django.urls import path
from django.shortcuts import redirect
from .views import resumen_compras_pdf

class DetalleProductosInline(admin.StackedInline):
    model = DetalleProductos
    extra = 1

class DetalleServiciosInline(admin.StackedInline):
    model = DetalleServicios
    extra = 1
    
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('correlativo', 'proveedor', 'descripcion_general', 'costo_total_iva', 'fecha_compra', 'compra_pdf')
    list_per_page = 20
    actions = ["descargar_pdf_compras"]
    search_fields = ('proveedor__nombre', 'descripcion')
    list_filter = ('fecha_compra', 'factura_compra', 'proveedor')
    date_hierarchy = 'fecha_compra'
    readonly_fields = ('correlativo', 'costo_total', 'costo_total_iva')
    
    def compra_pdf(self, obj):
        url = reverse('compra_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Hoja de compra</a>', url)

    compra_pdf.short_description = 'PDF'
    
    inlines = [DetalleProductosInline, DetalleServiciosInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pdf/', self.admin_site.admin_view(resumen_compras_pdf), name="compras-pdf"),
        ]
        return custom_urls + urls

    def descargar_pdf_compras(self, request, queryset):
        ids = "&".join([f"ids={c.id}" for c in queryset])
        return redirect(f"{request.path}pdf/?{ids}")
    descargar_pdf_compras.short_description = "Descargar PDF resumen de compras seleccionadas"

