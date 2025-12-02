from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from cotizaciones.models import Cotizacion
from documentacion.models import Documentacion
from proveedores.models import Proveedor
from equipos.models import Herramienta
import base64
from PIL import Image
from io import BytesIO
import io
from datetime import datetime
import os

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
        ('instalacion', 'Instalación'),
        ('desinstalacion', 'Desinstalación'),
        ('montaje', 'Montaje'),
        ('desmontaje', 'Desmontaje'),
        ('reparacion', 'Reparación'),
        ('otro', 'Otro'),
    ]
    
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    equipo = models.ForeignKey('equipos.Equipo', on_delete=models.CASCADE, blank=True, null=True)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True)
    cotizacion = models.ForeignKey(Cotizacion, blank=False, on_delete=models.CASCADE, default=1)
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
    #firma_tecnico = models.TextField(blank=True, null=True)
    firma_cliente_img = models.ImageField(upload_to=firma_upload_path, blank=True, null=True)
    #firma_tecnico_img = models.ImageField(upload_to=firma_upload_path, blank=True, null=True)
    class Meta:
        verbose_name = "Orden de trabajo"
        verbose_name_plural = "Órdenes de trabajo"
        
    def save(self, *args, **kwargs):
        self.cliente = self.cotizacion.cliente  # Asegura que el cliente siempre coincida con la cotización
        self.equipo = self.cotizacion.equipo  # Asegura que el equipo_cliente siempre coincida con la cotización
        self.descripcion = self.cotizacion.Descripcion  # Asegura que la descripción siempre coincida con la cotización
        if not self.correlativo:
            anio = datetime.now().year % 100  # 2025 -> 25
            ultimo = Ordendetrabajo.objects.order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass
            self.correlativo = f"OT-{anio}-{numero:06d}"  # OT-25-000001
        
        if self.nombre_recibe is None:
            self.nombre_recibe = ""  # evita que aparezca "None" en la plantilla
        
        super().save(*args, **kwargs)
        
        # 1️⃣ Reducir imágenes antes/después
        for campo in [self.imagen_antes_1, self.imagen_antes_2,
                      self.imagen_despues_1, self.imagen_despues_2]:
            self._reducir_imagen(campo)

        # 2️⃣ Procesar firmas
        self._procesar_firmas()
        
    def _reducir_imagen(self, imagen_field, max_kb=300):
        if imagen_field and hasattr(imagen_field, 'path'):
            try:
                img = Image.open(imagen_field.path)
                img_format = img.format or 'JPEG'
                quality = 85
                buffer = BytesIO()
                while True:
                    buffer.seek(0)
                    buffer.truncate()
                    img.save(buffer, format=img_format, optimize=True, quality=quality)
                    size_kb = buffer.tell() / 1024
                    if size_kb <= max_kb or quality <= 30:
                        break
                    quality -= 5
                with open(imagen_field.path, 'wb') as f:
                    f.write(buffer.getvalue())
            except Exception as e:
                print(f"⚠️ Error reduciendo {imagen_field.name}: {e}")

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