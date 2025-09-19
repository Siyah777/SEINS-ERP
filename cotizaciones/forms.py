from django import forms
from .models import Cotizacion, DetalleCotizacion

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['cliente']

class DetalleCotizacionProductoForm(forms.ModelForm):
    class Meta:
        model = DetalleCotizacionProducto
        fields = ['producto', 'cantidad', 'precio_unitario']

class DetalleCotizacionServicioForm(forms.ModelForm):
    class Meta:
        model = DetalleCotizacionServicio
        fields = ['servicio', 'cantidad', 'precio_unitario']