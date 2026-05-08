from django.db import models
from productos.models import Producto  
from proveedores.models import Proveedor 
from PIL import Image
from io import BytesIO
from core.utils.imagenes import ImageReduceMixin
from core.fields import RichTextMediumField


def ruta_imagen_inventario(instance, filename):
    correlativo = instance.producto.correlativo or 'sin_correlativo'
    return f"inventario/imagenes_inventario/{correlativo}/imagenes/{filename}"

class Inventario(ImageReduceMixin, models.Model):
    
    IMAGE_FIELDS = ("imagen_inventario",)
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.TextField(max_length=1000, default='Bodega Principal')
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    consideraciones =models.TextField(blank=True, null=True)
    stock_minimo = models.PositiveIntegerField(default=0)
    imagen_inventario = models.ImageField(upload_to=ruta_imagen_inventario, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.reducir_imagenes()
        es_nuevo = self.pk is None

        # 1️⃣ Guardar primero
        super().save(*args, **kwargs)

        # 2️⃣ Procesar imagen SOLO si es nuevo
        if es_nuevo and self.imagen_inventario:
            self._reducir_imagen(self.imagen_inventario)

        
    def _reducir_imagen(self, imagen_field, max_kb=300):
        if imagen_field and hasattr(imagen_field, 'path'):
            try:
                img = Image.open(imagen_field.path)
                img_format = img.format or 'JPEG'

                # 🔹 Limitar resolución
                img.thumbnail((1920, 1920), Image.LANCZOS)

                quality = 85
                buffer = BytesIO()

                while True:
                    buffer.seek(0)
                    buffer.truncate()

                    img.save(
                        buffer,
                        format=img_format,
                        optimize=True,
                        quality=quality
                    )

                    if buffer.tell() / 1024 <= max_kb or quality <= 30:
                        break

                    quality -= 5

                with open(imagen_field.path, 'wb') as f:
                    f.write(buffer.getvalue())

            except Exception as e:
                print(f"⚠️ Error reduciendo {imagen_field.name}: {e}")

                
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
