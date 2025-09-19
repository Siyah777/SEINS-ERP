# ======================================= COMPROBANTE DE RETENCION ================================================
from django.db import models
from clientes.models import Cliente   
from cotizaciones.models import Cotizacion
from decimal import Decimal
from datetime import datetime
import uuid
import logging
from django.utils import timezone
from django.utils.html import format_html
from ..utils.utils_retencion import (firmar_dte_para_factura_otros,
enviar_dte_a_hacienda_otros,
construir_dte_json_ComprobanteRetencion
)

logger = logging.getLogger(__name__)

class ComprobanteRetencion(models.Model):
    TIPO_FACTURA_CHOICES = [
        ('07', '(CR), Comprobante de Retención'),

    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)
    factura_referencia = models.ForeignKey(
        'facturacion.Factura',
        on_delete=models.PROTECT,
        null=True,
        related_name='comprobantes_retencion'
    )
    tipo_factura = models.CharField(
    max_length=4,
    choices=TIPO_FACTURA_CHOICES,
    default='07',
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
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    monto_retenido_iva = models.DecimalField(max_digits=10, decimal_places=2)
    monto_retenido_renta = models.DecimalField(max_digits=10, decimal_places=2)
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
        ('rechazado', 'Rechazado')
        ], default='pendiente')

    class Meta:
        verbose_name = "Comprobante de Retención"
        verbose_name_plural = "Comprobantes de Retención"
    
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
            
    def calcular_retenciones(self):
        """
        Calcula retenciones de IVA (1%) y de Renta (10%) según el proveedor.
        """
        if self.cliente.aplica_retencion ==True:
            self.monto_retenido_iva = round(self.factura_referencia.total_con_iva * Decimal('0.01'), 2)
            self.monto_retenido_renta = round(self.factura_referencia.total_con_iva * Decimal('0.10'), 2)
        else:
            self.monto_retenido_iva = Decimal('0.00')
            self.monto_retenido_renta = Decimal('0.00')
            logger.error(f"[DTE] Error el cliente no es agente de retención {self.pk}: {self.cliente.nombre_empresa}")
            self.observaciones = "Error: El cliente no es agente de retención."
            return
    
    def save(self, *args, **kwargs):
        self.cliente = self.factura_referencia.cliente
        self.calcular_retenciones()
        # Generar correlativo si no existe
        if not self.correlativo and self.pk is None:
            prefijos = {
                '07': 'CR',
            }
            prefijo = prefijos.get(self.tipo_factura, 'CR')
            
            anio = datetime.now().year % 100  # 2025 -> 25
            
            ultimo = ComprobanteRetencion.objects.filter(correlativo__startswith=f"{prefijo}-{anio}-").order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    numero = 1
            while True:
                correlativo_temp = f"{prefijo}-{anio}-{numero:06d}"
                if not ComprobanteRetencion.objects.filter(correlativo=correlativo_temp).exists():
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
                construir_dte_json_ComprobanteRetencion(self)
                firmar_dte_para_factura_otros(self)
                enviar_dte_a_hacienda_otros(self)
        except Exception as e:
            logger.error(f"[DTE] Error en generación/firma/envío de factura {self.pk}: {e}")
            print(f"Error en el proceso de firma/envío: {str(e)}")

        self._procesando_dte = False
        
    def __str__(self):
        return f"Factura {self.correlativo} - {self.cliente.nombre_empresa} - {self.factura_referencia}"
            