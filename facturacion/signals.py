# signals.py
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Contingencia

@receiver(m2m_changed, sender=Contingencia.facturas_contingencia.through)
def facturas_contingencia_changed(sender, instance, action, **kwargs):
    # Solo cuando se agregan facturas
    if action == "post_add":
        instance.procesar_envio_hacienda()
