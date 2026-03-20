from django.db import models
from core.utils.imagenes import ImageReduceMixin
from core.fields import RichTextMediumField


class Documentacion(models.Model):
    titulo = models.TextField(max_length=255)
    codigo_documento = models.TextField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)

    justificacion = RichTextMediumField(blank=True)
    objetivos = RichTextMediumField(blank=True)

    equipos = models.ManyToManyField('equipos.Equipo', blank=True)
    categoria = RichTextMediumField(max_length=100)

    insumos_necesarios = RichTextMediumField(blank=True)
    herramientas_necesarias = RichTextMediumField(blank=True)

    personal_tecnico = RichTextMediumField(
        max_length=255,
        help_text="Ej: 1 técnico mecánico, 1 electricista", blank=True
    )

    tiempo_estimado = models.DurationField(
        help_text="Duración estimada del procedimiento", blank=True, null=True
    )

    actividades_finales = RichTextMediumField(default="Ninguna")
    referencias = RichTextMediumField(blank=True, null=True)

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

class PasoProcedimiento(ImageReduceMixin, models.Model):
    
    IMAGE_FIELDS = ("imagen",)
    
    documentacion = models.ForeignKey(
        Documentacion,
        related_name='pasos',
        on_delete=models.CASCADE
    )

    orden = models.PositiveIntegerField()
    descripcion = RichTextMediumField()

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
        self.reducir_imagenes()
        super().save(*args, **kwargs)  # Guardar primero para tener path
        
class ActividadFinal(models.Model):
    documentacion = models.ForeignKey(
        Documentacion,
        related_name='actividades_post',
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = "Actividad final"
        verbose_name_plural = "Actividades finales"

    descripcion = RichTextMediumField()

    def __str__(self):
        return self.descripcion[:50]


