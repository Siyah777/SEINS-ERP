from django.apps import AppConfig


class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'facturacion'

    def ready(self):
        import facturacion.admin  # para asegurarse que se registren modelos
        import facturacion.signals
