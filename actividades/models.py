from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from cotizaciones.models import Cotizacion
from documentacion.models import Documentacion
from django.utils.timezone import now
from proveedores.models import Proveedor
from equipos.models import Herramienta
import base64
from PIL import Image
from io import BytesIO
import io
from datetime import datetime
import os
from django.core.files.base import ContentFile
import os
import logging

logger = logging.getLogger('media')


def reducir_imagen_upload(
    imagen_field,
    max_kb=300,
    max_size=(1920, 1920)
):
    if not imagen_field:
        return

    try:
        img = Image.open(imagen_field)
        img = img.convert("RGB")  # evita PNG gigantes

        img.thumbnail(max_size, Image.LANCZOS)

        quality = 85
        buffer = BytesIO()

        while True:
            buffer.seek(0)
            buffer.truncate()

            img.save(
                buffer,
                format="JPEG",
                optimize=True,
                quality=quality
            )

            if buffer.tell() / 1024 <= max_kb or quality <= 30:
                break

            quality -= 5

        nombre = os.path.splitext(imagen_field.name)[0] + ".jpg"
        imagen_field.file = ContentFile(buffer.getvalue(), name=nombre)

        logger.info(
            "Imagen optimizada",
            extra={"archivo": imagen_field.name}
        )

    except Exception:
        logger.exception(
            "Error reduciendo imagen",
            extra={"archivo": getattr(imagen_field, "name", "desconocido")}
        )
        
def ruta_imagen_antes(instance, filename):
    correlativo = instance.correlativo or 'sin_correlativo'
    return f"ordenes/{correlativo}/imagenes/antes/{filename}"

def ruta_imagen_despues(instance, filename):
    correlativo = instance.correlativo or 'sin_correlativo'
    return f"ordenes/{correlativo}/imagenes/despues/{filename}"

def firma_upload_path(instance, filename):
    return f"ordenes/{instance.correlativo}/firmas/{filename}"

class Ordendetrabajo(models.Model):
    ESTATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('programado', 'Programado'),
        ('en_proceso', 'En Proceso'),
        ('terminado', 'Terminado'),
    ]
    
    ESTATUS = [
        ('Si', 'Sí'),  
        ('No', 'No'),
    ]
    
    HORARIOS = [
        ('AM', 'Matutino 6-3'),  
        ('PM', 'Vespertino 12-9'),
        ('PM2', 'Nocturno 9-6'),
        ('8-5', 'Horario Normal 8-5'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Critica'),
    ]
    
    TIPO_ACTIVIDAD = [
        ('mantenimiento_preventivo', 'Mantenimiento Preventivo'),
        ('mantenimiento_correctivo', 'Mantenimiento Correctivo'),
        ('rutina', 'Rutina'),
        ('diagnostico', 'Diagnostico'),
        ('configuracion', 'Configuracion'),
        ('entrega_retiro', 'Entrega_retiro'),
        ('fabricacion', 'Fabricacion'),
        ('fontaneria', 'Fontaneria'),
        ('construccion', 'Construccion'),
        ('instalacion', 'Instalación'),
        ('desinstalacion', 'Desinstalación'),
        ('montaje', 'Montaje'),
        ('desmontaje', 'Desmontaje'),
        ('reparacion', 'Reparación'),
        ('otro', 'Otro'),
    ]
    
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    equipo = models.ManyToManyField('equipos.Equipo', blank=True)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True)
    cotizacion = models.ForeignKey(Cotizacion, blank=False, on_delete=models.CASCADE,)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    tipo_actividad = models.CharField(
        max_length=30,   # suficiente para el valor más largo
        choices=TIPO_ACTIVIDAD,
        default='mantenimiento_correctivo'
    )
    fecha_inicio = models.DateField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='pendiente')
    personal_asignado = models.ManyToManyField(
        User,
        blank=True,
        related_name='trabajos_asignados'
    )
    horas_hombre_estimadas = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, blank=True, null=True)
    equipo_funcionando = models.CharField(max_length=4, choices=ESTATUS, default='No')
    herramientas_necesarias = models.ManyToManyField(Herramienta, blank=True)
    horarios_actividad = models.CharField(max_length=4, choices=HORARIOS, default='8-5')
    documentos_necesarios = models.ManyToManyField(Documentacion, blank=True)
    proveedores = models.ManyToManyField(Proveedor, blank=True)
    notas = models.TextField(blank=True)
    comentarios = models.TextField(blank=True)
    imagen_antes_1 = models.ImageField(upload_to=ruta_imagen_antes, null=True, blank=True)
    imagen_antes_2 = models.ImageField(upload_to=ruta_imagen_antes, null=True, blank=True)
    imagen_despues_1 = models.ImageField(upload_to=ruta_imagen_despues, null=True, blank=True)
    imagen_despues_2 = models.ImageField(upload_to=ruta_imagen_despues, null=True, blank=True)
    nombre_recibe = models.CharField(max_length=200, blank=True, null=True)
    firma_cliente = models.TextField(blank=True, null=True)
    firma_cliente_img = models.ImageField(upload_to=firma_upload_path, blank=True, null=True)
    detalleplan = models.ForeignKey(
    'planes_mantenimiento.DetallePlanMantenimiento',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="ots_generadas"
    )
    class Meta:
        verbose_name = "Orden de trabajo"
        verbose_name_plural = "Órdenes de trabajo"
        
    IMAGENES_OT = (
        'imagen_antes_1',
        'imagen_antes_2',
        'imagen_despues_1',
        'imagen_despues_2',
    )
        
    def save(self, *args, **kwargs):
        # 🔹 Sincronizar datos SIEMPRE
        self.cliente = self.cotizacion.cliente
        self.descripcion = self.cotizacion.Descripcion or ""

        es_nuevo = self.pk is None

        # 🔹 Estado previo (por si luego lo necesitas)
        estado_anterior = None
        if not es_nuevo:
            estado_anterior = (
                Ordendetrabajo.objects
                .filter(pk=self.pk)
                .values_list('estatus', flat=True)
                .first()
            )

        # 🔹 Correlativo SOLO al crear
        if es_nuevo and not self.correlativo:

            anio = now().year % 100
            prefijo = f"OT-{anio}-"

            ultimo = Ordendetrabajo.objects.filter(
                correlativo__startswith=prefijo
            ).order_by('-correlativo').first()

            numero = 1
            if ultimo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    pass

            self.correlativo = f"{prefijo}{numero:06d}"

        # 🔹 Evitar None en plantillas
        if self.nombre_recibe is None:
            self.nombre_recibe = ""
            
        # 🔒 REDUCIR IMÁGENES ANTES DE GUARDAR
        for campo in self.IMAGENES_OT:
            imagen = getattr(self, campo)
            reducir_imagen_upload(imagen, max_kb=300)

        # 🔹 Guardar
        super().save(*args, **kwargs)

        # 🔹 Sincronizar equipos (M2M solo después del save)
        self.equipo.set(self.cotizacion.equipo.all())

        # 🔹 Procesar firmas SOLO si existen
        if self.firma_cliente:
            self._procesar_firmas()


    # -----------------------------
    # Procesar firmas
    # -----------------------------
    def _procesar_firmas(self):
        updated_fields = []
        for tipo in ["cliente",]:
            signature_data = getattr(self, f"firma_{tipo}")
            if signature_data:
                path = self._save_signature_as_image(
                    signature_data,
                    f"{self.correlativo}_{tipo}.png",
                    tipo
                )
                if path:
                    updated_fields.append(f"firma_{tipo}_img")

        if updated_fields:
            super().save(update_fields=updated_fields)

    def _save_signature_as_image(self, signature_data, filename, tipo):
        try:
            # Quitar el prefijo "data:image/png;base64,"
            if signature_data.startswith("data:image"):
                signature_data = signature_data.split(",")[1]

            # Decodificar base64
            image_data = base64.b64decode(signature_data)
            buffer = BytesIO(image_data)

            # Abrir con PIL y guardar
            img = Image.open(buffer)
            full_path = os.path.join(settings.MEDIA_ROOT, firma_upload_path(self, filename))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            img.save(full_path, format="PNG")

            setattr(self, f"firma_{tipo}_img", firma_upload_path(self, filename))
            return firma_upload_path(self, filename)
        except Exception as e:
            print(f"⚠️ Error guardando firma {tipo}: {e}")
            return None

    def __str__(self):
        return f"{self.correlativo} - {self.cliente.nombre_empresa}"   
    