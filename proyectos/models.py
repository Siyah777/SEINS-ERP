from django.db import models

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre del proyecto
    descripcion = models.CharField(max_length=255) # Descripción breve del proyecto
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    consideraciones = models.CharField(max_length=255) # Observaciones espaciales del proyecto
    ESTATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('proceso', 'En proceso'),
        ('terminado', 'Terminado'),
    ]
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='pendiente')

    def __str__(self):
        return self.nombre

