from django.db import models

class Analisis(models.Model):
    TIPO_ANALISIS = [
        ('CAUSA_RAIZ', 'Análisis de Causa Raíz'),
        ('MODOS_FALLO', 'Análisis de Modos de Fallo'),
        ('CICLO_VIDA', 'Análisis de Ciclo de Vida'),
        ('RIESGO', 'Análisis de Riesgo'),
        ('TENDENCIAS', 'Análisis de Tendencias'),
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPO_ANALISIS)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_analisis = models.DateTimeField()
    indicadores_incluidos = models.TextField(help_text="Indica los indicadores utilizados en el análisis")
    resultado = models.TextField(help_text="Resumen de los resultados del análisis")
    impacto_estudio = models.TextField(help_text="Impacto del análisis en la operación o producto")
    
    class Meta:
        verbose_name = "Análisis"
        verbose_name_plural = "Análisis"
        app_label = 'analisis_retroalimentacion'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_analisis}"

class Retroalimentacion(models.Model):
    analisis = models.ForeignKey(Analisis, related_name='retroalimentaciones', on_delete=models.CASCADE)
    comentario = models.TextField()
    fecha_retroalimentacion = models.DateTimeField(auto_now_add=True)
    responsabilidad = models.CharField(max_length=200)
    estado = models.CharField(max_length=50, choices=[('PENDIENTE', 'Pendiente'), ('EN_PROCESO', 'En Proceso'), ('COMPLETADO', 'Completado')], default='PENDIENTE')

    class Meta:
        verbose_name = "Retroalimentación"
        verbose_name_plural = "Retroalimentaciones"
        app_label = 'analisis_retroalimentacion'

    def __str__(self):
        return f"Retroalimentación para {self.analisis} - Estado: {self.estado}"

class PlanAccion(models.Model):
    retroalimentacion = models.ForeignKey(Retroalimentacion, related_name='acciones', on_delete=models.CASCADE)
    descripcion_accion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_limite = models.DateTimeField()
    responsable = models.CharField(max_length=200)
    estado = models.CharField(max_length=50, choices=[('PENDIENTE', 'Pendiente'), ('EN_PROCESO', 'En Proceso'), ('FINALIZADO', 'Finalizado')], default='PENDIENTE')

    class Meta:
        verbose_name = "Plan de Acción"
        verbose_name_plural = "Planes de Acción"
        app_label = 'analisis_retroalimentacion'

    def __str__(self):
        return f"Acción para {self.retroalimentacion} - Estado: {self.estado}"

