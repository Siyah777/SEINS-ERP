from django.db import models
from django.core.exceptions import ValidationError
import math

class Proceso(models.Model):
    nombre_del_proceso = models.CharField(max_length=200, default='nombre o descripción breve del proceso')

    # Variables
    nombre_variable_1 = models.CharField(max_length=50, default='variable 1')
    variable_entrada_1 = models.FloatField(default=0)
    unidades_variable_1 = models.CharField(max_length=25)

    nombre_variable_2 = models.CharField(max_length=50, default='variable 2', blank=True)
    variable_entrada_2 = models.FloatField(default=0, blank=True)
    unidades_variable_2 = models.CharField(max_length=25, blank=True)

    nombre_variable_3 = models.CharField(max_length=50, default='variable 3', blank=True)
    variable_entrada_3 = models.FloatField(default=0, blank=True)
    unidades_variable_3 = models.CharField(max_length=25, blank=True)

    nombre_variable_4 = models.CharField(max_length=50, default='variable 4', blank=True)
    variable_entrada_4 = models.FloatField(default=0, blank=True)
    unidades_variable_4 = models.CharField(max_length=25, blank=True)

    nombre_variable_5 = models.CharField(max_length=50, default='variable 5', blank=True)
    variable_entrada_5 = models.FloatField(default=0, blank=True)
    unidades_variable_5 = models.CharField(max_length=25, blank=True)

    nombre_variable_6 = models.CharField(max_length=50, default='variable 6', blank=True)
    variable_entrada_6 = models.FloatField(default=0, blank=True)
    unidades_variable_6 = models.CharField(max_length=25, blank=True)

    nombre_variable_7 = models.CharField(max_length=50, default='variable 7', blank=True)
    variable_entrada_7 = models.FloatField(default=0, blank=True)
    unidades_variable_7 = models.CharField(max_length=25, blank=True)

    nombre_variable_8 = models.CharField(max_length=50, default='variable 8', blank=True)
    variable_entrada_8 = models.FloatField(default=0, blank=True)
    unidades_variable_8 = models.CharField(max_length=25, blank=True)

    nombre_variable_9 = models.CharField(max_length=50, default='variable 9', blank=True)
    variable_entrada_9 = models.FloatField(default=0, blank=True)
    unidades_variable_9 = models.CharField(max_length=25, blank=True)

    nombre_variable_10 = models.CharField(max_length=50, default='variable 10', blank=True)
    variable_entrada_10 = models.FloatField(default=0, blank=True)
    unidades_variable_10 = models.CharField(max_length=25, blank=True)

    formula_proceso = models.TextField(
        help_text="Escribe una fórmula usando v1, v2, ..., v10. No uses '=' ni 'R1 ='. Solo la expresión."
    )

    nombre_resultado = models.CharField(max_length=50, blank=True)
    resultado = models.FloatField(blank=True, null=True)
    unidades_resultado = models.CharField(max_length=25, blank=True)

    def calcular_resultado(self):
        variables = {
            'v1': self.variable_entrada_1,
            'v2': self.variable_entrada_2,
            'v3': self.variable_entrada_3,
            'v4': self.variable_entrada_4,
            'v5': self.variable_entrada_5,
            'v6': self.variable_entrada_6,
            'v7': self.variable_entrada_7,
            'v8': self.variable_entrada_8,
            'v9': self.variable_entrada_9,
            'v10': self.variable_entrada_10,
        }
        try:
            result = eval(self.formula_proceso, {"__builtins__": {}, "math": math}, variables)
            return result
        except Exception as e:
            # Guardamos el error para validación
            self._formula_error = str(e)
            return None

    def clean(self):
        resultado = self.calcular_resultado()
        if resultado is None:
            raise ValidationError({
                'formula_proceso': f'La fórmula es inválida: {self._formula_error}'
            })

    def save(self, *args, **kwargs):
        resultado = self.calcular_resultado()
        if resultado is not None:
            # Redondeamos a 2 cifras significativas
            if resultado == 0:
                self.resultado = 0
            else:
                from math import log10, floor
                cifras = 2
                decimales = -int(floor(log10(abs(resultado)))) + (cifras - 1)
                self.resultado = round(resultado, decimales)
        super().save(*args, **kwargs)