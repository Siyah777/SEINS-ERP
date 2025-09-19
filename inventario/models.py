from django.db import models
from productos.models import Producto  
from proveedores.models import Proveedor 

class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    consideraciones = models.TextField(blank=True, null=True)
    stock_minimo = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
