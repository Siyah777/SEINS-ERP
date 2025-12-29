from django.db import models
from PIL import Image
from io import BytesIO

class Documentacion(models.Model):
    titulo = models.CharField(max_length=255)
    codigo_documento = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)

    justificacion = models.TextField(blank=True)
    objetivos = models.TextField(blank=True)

    equipos = models.ManyToManyField('equipos.Equipo', blank=True)
    categoria = models.CharField(max_length=100)

    insumos_necesarios = models.TextField(blank=True)
    herramientas_necesarias = models.TextField(blank=True)

    personal_tecnico = models.CharField(
        max_length=255,
        help_text="Ej: 1 técnico mecánico, 1 electricista", blank=True
    )

    tiempo_estimado = models.DurationField(
        help_text="Duración estimada del procedimiento", blank=True, null=True
    )

    actividades_finales = models.TextField(default="Ninguna")
    referencias = models.TextField(blank=True, null=True)

    creado_por = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'documentacion_procedimiento'
        ordering = ['codigo_documento']
        verbose_name = "Documentacion"
        verbose_name_plural = "Documentaciones"

    def __str__(self):
        return f"{self.codigo_documento} - {self.titulo}"

class PasoProcedimiento(models.Model):
    documentacion = models.ForeignKey(
        Documentacion,
        related_name='pasos',
        on_delete=models.CASCADE
    )

    orden = models.PositiveIntegerField()
    descripcion = models.TextField()

    imagen = models.ImageField(
        upload_to='documentacion/procedimientos/pasos/',
        null=True, blank=True
    )

    video = models.URLField(
        blank=True, null=True,
        help_text="URL de video (YouTube, Drive, etc.)"
    )

    class Meta:
        ordering = ['orden']
        unique_together = ('documentacion', 'orden')

    def __str__(self):
        return f"Paso {self.orden}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guardar primero para tener path
        self._reducir_imagen(self.imagen)

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

class ActividadFinal(models.Model):
    documentacion = models.ForeignKey(
        Documentacion,
        related_name='actividades_post',
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = "Actividad final"
        verbose_name_plural = "Actividades finales"

    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion[:50]


