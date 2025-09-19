from django import forms
from .models import Cliente
from .utils import cargar_actividades

class ClienteForm(forms.ModelForm):
    actividad_economica = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['actividad_economica'].choices = cargar_actividades()

    class Meta:
        model = Cliente
        fields = '__all__'
