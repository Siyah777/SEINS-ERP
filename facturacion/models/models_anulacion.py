# ======================================= ANULACION ============================================================
from django.db import models
from django.utils import timezone
from clientes.models import Cliente 
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime
import uuid
import logging
from django.utils.html import format_html
from ..utils.utils_anulacion import( firmar_dte_para_factura_Anulacion,
enviar_dte_a_hacienda_Anulacion,
construir_dte_json_Anulacion
)

logger = logging.getLogger(__name__)

class Anulacion(models.Model):
    TIPO_FACTURA_CHOICES = [
        ('01', '(CF), Consumidor Final'),
        ('03', '(CCF), Comprobante de Crédito Fiscal'),
        ('05', '(NC), Nota de Crédito'),
        ('06', '(ND), Nota de Débito'),
        ('04', '(NR), Nota de Remisión'),
        ('07', '(CR), Comprobante de Retención'),
        ('14', '(FS), Factura Sujeto Excluido'),
        ('15', '(CD), Comprobante de Donación'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)
    factura_anular = models.ForeignKey(
        'facturacion.Factura',
        on_delete=models.PROTECT,
        null=True,
        related_name='Anulaciones'
    )
    tipo_anulacion = models.CharField(max_length=200, blank=True, null=True)
    motivo_anulacion = models.TextField(blank=False, null=False, default='Anulación por cancelación de factura')
    responsable_anulacion = models.ForeignKey(User, on_delete=models.CASCADE,
    blank=False,
    null=False,
    related_name='anulaciones_responsable',
    default=1,
    verbose_name="Responsable de Anulación"
    )
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
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
    codigo_generacion_r = models.CharField(max_length=128, blank=True, unique=True, null=True, verbose_name="Código de Generación")
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
        verbose_name = "Anulacion"
        verbose_name_plural = "Anulaciones"
        
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
        # Generar correlativo si no existe
        if not self.correlativo and self.pk is None:
            prefijos = {
                'AN': 'AN',
            }
            prefijo = prefijos.get('AN')
            
            anio = datetime.now().year % 100  # 2025 -> 25
            
            ultimo = Anulacion.objects.filter(correlativo__startswith=f"{prefijo}-{anio}-").order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    numero = 1
            while True:
                correlativo_temp = f"{prefijo}-{anio}-{numero:06d}"
                if not Anulacion.objects.filter(correlativo=correlativo_temp).exists():
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
                construir_dte_json_Anulacion(self)
                firmar_dte_para_factura_Anulacion(self)
                enviar_dte_a_hacienda_Anulacion(self)
        except Exception as e:
            logger.error(f"[DTE] Error en generación/firma/envío de factura {self.pk}: {e}")
            print(f"Error en el proceso de firma/envío: {str(e)}")

        self._procesando_dte = False
        
    def __str__(self):
        return f"Factura {self.correlativo} - {self.cliente.nombre_empresa} - {self.total_con_iva}"
    