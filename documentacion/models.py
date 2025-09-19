from django.db import models

class Documentacion(models.Model):
    nombre = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100)
    fecha_actualizacion = models.DateField()
    documento = models.URLField(max_length=200, null=True, blank=True)  
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        
    def __str__(self):
        return f"{self.nombre} v{self.version}"

