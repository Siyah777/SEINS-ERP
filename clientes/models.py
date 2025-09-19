from django.db import models
from django.utils import timezone
from .utils import cargar_actividades, obtener_codigo_actividad
from django.db import transaction

DEPARTAMENTOS_CHOICES = [
    ("00", "Otros (Extranjeros)"),
    ("01", "Ahuachapán"),
    ("02", "Santa Ana"),
    ("03", "Sonsonate"),
    ("04", "Chalatenango"),
    ("05", "La Libertad"),
    ("06", "San Salvador"),
    ("07", "Cuscatlán"),
    ("08", "La Paz"),
    ("09", "Cabañas"),
    ("10", "San Vicente"),
    ("11", "Usulután"),
    ("12", "San Miguel"),
    ("13", "Morazán"),
    ("14", "La Unión"),
]

MUNICIPIOS_CHOICES = [
    ("00", "Otros (extranjeros)"),
    ("13", "Ahuachapán Norte"),
    ("01", "Ahuachapán Centro"),
    ("15", "Ahuachapán Sur"),
    ("14", "Santa Ana Norte"),
    ("02", "Santa Ana Centro"),
    ("16", "Santa Ana Este"),
    ("17", "Santa Ana Oeste"),
    ("18", "Sonsonate Norte"),
    ("03", "Sonsonate Centro"),
    ("19", "Sonsonate Este"),
    ("20", "Sonsonate Oeste"),
    ("34", "Chalatenango Norte"),
    ("04", "Chalatenango Centro"),
    ("36", "Chalatenango Sur"),
    ("23", "La Libertad Norte"),
    ("05", "La Libertad Centro"),
    ("25", "La Libertad Oeste"),
    ("26", "La Libertad Este"),
    ("27", "La Libertad Costa"),
    ("28", "La Libertad Sur"),
    ("20", "San Salvador Norte"),
    ("21", "San Salvador Oeste"),
    ("22", "San Salvador Este"),
    ("06", "San Salvador Centro"),
    ("24", "San Salvador Sur"),
    ("17", "Cuscatlán Norte"),
    ("18", "Cuscatlán Sur"),
    ("23", "La Paz Oeste"),
    ("08", "La Paz Centro"),
    ("25", "La Paz Este"),
    ("10", "Cabañas Oeste"),
    ("11", "Cabañas Este"),
    ("10", "San Vicente Norte"),
    ("15", "San Vicente Sur"),
    ("24", "Usulután Norte"),
    ("25", "Usulután Este"),
    ("26", "Usulután Oeste"),
    ("21", "San Miguel Norte"),
    ("12", "San Miguel Centro"),
    ("23", "San Miguel Oeste"),
    ("27", "Morazán Norte"),
    ("28", "Morazán Sur"),
    ("19", "La Unión Norte"),
    ("20", "La Unión Sur"),
]

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True )
    correlativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombre_empresa = models.CharField(max_length=255, unique=True)
    direccion = models.TextField()
    nit= models.CharField(max_length=20, unique=True, default='0000000000', help_text="Numero sin guiones ni espacios")
    nrc= models.CharField(max_length=20, blank=True, null=True, help_text="Numero sin guiones ni espacios")
    tipo_cliente = models.CharField(max_length=50, choices=[
        ('gobierno', 'Gobierno central'),
        ('alcaldia', 'Alcaldía'),
        ('autonoma', 'Institución autónoma'),
        ('persona_juridica', 'Persona Juridica'),
        ('persona_natural', 'Persona natural'),
        ('excluido', 'Contribuyente excluido'),
    ])
    sujeto_excluido = models.BooleanField(default=False)
    aplica_retencion = models.BooleanField(default=False)
    correo = models.CharField(max_length=100, default='ejemplo@midominio.com')
    telefono_contacto = models.CharField(max_length=15, help_text="Numero sin guiones ni espacios")
    sub_area = models.CharField(max_length=100)
    nombre_contacto = models.CharField(max_length=255)
    departamento = models.CharField(
        max_length=2,
        choices=DEPARTAMENTOS_CHOICES,
        default="06",
        verbose_name="Departamento",
        help_text="Seleccione el departamento donde se ubica el cliente"
    )
    municipio = models.CharField(
        max_length=3,
        choices=MUNICIPIOS_CHOICES,
        default="00",
        verbose_name="Municipio"
    )
    actividad_economica = models.CharField(
    max_length=200,
    choices=cargar_actividades(),  
    verbose_name="Actividad Económica",
    blank=True,
    null=True
   )
    actividad_descripcion = models.CharField(
        max_length=255, verbose_name="Descripción de la Actividad Económica", blank=True, null=True
    )
    actividad_codigo = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        verbose_name="Código de Actividad Económica"
    )
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.correlativo:
            with transaction.atomic():
                ultimo = Cliente.objects.order_by('-id_cliente').first()
                numero = 1
                if ultimo and ultimo.correlativo:
                    try:
                        numero = int(ultimo.correlativo.split('-')[-1]) + 1
                    except ValueError:
                        pass
                self.correlativo = f"C-{numero:06d}"  # C-000001
        
        actividades = dict(cargar_actividades())  # dict {codigo: descripcion}
        print(f"Buscando descripción para código: '{self.actividad_economica}'")

        descripcion = actividades.get(self.actividad_economica, "Sin especificar")
        self.actividad_codigo = self.actividad_economica or '99999'  # código guardado en el campo
        self.actividad_descripcion = descripcion

        print(f"Código asignado: {self.actividad_codigo}")
        print(f"Descripción asignada: {self.actividad_descripcion}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_empresa  

class Seguimiento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='seguimientos')
    cotizaciones = models.ForeignKey('cotizaciones.Cotizacion', on_delete=models.CASCADE, related_name='historial_cotizaciones', default=1)
    estado_cotizacion = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('aprobada', 'Aprobada'),
            ('rechazada', 'Rechazada'),
        ],
        default='pendiente'
    )
    fecha_contacto = models.DateField(default=timezone.now)
    medio_contacto = models.CharField(max_length=100, choices=[
        ('email', 'Correo electrónico'),
        ('telefono', 'Teléfono'),
        ('visita', 'Visita presencial'),
        ('otro', 'Otro'),
    ])
    asunto = models.CharField(max_length=200)
    observaciones = models.TextField(blank=True, null=True)
    proxima_accion = models.TextField(blank=True, null=True)
    fecha_proxima_contacto = models.DateField(blank=True, null=True)
    responsable = models.CharField(max_length=255)

    def __str__(self):
        return f"Seguimiento a {self.cliente} - {self.fecha_contacto}"