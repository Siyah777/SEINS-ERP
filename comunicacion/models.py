from django.db import models
from clientes.models import Cliente  
from django.contrib.auth.models import User

class Comunicacion(models.Model):
    usuario_remitente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comunicaciones_enviadas',
        default=1,
    )
    usuario_destino = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comunicaciones_recibidas',
        #null=True, 
        blank=True,
        default=1,
    )
    mensaje = models.CharField(max_length=1000, default='cuerpo del mensaje')
    fecha_inicio = models.DateTimeField()
    
    class Meta:
        verbose_name = "Comunicacion Interna"
        verbose_name_plural = "Comunicaciones internas"

    def __str__(self):
        return f"Conversación entre {self.usuario_destino} y {self.usuario_remitente} el {self.fecha_inicio.strftime('%Y-%m-%d %H:%M')}"


# MODELO para el formulario público
class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self):
        return f"{self.nombre} ({self.correo}) - {self.fecha.strftime('%Y-%m-%d %H:%M')}"



