from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.utils.imagenes import ImageReduceMixin
from core.fields import RichTextMediumField


def ruta_imagen_equipo(instance, filename):
    codigo_interno = instance.codigo_interno or 'sin_correlativo'
    return f"equipos/imagenes_equipos/{codigo_interno}/imagenes/{filename}"

def ruta_imagen_herramienta(instance, filename):
    codigo_interno = instance.codigo_interno or 'sin_correlativo'
    return f"equipos/imagenes_herramientas/{codigo_interno}/imagenes/{filename}"

class Equipo(ImageReduceMixin, models.Model):
    
    IMAGE_FIELDS = ("imagen_equipo",)
    
    nombre = models.CharField(max_length=500, default='equipo_interno')
    descripcion = RichTextMediumField(max_length=1000, default='equipo de uso en empresa')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, blank=True, null=True)
    marca = models.CharField(max_length=100, default='Generico')
    modelo = models.CharField(max_length=100, default='Modelo Generico')
    serie = models.CharField(max_length=100, default='Serie Generica')
    codigo_interno = models.CharField(max_length=100, default='Codigo Interno segun SG')
    ubicacion = RichTextMediumField(max_length=1000, default='Ubicación del equipo en la empresa')
    estatus = models.CharField(max_length=50, default='funcionando')
    categoria =models.CharField(max_length=100, null=False, default='General')
    componentes = models.PositiveIntegerField(default=1)
    especificaciones = RichTextMediumField(max_length=1000, default='especificaciones técnicas del equipo')
    notas = RichTextMediumField(blank=True)
    imagen_equipo = models.ImageField(upload_to=ruta_imagen_equipo, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.reducir_imagenes()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"

    
class Herramienta(ImageReduceMixin, models.Model):
    
    IMAGE_FIELDS = ("imagen_herramienta",)
    
    ESTADOS = [
        ('en_uso', 'En uso'),
        ('fuera_de_uso', 'Fuera de uso'),
        ('uso_limitado', 'Uso limitado'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = RichTextMediumField(blank=True)
    categoria = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    modelo = models.CharField(max_length=100, blank=True)
    codigo_interno = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='en_uso')
    componentes = models.PositiveIntegerField(default=1)
    especificaciones = RichTextMediumField(max_length=1000, default='especificaciones técnicas de la herramienta')
    notas = RichTextMediumField(blank=True)
    imagen_herramienta = models.ImageField(upload_to=ruta_imagen_herramienta, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.reducir_imagenes()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"
    
class HistorialTrabajos(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='historial_mantenimientos', default=1)
    ordenes_trabajo = models.ManyToManyField("actividades.Ordendetrabajo")
    fecha_registro = models.DateField("Fecha de Registro", auto_now_add=False)
    notas = RichTextMediumField(blank=True)
    class Meta:
        verbose_name = "Historial de trabajo"
        verbose_name_plural = "Historial de trabajos"
