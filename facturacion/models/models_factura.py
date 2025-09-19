from django.db import models
from clientes.models import Cliente   
from cotizaciones.models import Cotizacion
from decimal import Decimal
from datetime import datetime
import uuid
import logging
from django.utils import timezone
from django.utils.html import format_html
from ..utils.utils_factura import firmar_dte_para_factura, enviar_dte_a_hacienda, construir_dte_json

logger = logging.getLogger(__name__)
 
class Factura(models.Model):
    TIPO_FACTURA_CHOICES = [
        ('01', '(CF), Consumidor Final'),
        ('03', '(CCF), Comprobante de Crédito Fiscal'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, blank=False, null=False, default=1)
    tipo_factura = models.CharField(
    max_length=4,
    choices=TIPO_FACTURA_CHOICES,
    default='01',
    verbose_name="Tipo de Factura"
    )
    condicion_operacion = models.CharField(
        max_length=20,
        choices=[
            ('01', 'Contado'),
            ('02', 'Crédito'),
            ('05', 'Donación'),
            ('07', 'Otros')
        ],
        default='01',
        verbose_name="Condición de Operación"
    )
    detalle_contingencia = models.JSONField(null=True, blank=True)
    motivo_contingencia = models.TextField(blank=True, null=True)
    tipo_contingencia = models.IntegerField(blank=True, null=True)
    ventas_no_sujetas = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    ventas_exentas = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    ventas_gravadas = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    total_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    iva_retenido = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    iva_percibido = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    total_con_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_letras = models.CharField(max_length=255, blank=True, null=True, verbose_name="Total en Letras")
    codigo_generacion = models.CharField(max_length=128, blank=True, unique=True, null=True, verbose_name="Código de Generación")
    respuesta_firmador = models.TextField(blank=True, null=True)
    respuesta_hacienda = models.TextField(blank=True, null=True)
    idenvio_hacienda = models.CharField(max_length=64, blank=True, null=True)
    numero_control = models.CharField(max_length=64, blank=True, null=True)
    sello_recepcion = models.CharField(max_length=128, blank=True, null=True)
    version_dte = models.CharField(max_length=10, blank=True, null=True)
    version_json = models.CharField(max_length=16, blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=False, default=timezone.now)
    firma = models.TextField(blank=True, null=True)
    json_dte = models.JSONField(null=True, blank=True)
    json_firmado = models.JSONField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    estado_envio_hacienda = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'), 
        ('firmado', 'Firmado'), 
        ('enviado', 'Enviado'), 
        ('aprobado', 'Aprobado'), 
        ('rechazado', 'Rechazado'),
        ('anulado', 'Anulado'),
        ('contingencia', 'Contingencia'),
        ('enviado_contingencia', 'Enviado Contingencia'),
        ], default='pendiente')
    
    _procesando_dte = False 
    
    class Meta:
        verbose_name = "Venta-facturacion"
        verbose_name_plural = "Ventas-facturacion"
    
    def estado_coloreado(self):
        color = {
            "pendiente": "orange",
            "enviado": "blue",
            "aprobado": "green",
            "firmado": "purple",
            "rechazado": "red"
        }.get(self.estado_envio_hacienda, "black")

        return format_html(
            '<strong style="color: {};">{}</strong>',
            color,
            self.get_estado_envio_hacienda_display()
        )

    estado_coloreado.short_description = "Estado Hacienda"
        
    def calcular_totales(self):
        subtotal = Decimal('0.00')
        
        if self.cotizacion:
            subtotal += self.cotizacion.total or Decimal('0.00')  
        
        self.total_sin_iva = subtotal
        iva = subtotal * Decimal('0.13')
        self.total_con_iva = subtotal + iva

    def save(self, *args, **kwargs):
        self.cliente = self.cotizacion.cliente
        self.calcular_totales()
        # Generar correlativo si no existe
        if not self.correlativo and self.pk is None:
            prefijos = {
                '01': 'CF',
                '03': 'CCF',
            }
            prefijo = prefijos.get(self.tipo_factura, 'CF')
            
            anio = datetime.now().year % 100  # 2025 -> 25
            
            ultimo = Factura.objects.filter(correlativo__startswith=f"{prefijo}-{anio}-").order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    numero = 1
            while True:
                correlativo_temp = f"{prefijo}-{anio}-{numero:06d}"
                if not Factura.objects.filter(correlativo=correlativo_temp).exists():
                    self.correlativo = correlativo_temp
                    break
                numero += 1

        # Generar código si no existe
        if not self.codigo_generacion:
            self.codigo_generacion = str(uuid.uuid4()).upper()

        # Detectar si es edición o creación
        is_new = self.pk is None

        # Guardar primero para tener PK y persistir en BD
        if self.pk is None:
            if not self.fecha_envio:
                self.fecha_envio = timezone.localtime()
        super().save(*args, **kwargs)
        
        # Prevenir recursividad infinita con atributo temporal
        if hasattr(self, '_procesando_dte') and self._procesando_dte:
            return

        self._procesando_dte = True

        try:
            # Ejecutar lógica DTE siempre que esté pendiente o sea actualización
            if not self.firma or self.estado_envio_hacienda in ['pendiente', 'rechazado']:
                construir_dte_json(self)
                firmar_dte_para_factura(self)
                enviar_dte_a_hacienda(self)
        except Exception as e:
            logger.error(f"[DTE] Error en generación/firma/envío de factura {self.pk}: {e}")
            print(f"Error en el proceso de firma/envío: {str(e)}")

        self._procesando_dte = False
        
    def __str__(self):
        return f"Factura {self.correlativo} - {self.cliente.nombre_empresa} - {self.total_con_iva} -{self.estado_envio_hacienda}"

    