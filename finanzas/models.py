from django.db import models
from django.utils import timezone
from facturacion.models import Factura
from proveedores.models import Proveedor


class Presupuesto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    total_ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_gastos = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def actualizar_totales(self):
        self.total_ingresos = sum(ingreso.monto for ingreso in self.ingresos.all())
        self.total_gastos = sum(gasto.monto for gasto in self.gastos.all())
        self.balance_total = self.total_ingresos - self.total_gastos
        self.save()

    def __str__(self):
        return self.nombre

class Ingreso(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='ingresos')
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.presupuesto.actualizar_totales()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.presupuesto.actualizar_totales()

    def __str__(self):
        return f"{self.nombre} - ${self.monto}"

class Gasto(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='gastos')
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.presupuesto.actualizar_totales()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.presupuesto.actualizar_totales()

    def __str__(self):
        return f"{self.nombre} - ${self.monto}"

class CuentaPorCobrar(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='cuentas_por_cobrar')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_creacion = models.DateField(default=timezone.now)
    fecha_caducidad = models.DateField()
    estatus = models.CharField(max_length=20, choices=[
        ('cobrada', 'Cobrada'),
        ('por_cobrar', 'Por cobrar'),
    ])
    observaciones = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Cuenta por Cobrar"
        verbose_name_plural = "Cuentas por Cobrar"

    def __str__(self):
        return f"Cuenta por cobrar - Factura #{self.factura.id} - {self.estatus}"

class CuentaPorPagar(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='cuentas_por_pagar')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_creacion = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    estatus = models.CharField(max_length=20, choices=[
        ('pagada', 'Pagada'),
        ('pendiente', 'Pendiente'),
    ])
    observaciones = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Cuenta por pagar"
        verbose_name_plural = "Cuentas por pagar"

    def __str__(self):
        return f"Cuenta por pagar - {self.proveedor.nombre} - {self.estatus}"


class AsientoContable(models.Model):
    fecha = models.DateField()
    descripcion = models.TextField()
    relacionado_con_pago = models.ForeignKey(CuentaPorPagar, on_delete=models.SET_NULL, null=True, blank=True)
    # ...
