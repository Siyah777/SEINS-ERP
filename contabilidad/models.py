from django.db import models

# Asiento contable (registro en el libro diario)
class AsientoContable(models.Model):
    fecha = models.DateField()
    descripcion = models.TextField()
    creado_por = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Asiento {self.id} - {self.fecha}"
    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"

# Detalles del asiento (cuentas afectadas con debe y haber)
class DetalleAsiento(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='detalles')
    cuenta = models.CharField(max_length=100)
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.cuenta} - Debe: {self.debe} / Haber: {self.haber}"

# Declaraciones fiscales (mensuales o anuales)
class DeclaracionFiscal(models.Model):
    periodo = models.CharField(max_length=20)
    fecha_presentacion = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Declaración {self.periodo}"
    class Meta:
        verbose_name = "Declaracion fiscal"
        verbose_name_plural = "Declaraciones fiscales"

# Créditos fiscales relacionados a compras
class CreditoFiscal(models.Model):
    proveedor = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    relacionado_con = models.ForeignKey(DeclaracionFiscal, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.proveedor} - {self.monto}"
    class Meta:
        verbose_name = "Credito Fiscal"
        verbose_name_plural = "Creditos Fiscales"

# Tributos pagados (IVA, ISR, etc.)
class Tributo(models.Model):
    tipo = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField()
    relacionado_con = models.ForeignKey(DeclaracionFiscal, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.monto}"
