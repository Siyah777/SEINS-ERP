from django.db import models
from clientes.models import Cliente   
import uuid
from django.utils import timezone
from datetime import datetime
from django.utils.html import format_html
from ..utils.utils_credito_debito import  (construir_dte_json_notacreditodebito,
firmar_dte_para_factura_otros,
enviar_dte_a_hacienda_otros)
from decimal import Decimal
import logging
from clientes.models import Cliente 
from facturacion.models import Factura

logger = logging.getLogger(__name__)

 # ======================================= NOTAS DE CREDITO/DEBITO ================================================
    
class NotaCreditoDebito(models.Model):
    TIPO_NOTA_CHOICES = [
        ('05', '(NC), Nota de Crédito'),
        ('06', '(ND), Nota de Débito'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)
    factura_referencia = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="notas", verbose_name="Factura Referencia (solo creditos fiscales)")
    condicion_operacion = models.CharField(
        max_length=20,
        choices=[
            ('01', 'Contado'),
            ('02', 'Crédito'),
            ('05', 'Donación'),
            ('07', 'Otros')
        ],
        default='01',
        null=True,
        blank=True,
        verbose_name="Condición de Operación"
    )
    tipo_nota = models.CharField(
    max_length=4,
    choices=TIPO_NOTA_CHOICES,
    default='05',
    verbose_name="Tipo de Nota"
    )
    motivo = models.TextField()
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nuevo_monto = models.DecimalField(max_digits=10, decimal_places=2)
    nuevo_monto_letras = models.CharField(max_length=255, blank=True, null=True, verbose_name="Total en Letras")
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
        verbose_name = "Nota de Credito/Debito"
        verbose_name_plural = "Notas de Credito/Debito"
    
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
        self.cliente = self.factura_referencia.cliente
        if not self.factura_referencia:
            logger.error("No se puede procesar NotaCreditoDebito sin factura_referencia asociada.")
            return  # O lanzar excepción según cómo manejes errores

        total_con_iva = self.factura_referencia.total_con_iva

        if total_con_iva == self.nuevo_monto:
            logger.info(
                f"No se genera nota para factura {self.factura_referencia_id}: "
                f"monto sin cambios ({total_con_iva} -> {self.nuevo_monto})"
            )
            return  # Detener procesamiento porque no hay cambios

        if self.nuevo_monto > total_con_iva:
            self.tipo_nota = '06'   # Nota de débito (aumenta valor)
        elif self.nuevo_monto < total_con_iva:
            self.tipo_nota = '05'   # Nota de crédito (reduce valor)
        else:
            return  # No debería llegar aquí, pero por seguridad evitamos guardar

        # Después de calcular tipo_nota
        if self.tipo_nota:
            self.tipo_factura = self.tipo_nota
        # Generar correlativo si no existe
        if not self.correlativo and self.pk is None:
            prefijos = {
                '05': 'NC',
                '06': 'ND',
            }
            prefijo = prefijos.get(self.tipo_nota, 'NC')
            
            anio = datetime.now().year % 100  # 2025 -> 25
            
            ultimo = NotaCreditoDebito.objects.filter(correlativo__startswith=f"{prefijo}-{anio}-").order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    numero = 1
            while True:
                correlativo_temp = f"{prefijo}-{anio}-{numero:06d}"
                if not NotaCreditoDebito.objects.filter(correlativo=correlativo_temp).exists():
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
                construir_dte_json_notacreditodebito(self)
                firmar_dte_para_factura_otros(self)
                enviar_dte_a_hacienda_otros(self)
        except Exception as e:
            logger.error(f"[DTE] Error en generación/firma/envío de factura {self.pk}: {e}")
            print(f"Error en el proceso de firma/envío: {str(e)}")

        self._procesando_dte = False
        
    def __str__(self):
        return f"Factura {self.correlativo} - {self.cliente.nombre_empresa} - {self.nuevo_monto}"