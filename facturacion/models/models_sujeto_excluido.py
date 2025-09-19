# ======================================= FACTURA SUJETO EXCLUIDO ================================================
from django.db import models
from clientes.models import Cliente   
from cotizaciones.models import Cotizacion
from decimal import Decimal
from datetime import datetime
import uuid
import logging
from django.utils import timezone
from django.utils.html import format_html
from ..utils.utils_sujeto_excluido import (firmar_dte_para_factura_otros,
enviar_dte_a_hacienda_otros,
construir_dte_json_FacturaSujetoExcluido
)

logger = logging.getLogger(__name__)

# ======================================= MODELO FACTURA SUJETO EXCLUIDO ====================================

class FacturaSujetoExcluido(models.Model):
    TIPO_FACTURA_CHOICES = [
        ('14', '(FS), Factura Sujeto Excluido'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    tipo_factura = models.CharField(
    max_length=4,
    choices=TIPO_FACTURA_CHOICES,
    default='14',
    verbose_name="Tipo de Factura"
    )
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, blank=False, null=False, default=1)
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
    
    def aplicar_exencion_si_corresponde(self):
        """
        Aplica lógica de exención para contribuyentes excluidos.
        """
        if self.cliente.tipo_cliente == "excluido":
            self.total_sin_iva = self.cotizacion.total
            self.ventas_exentas = self.total_sin_iva
            self.ventas_gravadas = Decimal('0.00')
            self.iva = Decimal('0.00')
        else:
            self.ventas_gravadas = self.total_sin_iva or Decimal('0.00')
            ventas_gravadas = self.ventas_gravadas or Decimal('0.00')
            self.iva = round(ventas_gravadas * Decimal('0.13'), 2)
    
    #print(f"[DEBUG] Exenta: {self.ventas_exentas}, Gravada: {self.ventas_gravadas}, IVA: {self.iva}")
    
    class Meta:
        verbose_name = "Factura Sujeto Excluido"
        verbose_name_plural = "Facturas Sujetos Excluidos"
        
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
        self.cliente = self.cotizacion.cliente
        self.aplicar_exencion_si_corresponde()
        # Generar correlativo si no existe
        if not self.correlativo and self.pk is None:
            prefijos = {
                '14': 'FS',
            }
            prefijo = prefijos.get(self.tipo_factura, 'FS')
            
            anio = datetime.now().year % 100  # 2025 -> 25
            
            ultimo = FacturaSujetoExcluido.objects.filter(correlativo__startswith=f"{prefijo}-{anio}-").order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    numero = 1
            while True:
                correlativo_temp = f"{prefijo}-{anio}-{numero:06d}"
                if not FacturaSujetoExcluido.objects.filter(correlativo=correlativo_temp).exists():
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
         self.fecha_envio = timezone.localtime()
        super().save(*args, **kwargs)
        
        # Prevenir recursividad infinita con atributo temporal
        if hasattr(self, '_procesando_dte') and self._procesando_dte:
            return

        self._procesando_dte = True

        try:
            # Ejecutar lógica DTE siempre que esté pendiente o sea actualización
            if not self.firma or self.estado_envio_hacienda in ['pendiente', 'rechazado']:
                construir_dte_json_FacturaSujetoExcluido(self)
                firmar_dte_para_factura_otros(self)
                enviar_dte_a_hacienda_otros(self)
        except Exception as e:
            logger.error(f"[DTE] Error en generación/firma/envío de factura {self.pk}: {e}")
            print(f"Error en el proceso de firma/envío: {str(e)}")

        self._procesando_dte = False
        
    def __str__(self):
        return f"Factura {self.correlativo} - {self.cliente.nombre_empresa} - {self.total_con_iva}"
    pass