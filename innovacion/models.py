from django.db import models

class Innovacion(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('en_progreso', 'En Progreso'), ('completado', 'Completado')], default='pendiente')
    requisitos = models.TextField(blank=True, null=True)  # Requisitos necesarios para cumplir la innovación
    responsable = models.CharField(max_length=255, blank=True, null=True)
    documento_adjunto = models.FileField(upload_to='innovacion_documentos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Innovación"
        verbose_name_plural = "Innovaciones"
    
    def __str__(self):
        return self.nombre
