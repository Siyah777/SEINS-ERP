from django.db import models
from proveedores.models import Proveedor

class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descripcion = models.TextField()
    cantidad = models.PositiveIntegerField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_ingreso = models.DateField()
    fecha_aprobacion = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.correlativo:
            ultimo = Compra.objects.order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass
            self.correlativo = f"COM-{numero:06d}"  # COM-000001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra a {self.proveedor.nombre_empresa} - {self.descripcion[:30]}"

