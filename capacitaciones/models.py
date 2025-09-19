from django.db import models

class Curso(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    proveedor = models.CharField(max_length=100, blank=True)  # Quién lo imparte
    modalidad = models.CharField(max_length=50, choices=[
        ('Presencial', 'Presencial'),
        ('Virtual', 'Virtual'),
        ('Mixto', 'Mixto'),
    ])

    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    nombre_completo = models.CharField(max_length=150)
    puesto = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nombre_completo

class Inscripcion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    class Meta:
        verbose_name = "Inscripcion"
        verbose_name_plural = "Inscripciones"

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.curso.nombre}"

class Certificado(models.Model):
    inscripcion = models.OneToOneField(Inscripcion, on_delete=models.CASCADE)
    fecha_emision = models.DateField()
    archivo_certificado = models.FileField(upload_to='certificados/', blank=True, null=True)

    def __str__(self):
        return f"Certificado de {self.inscripcion.empleado.nombre_completo} - {self.inscripcion.curso.nombre}"
