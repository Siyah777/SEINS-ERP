from django.db import models
from core.utils.imagenes import ImageReduceMixin
from core.fields import RichTextSimpleField


def ruta_imagen_producto(instance, filename):
    correlativo = instance.correlativo or 'sin_correlativo'
    return f"productos/imagenes_productos/{correlativo}/imagenes/{filename}"

class Producto(ImageReduceMixin, models.Model):
    
    IMAGE_FIELDS = ("imagen_producto",)
    
    EXISTENCIA_CHOICES = [
        ('EN STOCK', 'en stock'),
        ('SIN STOCK', 'sin stock'),
    ]
    id_producto = models.AutoField(primary_key=True)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100, unique=True, default="Nombre del Producto")
    descripcion = RichTextSimpleField(blank=True, null=True, default="Descripción del Producto")
    categoria = RichTextSimpleField(max_length=100)
    equipo = models.ManyToManyField('equipos.Equipo', blank=True)
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.CASCADE, blank=True, null=True)
    marca = RichTextSimpleField(max_length=100)
    serie = RichTextSimpleField(max_length=100, unique=False)
    modelo = RichTextSimpleField(max_length=100)
    existencia = models.TextField(choices=EXISTENCIA_CHOICES, default='EN STOCK')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Colocar precios sin IVA")
    factura_compra = models.CharField(max_length=100, blank=True, null=True)
    fecha_compra = models.DateField(blank=True, null=True)
    notas = RichTextSimpleField(blank=True, null=True)
    imagen_producto = models.ImageField(upload_to=ruta_imagen_producto, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.reducir_imagenes()
        es_nuevo = self.pk is None

        # 1️⃣ Generar correlativo solo al crear
        if es_nuevo and not self.correlativo:
            ultimo = Producto.objects.order_by('-id_producto').first()
            numero = 1

            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass

            self.correlativo = f"PR-{numero:06d}"  # PR-000001

        # 2️⃣ Guardar primero
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.correlativo} {self.nombre}"

