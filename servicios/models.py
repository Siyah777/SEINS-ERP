from django.db import models
from core.fields import RichTextSimpleField

class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    correlativo = models.CharField(max_length=30, unique=True, blank=True, null=True)
    nombre = RichTextSimpleField(max_length=100)
    especialidad = RichTextSimpleField(max_length=100)
    descripcion = RichTextSimpleField(max_length=200)
    equipo = models.ManyToManyField('equipos.Equipo', blank=True)
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.CASCADE, blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    descripcion_unidad = models.CharField(max_length=100, default='Unidades para el precio unitario, ej. por milla')
    factura_compra = models.CharField(max_length=100, blank=True, null=True)
    fecha_compra = models.DateField(blank=True, null=True)
    notas = RichTextSimpleField(max_length=100, default='consideraciones')
    
    def save(self, *args, **kwargs):
        if not self.correlativo:
            ultimo = Servicio.objects.order_by('-id_servicio').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass
            self.correlativo = f"SV-{numero:06d}"  # SV-000001
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.correlativo} - {self.nombre}"
