from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Indicador


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        return redirect('/indicadores/')