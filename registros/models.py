from django.db import models

class Atestado(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
    enlace_archivo = models.URLField(verbose_name="Enlace al archivo en la nube")
    
    class Meta:
        verbose_name = "Atestado-Contrato"
        verbose_name_plural = "Atestados-Contratos"
        
    def __str__(self):
        return self.nombre

class DescripcionesPuesto(models.Model):
    nombre_puesto = models.CharField(max_length=100, verbose_name="Nombre del puesto")
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario base")
    pago_adicional = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="pago dicional", default=0)
    actividades = models.TextField(verbose_name="Actividades que realiza")
    competencias_requeridas = models.TextField(verbose_name="Competencias requeridas")
    jefe_inmediato = models.CharField(max_length=100, verbose_name="Jefe inmediato (puesto)")
    comentarios = models.TextField(blank=True, null=True, verbose_name="Comentarios")

    def __str__(self):
        return self.nombre_puesto

    class Meta:
        verbose_name = "Descripción de Puesto"
        verbose_name_plural = "Descripciones de Puestos"

