from django.db import models

class Producto(models.Model):
    EXISTENCIA_CHOICES = [
        ('EN STOCK', 'en stock'),
        ('SIN STOCK', 'sin stock'),
    ]
    id_producto = models.AutoField(primary_key=True)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100, unique=True, default="Nombre del Producto")
    descripcion = models.TextField(blank=True, null=True, default="Descripción del Producto")
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    serie = models.CharField(max_length=100, unique=True)
    modelo = models.CharField(max_length=100)
    existencia = models.TextField(choices=EXISTENCIA_CHOICES, default='EN STOCK')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        if not self.correlativo:
            ultimo = Producto.objects.order_by('-id_producto').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass
            self.correlativo = f"PR-{numero:06d}"  # PR-000001
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.correlativo} {self.nombre}"
