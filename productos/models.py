from django.db import models
from PIL import Image
from io import BytesIO

def ruta_imagen_producto(instance, filename):
    correlativo = instance.correlativo or 'sin_correlativo'
    return f"productos/imagenes_productos/{correlativo}/imagenes/{filename}"

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
    equipo = models.ManyToManyField('equipos.Equipo', blank=True)
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.CASCADE, blank=True, null=True)
    marca = models.CharField(max_length=100)
    serie = models.CharField(max_length=100, unique=False)
    modelo = models.CharField(max_length=100)
    existencia = models.TextField(choices=EXISTENCIA_CHOICES, default='EN STOCK')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Colocar precios sin IVA")
    factura_compra = models.CharField(max_length=100, blank=True, null=True)
    fecha_compra = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    imagen_producto = models.ImageField(upload_to=ruta_imagen_producto, null=True, blank=True)
    
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
        self._reducir_imagen(self.imagen_producto)
        super().save(*args, **kwargs)
    
    def _reducir_imagen(self, imagen_field, max_kb=300):
        if imagen_field and hasattr(imagen_field, 'path'):
            try:
                img = Image.open(imagen_field.path)
                img_format = img.format or 'JPEG'
                quality = 85
                buffer = BytesIO()
                while True:
                    buffer.seek(0)
                    buffer.truncate()
                    img.save(buffer, format=img_format, optimize=True, quality=quality)
                    size_kb = buffer.tell() / 1024
                    if size_kb <= max_kb or quality <= 30:
                        break
                    quality -= 5
                with open(imagen_field.path, 'wb') as f:
                    f.write(buffer.getvalue())
            except Exception as e:
                print(f"⚠️ Error reduciendo {imagen_field.name}: {e}")
        
    def __str__(self):
        return f"{self.correlativo} {self.nombre}"

