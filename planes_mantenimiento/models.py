from django.db import models          
from equipos.models import Equipo             
from documentacion.models import Documentacion  
from proveedores.models import Proveedor

class PlanMantenimiento(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    descripcion = models.TextField(default="Plan de mantenimiento personalizado")

    def __str__(self):
        return f"Plan de mantenimiento para {self.equipo.nombre}"

class DetallePlanMantenimiento(models.Model):
    plan = models.ForeignKey(PlanMantenimiento, on_delete=models.CASCADE, related_name='detalles')
    actividad = models.CharField(max_length=500)
    motivo_actividad = models.CharField(max_length=500)
    frecuencia = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    procedimiento = models.ForeignKey(Documentacion, on_delete=models.SET_NULL, null=True, blank=True)
    especialista = models.CharField(max_length=100)
    proveedores = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    herramientas = models.CharField(max_length=500, default='caja de herramientas')
    cantidad_personas = models.PositiveIntegerField(default=1)
    tiempo_realizacion_estimado = models.DurationField()
    hora_realizacion_estimada = models.TimeField(null=True, blank=True)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actividad} - {self.plan.equipo.nombre}"

