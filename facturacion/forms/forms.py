from django import forms
from ..models import Factura
from cotizaciones.models import Cotizacion

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar todas las cotizaciones por defecto para evitar lista vacía al inicio
        self.fields['cotizacion'].queryset = Cotizacion.objects.all()

        if self.instance and self.instance.pk:
            cliente = self.instance.cliente
            self.fields['cotizacion'].queryset = Cotizacion.objects.filter(cliente=cliente)

