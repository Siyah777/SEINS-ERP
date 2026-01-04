from django.db import models
from clientes.models import Cliente
from servicios.models import Servicio
from productos.models import Producto
from inventario.models import Inventario
from django.contrib.auth.models import User
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.db import transaction
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

class Cotizacion(models.Model):
    ESTATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('no_aprobada', 'No aprobada'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Cliente que solicita la cotización
    equipo = models.ManyToManyField('equipos.Equipo', blank=True) # Equipos relacionados con la cotización
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    Descripcion = models.TextField(blank=False, null=False, default='Descripcion de la cotización')  # Descripción de la cotización
    porcentaje_administracion = models.DecimalField(max_digits=5, decimal_places=0, default=0)  # Porcentaje de administración
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=0, default=0)  # Porcentaje de ganancia
    validez_oferta = models.PositiveIntegerField(default=15)  # Días de validez de la oferta
    unidades_oferta = models.CharField(max_length=50, default='dias')  # Unidades de la oferta
    condiciones_pago = models.CharField(
        max_length=20,
        choices=[
            ('Contado', 'Contado'),
            ('Credito', 'Crédito'),
            ('Otros', 'Otros')
        ],  default=None,
        verbose_name="Condición de Operación"
    )  # Condiciones de pago
    dias_credito = models.PositiveIntegerField(default=0, null=False, help_text="Días de crédito otorgado")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, null=True, blank=True)  # Usuario que la generó
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)  # Total de la cotización
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)  # Total con IVA
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='pendiente')
    
    class Meta:
        verbose_name = "Cotizacion"
        verbose_name_plural = "Cotizaciones"
    
    def calcular_total(self):
        total_productos = sum(item.subtotal for item in self.detalles_productos.all())  # Total de productos
        total_servicios = sum(item.subtotal for item in self.detalles_servicios.all())  # Total de servicios
        logger.debug(f"[Cotización #{self.id}] Productos: {total_productos}, Servicios: {total_servicios}")
        
        if not self.detalles_productos.exists() and not self.detalles_servicios.exists():
            self.total = Decimal('0.00')
            self.total_iva = Decimal('0.00')
            return self.total
        
        # Convertir porcentajes a Decimal para evitar errores de flotantes
        porcentaje_admin = Decimal(self.porcentaje_administracion) / Decimal('100')
        porcentaje_gan = Decimal(self.porcentaje_ganancia) / Decimal('100')
        
        # Cálculos base
        gastos_administracion = (total_productos + total_servicios) * (Decimal('1') + porcentaje_admin)
        gasto_total_unitario = gastos_administracion * (Decimal('1') + porcentaje_gan)
        
        # 🔁 Aumento automático por crédito
        dias_credito = self.dias_credito 
        if dias_credito >= 120:
            recargo_credito = Decimal('0.20')  # Recargo del 20% si es de 120 días
        elif dias_credito >= 90:
            recargo_credito = Decimal('0.15') # Recargo del 15% si es de 90 días
        elif dias_credito >= 60:
            recargo_credito = Decimal('0.10') # Recargo del 10% si es de 60 días
        elif dias_credito >= 30:
            recargo_credito = Decimal('0.05') # Recargo del 5% si es de 30 días
        elif dias_credito >= 15:
            recargo_credito = Decimal('0.02')  # Recargo del 2% si es más de 15 días y menos de 30
        else:
            recargo_credito = Decimal('0.00')  # Sin recargo si es menos de 15 días
        gasto_total_con_credito = gasto_total_unitario*(Decimal('1') + recargo_credito)
        total_redondeado = gasto_total_con_credito
        
        # Redondear a 2 decimales (centavos) usando ROUND_HALF_UP
        total_redondeado = total_redondeado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) 
        total_iva_calculado = (total_redondeado * Decimal('1.13')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) # Calcula total con IVA del 13%
        self.total = total_redondeado
        self.total_iva = total_iva_calculado
        Cotizacion.objects.filter(pk=self.pk).update(total=self.total, total_iva=self.total_iva)  # evita recursión
        return self.total
    
    def save(self, *args, **kwargs):

        # 🔹 Estado previo SIEMPRE definido
        estado_anterior = None
        if self.pk:
            estado_anterior = (
                Cotizacion.objects
                .filter(pk=self.pk)
                .values_list('estatus', flat=True)
                .first()
            )

        # 🔹 Correlativo SOLO al crear
        if self.pk is None and not self.correlativo:

            anio = now().year % 100
            prefijo = f"COT-{anio}-"

            ultimo = Cotizacion.objects.filter(
                correlativo__startswith=prefijo
            ).order_by('-correlativo').first()

            numero = 1
            if ultimo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    pass

            self.correlativo = f"{prefijo}{numero:06d}"

        super().save(*args, **kwargs)
        # Manejo de inventario solo si hay productos
        detalles = self.detalles_productos.all()
        if detalles.exists():
            try:
                with transaction.atomic():
                    for detalle in detalles:
                        inventario = Inventario.objects.get(producto=detalle.producto)

                        # Si antes NO estaba aprobada y ahora sí => descontar
                        if estado_anterior != 'aprobada' and self.estatus == 'aprobada':
                            if inventario.cantidad >= detalle.cantidad:
                                inventario.cantidad -= detalle.cantidad
                            else:
                                inventario.cantidad = 0

                        # Si antes estaba aprobada y ahora NO => devolver inventario
                        elif estado_anterior == 'aprobada' and self.estatus != 'aprobada':
                            inventario.cantidad += detalle.cantidad

                        inventario.save()
            except Inventario.DoesNotExist:
                # Podés agregar logging aquí si un producto no tiene inventario
                pass

    def __str__(self):
        return f" {self.correlativo} - Cliente: {self.cliente.nombre_empresa} - Total: ${self.total_iva} - Estatus: {self.estatus}"

class DetalleCotizacionProductos(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name="detalles_productos", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    unidades_cantidad = models.CharField(max_length=50, default='Unidad')  # Unidades de la cantidad
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        verbose_name = "Cotizacion de Producto"
        verbose_name_plural = "Cotizacion de Productos"

    def save(self, *args, **kwargs):
        if self.producto:
            self.precio_unitario = self.producto.precio_unitario  # Obtener precio de Producto
            self.subtotal = self.cantidad * self.precio_unitario  # Calcular subtotal
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Detalle {self.producto.correlativo} - Cotización #{self.cotizacion.correlativo}"

class DetalleCotizacionServicios(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name="detalles_servicios", on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.PositiveIntegerField(default=1)
    unidades_cantidad = models.CharField(max_length=50, default='Unidad')  # Unidades de la cantidad
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        verbose_name = "Cotizacion de Servicio"
        verbose_name_plural = "Cotizacion de Servicios"

    def save(self, *args, **kwargs):
        if self.servicio:
            self.precio_unitario = self.servicio.precio_unitario # Obtener precio de Servicio
            self.subtotal = self.cantidad * self.precio_unitario  # Calcular subtotal
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Detalle {self.id} - Cotización #{self.cotizacion.id}"

class ListaDeMateriales(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='lista_materiales')
    descripcion_material = models.TextField(blank=True, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=0, default=1.0, blank=True)
    unidades = models.CharField(max_length=100, default='Unidad', blank=True)
    
    class Meta:
        verbose_name = "Lista de Materiales"
        verbose_name_plural = "Listas de Materiales"

    def __str__(self):
        return f"Lista de materiales de la Cotización {self.cotizacion.id} {self.cantidad} {self.unidades} de {self.descripcion_material}"
    

