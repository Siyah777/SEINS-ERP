from django.db import models
from django.contrib.auth.models import User
from inventario.models import Producto 

class Notificacion(models.Model):
    nombre = models.CharField(max_length=200, blank=True)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)  
    modulo_enlace = models.URLField(max_length=500, default='https://seinsv.com/admin/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_destino = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "notificacion"
        verbose_name_plural = "notificaciones"

    def __str__(self):
        return self.mensaje
    
