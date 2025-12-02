from django.db import models
from clientes.models import Cliente
from actividades.models import Ordendetrabajo
import datetime
from datetime import timedelta

class EquipoCliente(models.Model):
    nombre = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=100, default='equipo de uso en empresa')
    marca = models.CharField(max_length=100, default='Generico')
    modelo = models.CharField(max_length=100, default='Modelo Generico')
    serie = models.CharField(max_length=100, default='Serie Generica')
    codigo_interno = models.CharField(max_length=100, default='Codigo Interno segun SG')
    ubicacion = models.CharField(max_length=100, default='Ubicación del equipo segun el cliente')
    estatus = models.CharField(max_length=50, default='funcionando')  # Ej. "Disponible", "En mantenimiento", etc.
    categoria = models.CharField(max_length=100, null=False, default='General')  # Ej. "Computadoras", "Herramientas", etc.
    cantidad = models.PositiveIntegerField(default=0)  # Para contar la cantidad de equipos
    
    def __str__(self):
     return f"{self.nombre} ({self.serie})"
    
class HistorialMantenimiento(models.Model):
    equipo_cliente = models.ForeignKey(EquipoCliente, on_delete=models.CASCADE, related_name='historial_mantenimientos', default=1)
    fecha_mant = models.DateField("Fecha de Mantenimiento", auto_now=False, auto_now_add=False, default=datetime.date.today)
    ordenes_trabajo = models.ManyToManyField(Ordendetrabajo, related_name='historial_mantenimientos')
    proximo_mant = models.DateField("Fecha estimada de Proximo Mantenimiento", auto_now=False, auto_now_add=False, default=datetime.date.today)
    notas = models.TextField(blank=True)
    

    def __str__(self):
     return f"Mantenimiento de {self.equipo_cliente.nombre} en {self.fecha_mant}"