from django.db import models

class Proceso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Auditoria(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE)
    fecha = models.DateField()
    responsable = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Auditoría {self.proceso.nombre} - {self.fecha}"

class NoConformidad(models.Model):
    auditoria = models.ForeignKey(Auditoria, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_detectada = models.DateField()
    gravedad = models.CharField(max_length=50, choices=[
        ('Menor', 'Menor'),
        ('Mayor', 'Mayor'),
        ('Crítica', 'Crítica'),
    ])
    estatus = models.CharField(max_length=50, choices=[
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Resuelto', 'Resuelto'),
    ], default='Pendiente')

    class Meta:
        verbose_name = "No conformidad"
        verbose_name_plural = "No conformidades"
        
    def __str__(self):
        return f"No Conformidad ({self.gravedad}) - {self.fecha_detectada}"

class AccionCorrectiva(models.Model):
    no_conformidad = models.ForeignKey(NoConformidad, on_delete=models.CASCADE)
    descripcion = models.TextField()
    responsable = models.CharField(max_length=100)
    fecha_compromiso = models.DateField()
    fecha_cierre = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Acción Correctiva para NC {self.no_conformidad.id}"
