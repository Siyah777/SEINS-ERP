from django.contrib import admin
from .models import Notificacion
from django.utils.html import format_html

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mensaje', 'leido', 'mostrar_enlace')
    list_filter = ('leido',)
    search_fields = ('mensaje',)
    readonly_fields = ('nombre', 'mensaje','mostrar_enlace', 'modulo_enlace', 'usuario_destino')

    actions = ['marcar_como_leido']
    
    def marcar_como_leida(self, request, queryset):
        queryset.update(leido=True)
        self.message_user(request, "Las notificaciones seleccionadas han sido marcadas como leídas.")
    
    def mostrar_enlace(self, obj):
        if obj.modulo_enlace:
            return format_html('<a href="{}" target="_blank">ver detalle</a>', obj.modulo_enlace)
        return "-"
    
    def enlace_html(self, obj):
        if obj.modulo_enlace:
            return format_html('<a href="{}" target="_blank">ver detalle</a>', obj.modulo_enlace)
        return "-"
    enlace_html.short_description = "Enlace al módulo"
    
