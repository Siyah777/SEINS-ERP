from django.db import models

class Indicador(models.Model):
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    formula = models.TextField()
    criterio_de_aceptacion = models.TextField()
    consideraciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"

    def __str__(self):
        return self.nombre
