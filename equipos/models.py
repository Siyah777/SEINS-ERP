from django.db import models
from proveedores.models import Proveedor
import datetime
from datetime import timedelta
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Equipo(models.Model):
    nombre = models.CharField(max_length=100, default='equipo_interno')
    descripcion = models.CharField(max_length=100, default='equipo de uso en empresa')
    marca = models.CharField(max_length=100, default='Generico')
    modelo = models.CharField(max_length=100, default='Modelo Generico')
    serie = models.CharField(max_length=100, default='Serie Generica')
    codigo_interno = models.CharField(max_length=100, default='Codigo Interno segun SG')
    estatus = models.CharField(max_length=50, default='funcionando')
    categoria = models.CharField(max_length=100, null=False, default='General')
    cantidad = models.PositiveIntegerField(default=0)
    #costo_total_acumulado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.nombre} - {self.serie}"
    
    def calcular_costo_total_mantenimientos(self):
        total = self.historial_mantenimientos.aggregate(total=Sum('costo_total'))['total']
        return total or 0

class Herramienta(models.Model):
    ESTADOS = [
        ('en_uso', 'En uso'),
        ('fuera_de_uso', 'Fuera de uso'),
        ('uso_limitado', 'Uso limitado'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    modelo = models.CharField(max_length=100, blank=True)
    serie = models.CharField(max_length=100, blank=True)
    codigo_interno = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='en_uso')
    notas = models.TextField(blank=True)

    def __str__(self):
        return self.nombre
    
class HistorialMantenimiento(models.Model):
    UNIDADES = [
        ('M', 'Millas'),
        ('Km', 'Kilometros'),
        ('Hr', 'Horas'),
        ('%', 'Porcentaje'),
    ]
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='historial_mantenimientos', default=1)
    fecha_mant = models.DateField("Fecha del Mantenimiento", default=datetime.date.today)
    descripcion_mant = models.CharField(max_length=100, default='breve descripción del mantenimiento realizado')
    mot_mant = models.CharField(max_length=100, default='debe especificar el motivo del porque se realiza el mantenimiento')
    repuestos = models.CharField(max_length=100, default='especificar los repuestos utilizados, nombre y cantidad')
    
    proveedor_mantenimiento = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='mantenimientos_realizados_equipos',
        default=1
    )
    proveedor_repuestos = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='repuestos_suministrados_equipos',
        default=1
    )

    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_repuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    indicacion_odometro = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    unidad_odometro = models.CharField(max_length=4, choices=UNIDADES, default='Km')
    tiempo_falla = models.DurationField(default=timedelta(days=1))
    tiempo_reparacion = models.DurationField(default=timedelta(days=1))
    proximo_mant = models.DateField("Fecha de Proximo Mantenimiento", default=datetime.date.today)
    notas = models.TextField(blank=True)
    usuario_asignado = models.CharField(max_length=50, default='admin')
    
    def __str__(self):
        return f"Mantenimiento de {self.equipo.nombre} en {self.fecha_mant}"
    
    def calcular_costo_total(self):
        self.costo_total = self.costo_mano_obra + self.costo_repuestos
        return self.costo_total

    def save(self, *args, **kwargs):
        # Evita errores si alguno es None
        self.costo_mano_obra = self.costo_mano_obra or 0
        self.costo_repuestos = self.costo_repuestos or 0

        # Calcula el costo total antes de guardar
        self.calcular_costo_total()
        super().save(*args, **kwargs)

        # Actualiza el costo total acumulado del equipo
        self.equipo.costo_total_acumulado = self.equipo.calcular_costo_total_mantenimientos()
        self.equipo.save()

@receiver(post_delete, sender=HistorialMantenimiento)
def actualizar_costo_total_al_borrar(sender, instance, **kwargs):
    equipo = instance.equipo
    equipo.costo_total_acumulado = equipo.calcular_costo_total_mantenimientos()
    equipo.save()
