# ======================================= COMPROBANTE DE DONACION ================================================
from django.db import models
from django.utils import timezone
from clientes.models import Cliente 
from datetime import datetime
import uuid
import logging
from django.utils.html import format_html
from ..utils.utils_donacion import (firmar_dte_para_factura_otros,
enviar_dte_a_hacienda_otros,
construir_dte_json_ComprobanteDonacion
)

logger = logging.getLogger(__name__)

class ComprobanteDonacion(models.Model):
    TIPO_FACTURA_CHOICES = [
        ('15', '(CD), Comprobante de Donación'),
    ]
    donatario = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)
    descripcion_donacion = models.TextField(blank=False, null=False, default="", verbose_name="Descripción de la Donación")
    monto = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, verbose_name="Monto de la Donación")
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    tipo_factura = models.CharField(
    max_length=4,
    choices=TIPO_FACTURA_CHOICES,
    default='15',
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
        default=None,
        verbose_name="Condición de Operación"
    )
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
    estado_envio_hacienda = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'), 
        ('firmado', 'Firmado'), 
        ('enviado', 'Enviado'), 
        ('aprobado', 'Aprobado'), 
        ('rechazado', 'Rechazado')
        ], default='pendiente')
    
    class Meta:
        verbose_name = "Comprobante de Donación"
        verbose_name_plural = "Comprobantes de Donación"
        
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
    
    def save(self, *args, **kwargs):
        self.tipo_factura = '15'  # Fijar siempre el tipo de factura a '15' para donaciones
        # Generar correlativo si no existe
        if not self.correlativo and self.pk is None:
            prefijos = {
                '15': 'CD',
            }
            prefijo = prefijos.get(self.tipo_factura, 'CD')
            
            anio = datetime.now().year % 100  # 2025 -> 25
            
            ultimo = ComprobanteDonacion.objects.filter(correlativo__startswith=f"{prefijo}-{anio}-").order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    numero = 1
            while True:
                correlativo_temp = f"{prefijo}-{anio}-{numero:06d}"
                if not ComprobanteDonacion.objects.filter(correlativo=correlativo_temp).exists():
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
                construir_dte_json_ComprobanteDonacion(self)
                firmar_dte_para_factura_otros(self)
                enviar_dte_a_hacienda_otros(self)
        except Exception as e:
            logger.error(f"[DTE] Error en generación/firma/envío de factura {self.pk}: {e}")
            print(f"Error en el proceso de firma/envío: {str(e)}")

        self._procesando_dte = False
        
    def __str__(self):
        return f"Factura {self.correlativo} - {self.donatario.nombre_empresa} - {self.monto}"
            
    