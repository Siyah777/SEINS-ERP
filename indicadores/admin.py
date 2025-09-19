from django.contrib import admin
from .models import Indicador

@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)

