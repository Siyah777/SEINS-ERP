from django.db import models

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
        upload_to='procedimientos/pasos/',
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

class ActividadFinal(models.Model):
    documentacion = models.ForeignKey(
        Documentacion,
        related_name='actividades_post',
        on_delete=models.CASCADE
    )

    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion[:50]


