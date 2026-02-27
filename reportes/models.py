from django.db import models
from django.contrib.auth.models import User
from clientes.models import Cliente
from core.fields import RichTextSimpleField

class Reporte(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    categoria = RichTextSimpleField(max_length=100)
    descripcion = RichTextSimpleField()
    cantidad = models.PositiveIntegerField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    enlace_documento = models.URLField(max_length=200, null=True, blank=True)  # Campo para el enlace

    def __str__(self):
        return f"Reporte de {self.categoria} - Cliente: {self.cliente.nombre}"
