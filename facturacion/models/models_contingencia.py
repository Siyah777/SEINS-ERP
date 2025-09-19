from django.db import models
from decimal import Decimal
from datetime import datetime
import uuid
import logging
from django.utils import timezone
from facturacion.models import Factura
from django.utils.html import format_html
from ..utils.utils_contingencia import generar_json_contingencia, firmar_contingencia, enviar_contingencia_a_hacienda 

logger = logging.getLogger(__name__)

class Contingencia(models.Model):
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    detalle_contingencia = models.JSONField(null=True, blank=True)
    motivo_contingencia = models.TextField(blank=True, null=True)
    tipo_contingencia = models.IntegerField(blank=True, null=True)
    fecha_inicio_contingencia = models.DateTimeField(blank=True, null=True)
    fecha_fin_contingencia = models.DateTimeField(blank=True, null=True)
    codigo_generacion = models.CharField(max_length=128, blank=True, unique=True, null=True, verbose_name="Código de Generación")
    facturas_contingencia = models.ManyToManyField(Factura)
    firma = models.TextField(blank=True, null=True)
    respuesta_firmador = models.TextField(blank=True, null=True)
    respuesta_hacienda = models.TextField(blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=False, default=timezone.now)
    estado_envio_hacienda = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'), 
        ('firmado', 'Firmado'), 
        ('enviado', 'Enviado'), 
        ('aprobado', 'Aprobado'), 
        ('rechazado', 'Rechazado'),
        ('anulado', 'Anulado')
        ], default='pendiente')
    sello_recepcion = models.CharField(max_length=128, blank=True, null=True)
    version_json = models.CharField(max_length=16, blank=True, null=True)
    idenvio_hacienda = models.CharField(max_length=64, blank=True, null=True)
    class Meta:
        verbose_name = "Contingencia"
        verbose_name_plural = "Contingencias"
    
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
    
    def procesar_envio_hacienda(self):
        from ..utils.utils_contingencia import enviar_contingencia_a_hacienda 
        # Enviar la contingencia completa a Hacienda
        enviar_contingencia_a_hacienda(self)
        
    def save(self, *args, **kwargs):
        # Generar correlativo si no existe
        if not self.correlativo and self.pk is None:
            prefijos = {
                'EC': 'EC'
            }
            prefijo = prefijos.get('EC')
            
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
                if not Contingencia.objects.filter(correlativo=correlativo_temp).exists():
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
                generar_json_contingencia(self)
                firmar_contingencia(self)
                enviar_contingencia_a_hacienda(self)
        except Exception as e:
            logger.error(f"[DTE] Error en generación/firma/envío de contingencia {self.pk}: {e}")
            print(f"Error en el proceso de firma/envío: {str(e)}")

        self._procesando_dte = False
        
    def __str__(self):
        return f"Factura {self.correlativo}"

    