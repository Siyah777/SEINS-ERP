from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from PIL import Image
from io import BytesIO

def ruta_imagen_equipo(instance, filename):
    correlativo = instance.correlativo or 'sin_correlativo'
    return f"equipos/{correlativo}/imagenes/{filename}"

def ruta_imagen_herramienta(instance, filename):
    correlativo = instance.correlativo or 'sin_correlativo'
    return f"equipos/herramientas/{correlativo}/imagenes/{filename}"

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

class Equipo(models.Model):
    nombre = models.CharField(max_length=500, default='equipo_interno')
    descripcion = models.CharField(max_length=1000, default='equipo de uso en empresa')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, blank=True, null=True)
    marca = models.CharField(max_length=100, default='Generico')
    modelo = models.CharField(max_length=100, default='Modelo Generico')
    serie = models.CharField(max_length=100, default='Serie Generica')
    codigo_interno = models.CharField(max_length=100, default='Codigo Interno segun SG')
    ubicacion = models.CharField(max_length=1000, default='Ubicación del equipo en la empresa')
    estatus = models.CharField(max_length=50, default='funcionando')
    categoria = models.CharField(max_length=100, null=False, default='General')
    componentes = models.PositiveIntegerField(default=1)
    especificaciones = models.CharField(max_length=1000, default='especificaciones técnicas del equipo')
    notas = models.TextField(blank=True)
    imagen_equipo = models.ImageField(upload_to=ruta_imagen_equipo, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self._reducir_imagen(self.imagen_equipo)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"
    
class Herramienta(models.Model):
    ESTADOS = [
        ('en_uso', 'En uso'),
        ('fuera_de_uso', 'Fuera de uso'),
        ('uso_limitado', 'Uso limitado'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    modelo = models.CharField(max_length=100, blank=True)
    serie = models.CharField(max_length=100, blank=True)
    codigo_interno = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='en_uso')
    componentes = models.PositiveIntegerField(default=1)
    especificaciones = models.CharField(max_length=1000, default='especificaciones técnicas de la herramienta')
    notas = models.TextField(blank=True)
    imagen_herramienta = models.ImageField(upload_to=ruta_imagen_herramienta, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self._reducir_imagen(self.imagen_herramienta)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"
    
class HistorialTrabajos(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='historial_mantenimientos', default=1)
    ordenes_trabajo = models.ManyToManyField("actividades.Ordendetrabajo")
    fecha_registro = models.DateField("Fecha de Registro", auto_now_add=False)
    notas = models.TextField(blank=True)
    class Meta:
        verbose_name = "Historial de trabajo"
        verbose_name_plural = "Historial de trabajos"
