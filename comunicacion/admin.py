from django.contrib import admin
from .models import Comunicacion, MensajeContacto
from django.template.response import TemplateResponse


@admin.register(Comunicacion)
class ComunicacionAdmin(admin.ModelAdmin):
    list_display = ('usuario_destino', 'usuario_remitente', 'mensaje', 'fecha_inicio')
    list_filter = ('fecha_inicio',)
    search_fields = ('usuario_destino',)
    exclude = ('usuario_remitente',)  # Ocultar campo en el admin

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Solo al crear (no modificar)
            obj.usuario_remitente = request.user
        super().save_model(request, obj, form, change)
        
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si ya existe (estamos editando)
            return [f.name for f in self.model._meta.fields if f.name != 'mensaje']
        return []


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'fecha')
    search_fields = ('nombre', 'correo', 'mensaje')
    readonly_fields = ('nombre', 'correo', 'mensaje', 'fecha')
        
