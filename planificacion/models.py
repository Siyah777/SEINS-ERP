from django.db import models
from servicios.models import Servicio
from registros.models import DescripcionesPuesto  # o como se llame exactamente
from equipos.models import Herramienta
from documentacion.models import Documentacion
from proveedores.models import Proveedor

class Planificacion(models.Model):
    ESTATUS = [
        ('Si', 'Sí'),  
        ('No', 'No'),
    ]
    
    HORARIOS = [
        ('AM', 'Matutino'),  
        ('PM', 'Vespertino'),
        ('8-5', 'Horario Normal'),
    ]
    #servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, blank=True)
    descripcion = models.TextField(blank=False, null=False, default='Descripción de la planificación')
    cantidad_personas = models.PositiveIntegerField()
    especialidad = models.ManyToManyField(DescripcionesPuesto,)
    horas_estimadas = models.DecimalField(max_digits=6, decimal_places=2)
    equipo_funcionando = models.CharField(max_length=4, choices=ESTATUS, default='No')
    herramientas_necesarias = models.ManyToManyField(Herramienta, blank=True)
    horarios_actividad = models.CharField(max_length=4, choices=HORARIOS, default='8-5')
    documentos_necesarios = models.ManyToManyField(Documentacion, blank=True)
    proveedores = models.ManyToManyField(Proveedor, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Planificación para {self.descripcion} - {self.especialidad}"
    
    class Meta:
        verbose_name_plural = "Planificaciones"
