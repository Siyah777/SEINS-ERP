from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetalleCotizacionProductos, DetalleCotizacionServicios
from .models import Cotizacion 

# Señal para productos
@receiver([post_save, post_delete], sender=DetalleCotizacionProductos)
def actualizar_total_cotizacion_productos(sender, instance, **kwargs):
    if instance.cotizacion:
        instance.cotizacion.calcular_total()

# Señal para servicios
@receiver([post_save, post_delete], sender=DetalleCotizacionServicios)
def actualizar_total_cotizacion_servicios(sender, instance, **kwargs):
   if instance.cotizacion:
        instance.cotizacion.calcular_total()

# Señal para cotizaciones
@receiver(post_save, sender=Cotizacion)
def recalcular_total_al_guardar_cotizacion(sender, instance, **kwargs):
    instance.calcular_total()
