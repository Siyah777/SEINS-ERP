from django.db import models
from django.contrib.auth.models import User
from cotizaciones.models import Cotizacion
from documentacion.models import Documentacion
from proveedores.models import Proveedor
from equipos.models import Herramienta
from productos.models import Producto
from datetime import datetime

class Ordendetrabajo(models.Model):
    ESTATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('terminado', 'Terminado'),
    ]
    
    ESTATUS = [
        ('Si', 'Sí'),  
        ('No', 'No'),
    ]
    
    HORARIOS = [
        ('AM', 'Matutino 6-3'),  
        ('PM', 'Vespertino 12-9'),
        ('PM2', 'Nocturno 9-6'),
        ('8-5', 'Horario Normal 8-5'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Critica'),
    ]
    
    TIPO_ACTIVIDAD = [
        ('mantenimiento_preventivo', 'Mantenimiento Preventivo'),
        ('mantenimiento_correctivo', 'Mantenimiento Correctivo'),
        ('rutina', 'Rutina'),
        ('instalacion', 'Instalación'),
        ('desinstalacion', 'Desinstalación'),
        ('montaje', 'Montaje'),
        ('desmontaje', 'Desmontaje'),
        ('reparacion', 'Reparación'),
        ('otro', 'Otro'),
    ]
    
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    equipo_cliente = models.ForeignKey('equipos_clientes.EquipoCliente', on_delete=models.CASCADE, blank=True, null=True)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True)
    cotizacion = models.ForeignKey(Cotizacion, blank=False, on_delete=models.CASCADE, default=1)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    tipo_actividad = models.CharField(
        max_length=30,   # suficiente para el valor más largo
        choices=TIPO_ACTIVIDAD,
        default='mantenimiento_correctivo'
    )
    fecha_inicio = models.DateField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='pendiente')
    personal_asignado = models.ManyToManyField(
        User,
        blank=True,
        related_name='trabajos_asignados'
    )
    horas_hombre_estimadas = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, blank=True, null=True)
    equipo_funcionando = models.CharField(max_length=4, choices=ESTATUS, default='No')
    herramientas_necesarias = models.ManyToManyField(Herramienta, blank=True)
    horarios_actividad = models.CharField(max_length=4, choices=HORARIOS, default='8-5')
    documentos_necesarios = models.ManyToManyField(Documentacion, blank=True)
    proveedores = models.ManyToManyField(Proveedor, blank=True)
    notas = models.TextField(blank=True)
    comentarios = models.TextField(blank=True)
    class Meta:
        verbose_name = "Orden de trabajo"
        verbose_name_plural = "Órdenes de trabajo"
        
    def save(self, *args, **kwargs):
        self.cliente = self.cotizacion.cliente  # Asegura que el cliente siempre coincida con la cotización
        self.descripcion = self.cotizacion.Descripcion  # Asegura que la descripción siempre coincida con la cotización
        if not self.correlativo:
            anio = datetime.now().year % 100  # 2025 -> 25
            ultimo = Ordendetrabajo.objects.order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass
            self.correlativo = f"OT-{anio}-{numero:06d}"  # OT-25-000001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.correlativo} - {self.cliente.nombre_empresa}"


