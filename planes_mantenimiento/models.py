from django.db import models          
from equipos.models import Herramienta            
from documentacion.models import Documentacion
from proveedores.models import Proveedor
from cotizaciones.models import Cotizacion
from datetime import datetime, timedelta
from core.fields import RichTextMediumField

class PlanMantenimiento(models.Model):
    codigo_plan = models.CharField(max_length=100, unique=True, default='PM-001')
    descripcion = RichTextMediumField(default="Plan de mantenimiento personalizado")
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = "Plan de mantenimiento"
        verbose_name_plural = "Planes de mantenimiento"

    def __str__(self):
        return f"Plan de mantenimiento para {self.codigo_plan}"

class DetallePlanMantenimiento(models.Model):
    FRECUENCIAS = [
        ("8h", "Cada 8 horas"),
        ("diario", "Diario"),
        ("semanal", "Semanal"),
        ("mensual", "Mensual"),
        ("bimensual", "Bimensual"),
        ("trimestral", "Trimestral"),
        ("semestral", "Semestral"),
        ("anual", "Anual"),
    ]
    
    HORARIOS = [
        ('AM', 'Matutino 6-3'),  
        ('PM', 'Vespertino 12-9'),
        ('PM2', 'Nocturno 9-6'),
        ('8-5', 'Horario Normal 8-5'),
    ]
    
    plan = models.ForeignKey(PlanMantenimiento, on_delete=models.CASCADE, related_name='detalles')
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='cotizacion', null=True, blank=False)
    motivo_actividad = models.CharField(max_length=500, blank=True)
    frecuencia = models.CharField(
    max_length=20,
    choices=FRECUENCIAS,
    default="mensual",  
    )
    fechainicio = models.DateField(null=False, blank=False)
    horarios_actividad = models.CharField(max_length=4, choices=HORARIOS, default='8-5')
    cantidad_autogenerada = models.PositiveIntegerField(
        default=1,
        help_text="Número de OTs futuras a generar automáticamente."
    )
    procedimiento = models.ManyToManyField(Documentacion, blank=True)
    especialista = models.CharField(max_length=100, blank=True)
    proveedores = models.ManyToManyField(Proveedor, blank=True)
    herramientas = models.ManyToManyField(Herramienta, blank=True)
    cantidad_personas = models.PositiveIntegerField(default=1, blank=True)
    tiempo_realizacion_estimado = models.DurationField(blank=True, null=True)
    hora_realizacion_estimada = models.TimeField(null=True, blank=True)
    proxima_fecha = models.DateTimeField(null=True, blank=True)
    notas = RichTextMediumField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):

        # Si no existe próxima fecha, se calcula desde fechainicio
        if not self.proxima_fecha:
            base = datetime.combine(self.fechainicio, datetime.min.time())

            if self.frecuencia == "8h":
                self.proxima_fecha = base + timedelta(hours=8)
            elif self.frecuencia == "diario":
                self.proxima_fecha = base + timedelta(days=1)
            elif self.frecuencia == "semanal":
                self.proxima_fecha = base + timedelta(days=7)
            elif self.frecuencia == "mensual":
                self.proxima_fecha = base + timedelta(days=30)
            elif self.frecuencia == "bimensual":
                self.proxima_fecha = base + timedelta(days=60)
            elif self.frecuencia == "trimestral":
                self.proxima_fecha = base + timedelta(days=90)
            elif self.frecuencia == "semestral":
                self.proxima_fecha = base + timedelta(days=180)
            elif self.frecuencia == "anual":
                self.proxima_fecha = base + timedelta(days=365)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Plan de mantenimiento {self.plan.codigo_plan}"