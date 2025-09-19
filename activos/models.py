from django.db import models

class Activo(models.Model):
    ESTADO_CHOICES = [
        ('alta', 'De alta'),
        ('baja', 'De baja'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100, blank=True)
    serie = models.CharField(max_length=100, blank=True)
    codigo_interno = models.CharField(max_length=100, unique=True)
    ficha_ingreso = models.DateField()
    estado_sistema = models.CharField(max_length=5, choices=ESTADO_CHOICES, default='alta')
    cantidad = models.PositiveIntegerField(default=1)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo_interno})"

class Infraestructura(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    codigo_interno = models.CharField(max_length=50, unique=True)
    encargado = models.CharField(max_length=100, blank=True, null=True)
    caracteristicas = models.TextField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre