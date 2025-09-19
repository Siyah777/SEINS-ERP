from django.contrib.admin import AdminSite
from django.contrib import admin
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from notificaciones.models import Notificacion
from notificaciones.admin import NotificacionAdmin

class CustomAdminSite(AdminSite):
    site_header = _("Panel de administración SEINS-ERP")
    site_title = _("Admin SEINS")
    index_title = _("Bienvenido al panel de administración SEINS-ERP")

    def each_context(self, request):
        context = super().each_context(request)
        # Conteo de notificaciones no leídas por usuario
        if request.user.is_authenticated:
            context['notificaciones_pendientes'] = Notificacion.objects.filter(
                leido=False,
                usuario_destino=request.user
            ).count()
        else:
            context['notificaciones_pendientes'] = 0
        return context

# Crear la instancia de admin personalizada
admin_site = CustomAdminSite(name='custom_admin')

# Registrar Notificacion con su Admin personalizado
admin_site.register(Notificacion, NotificacionAdmin)

# Función para registrar automáticamente todos los demás modelos
def register_models():
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            try:
                admin_site.register(model)
            except admin.sites.AlreadyRegistered:
                pass

register_models()


