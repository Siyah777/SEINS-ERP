from django.db import models
from django.contrib.auth.models import User

class Empleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    fecha_ingreso = models.DateField(verbose_name="Fecha de ingreso")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    sueldo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sueldo")
    numero_dui = models.CharField(max_length=10, verbose_name="Número de DUI")
    nit = models.CharField(max_length=17, verbose_name="NIT")
    id_seguro_social = models.CharField(max_length=15, verbose_name="ID de Seguro Social")
    cuenta_bancaria = models.CharField(max_length=25, verbose_name="Cuenta bancaria")
    fotografia = models.ImageField(upload_to='fotografias_empleados/', blank=True, null=True, verbose_name="Fotografía")
    permisos = models.TextField(blank=True, null=True, verbose_name="Permisos adicionales")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.cargo}"

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"


class DetalleCompetenciaUsuario(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='competencias', verbose_name="Empleado", default=1)
    competencia = models.TextField()
    descripcion = models.TextField()
    enlace_archivo = models.URLField(verbose_name="Enlace al archivo en la nube")

    def __str__(self):
        return f"Detalle para {self.empleado.usuario.username} - {self.competencia}"