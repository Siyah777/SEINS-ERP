from django.db import models

class Proveedor(models.Model):
    # Definir los campos de la base de datos
    nombre_empresa = models.CharField(max_length=100)
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descripcion = models.CharField(max_length=100, default= 'descripcion de productos o servicios lo que proveen')
    nombre_contacto = models.CharField(max_length=100, default='Nombre')
    correo_electronico = models.CharField(max_length=100, default ='ejemplo@dominio.com')
    telefono = models.CharField(max_length=15, default ='+503 7777-7777')
    direccion = models.TextField()
    nit_proveedor= models.CharField(max_length=20, default='0000000000')
    nrc_proveedor= models.CharField(max_length=20, blank=True, null=True)
    tipo_proveedor = models.CharField(
        max_length=20,
        choices=[
            ('persona_natural', 'Persona Natural'),
            ('persona_juridica', 'Persona Jurídica'),
        ],
        default='persona_natural'
    ) 
    agente_retencion = models.BooleanField(default=False)
    retencion_renta = models.BooleanField(default=False)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    notas = models.CharField(max_length=100, blank=True)
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
    
    def save(self, *args, **kwargs):
        if not self.correlativo:
            ultimo = Proveedor.objects.order_by('-id').first()
            numero = 1
            if ultimo and ultimo.correlativo:
                try:
                    numero = int(ultimo.correlativo.split('-')[-1]) + 1
                except ValueError:
                    pass
            self.correlativo = f"P-{numero:06d}"  # P-000001
        super().save(*args, **kwargs)

    # Método que devuelve el nombre del proveedor en la representación en cadena
    def __str__(self):
        return self.nombre_empresa

