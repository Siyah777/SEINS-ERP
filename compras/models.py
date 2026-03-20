from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from proveedores.models import Proveedor
from core.fields import RichTextMediumField
from productos.models import Producto
from servicios.models import Servicio
import logging

logger = logging.getLogger(__name__)

class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    factura_compra = models.CharField(max_length=50, blank=True, null=True)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descripcion_general = RichTextMediumField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    costo_total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fecha_compra = models.DateField()
    fecha_aprobacion = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
    
    def calcular_total(self):
        total_productos = sum(
            (item.subtotal for item in self.detalles_productos.all()),
            Decimal('0.00')
        )
        total_servicios = sum(
            (item.subtotal for item in self.detalles_servicios.all()),
            Decimal('0.00')
        )

        total = total_productos + total_servicios

        total_redondeado = total.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        total_iva = (total_redondeado * Decimal('1.13')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        self.costo_total = total_redondeado
        self.costo_total_iva = total_iva

        # ⚠️ update evita recursión
        Compra.objects.filter(pk=self.pk).update(
            costo_total=total_redondeado,
            costo_total_iva=total_iva
        )

        logger.debug(
            f"[Compra {self.pk}] Total: {total_redondeado}, IVA: {total_iva}"
        )
    
    def save(self, *args, **kwargs):
        if not self.correlativo:
            ultimo = Compra.objects.order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass
            self.correlativo = f"COM-{numero:06d}"  # COM-000001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra a {self.proveedor.nombre_empresa} - {self.descripcion_general[:30]}"

class DetalleProductos(models.Model):
    compra = models.ForeignKey(Compra, related_name="detalles_productos", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.PositiveIntegerField(default=1)
    descripcion_producto = RichTextMediumField(blank=True)
    cliente = models.ManyToManyField('clientes.Cliente', blank=True)  # Cliente al que se le realiza la compra
    equipo = models.ManyToManyField('equipos.Equipo', blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    unidades_cantidad = models.CharField(max_length=50, default='Unidad')  # Unidades de la cantidad
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        verbose_name = "Compra de Producto"
        verbose_name_plural = "Compras de Productos"

    def save(self, *args, **kwargs):
        if self.producto:
            self.precio_unitario = self.producto.precio_unitario
            self.subtotal = (Decimal(self.cantidad) * self.precio_unitario).quantize(Decimal('0.01'))
        else:
            self.precio_unitario = Decimal('0.00')
            self.subtotal = Decimal('0.00')

        super().save(*args, **kwargs)
        self.compra.calcular_total()
        
    def __str__(self):
        return f"Compra #{self.compra.correlativo}"

class DetalleServicios(models.Model):
    compra = models.ForeignKey(Compra, related_name="detalles_servicios", on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.PositiveIntegerField(default=1)
    descripcion_servicio =RichTextMediumField(blank=True)
    cliente = models.ManyToManyField('clientes.Cliente', blank=True)  # Cliente al que se le realiza la compra
    equipo = models.ManyToManyField('equipos.Equipo', blank=True)
    unidades_cantidad = models.CharField(max_length=50, default='Unidad')  # Unidades de la cantidad
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        verbose_name = "Compra de Servicio"
        verbose_name_plural = "Compras de Servicios"

    def save(self, *args, **kwargs):
        if self.servicio:
            self.precio_unitario = self.servicio.precio_unitario
            self.subtotal = (Decimal(self.cantidad) * self.precio_unitario).quantize(Decimal('0.01'))
        else:
            self.precio_unitario = Decimal('0.00')
            self.subtotal = Decimal('0.00')

        super().save(*args, **kwargs)
        self.compra.calcular_total()

    def __str__(self):
        return f"Compra #{self.compra.correlativo}"