from django.shortcuts import render
from django.http import JsonResponse
from .services import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from datetime import datetime
import base64
import os
from django.conf import settings
import json

def obtener_logo_base64():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    with open(logo_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


@staff_member_required
def dashboard(request):
    context = admin.site.each_context(request)
    return render(request, 'dashboard.html', context)


def dashboard_data(request):

    mes = request.GET.get('mes')
    anio = request.GET.get('anio')

    mes = int(mes) if mes else None
    anio = int(anio) if anio else 2026

    data = {
        "kpis": resumen_kpis(mes, anio),
        "clientes_top": clientes_top(mes, anio),
        "tipos": tipos_actividad(mes, anio),
        "costos": costos_clientes(mes, anio),
        "equipos_top": equipos_top_ots(mes, anio),
        "equipos_costos": equipos_top_costos(mes, anio),
        "comparativo": comparativo_mensual(anio),
        "tendencia": tendencia_mantenimiento(anio),
    }

    return JsonResponse(data)

@staff_member_required
def exportar_pdf(request):

    # ---------------------------------
    # RECIBIR DATOS
    # ---------------------------------
    if request.method == "POST":

        data = json.loads(request.body)

        mes = data.get("mes")
        anio = data.get("anio")

        mes = int(mes) if mes else None
        anio = int(anio) if anio else 2026

        clientes_img = data.get("clientes")
        tipos_img = data.get("tipos")
        costos_img = data.get("costos")
        equipos_img = data.get("equipos")
        equipos_costos_img = data.get("equipos_costos")
        comparativo_img = data.get("comparativo")
        tendencia_img = data.get("tendencia")

    else:

        mes = request.GET.get("mes")
        anio = request.GET.get("anio")

        mes = int(mes) if mes else None
        anio = int(anio) if anio else 2026

        clientes_img = request.GET.get("clientes")
        tipos_img = request.GET.get("tipos")
        costos_img = request.GET.get("costos")

    # ---------------------------------
    # NOMBRE MES
    # ---------------------------------
    meses = {
        1:"Enero",
        2:"Febrero",
        3:"Marzo",
        4:"Abril",
        5:"Mayo",
        6:"Junio",
        7:"Julio",
        8:"Agosto",
        9:"Septiembre",
        10:"Octubre",
        11:"Noviembre",
        12:"Diciembre"
    }

    nombre_mes = meses.get(mes, "Total")

    # ---------------------------------
    # CONTEXTO
    # ---------------------------------
    context = {
        "logo_base64": obtener_logo_base64(),
        "fecha": datetime.now(),
        "mes": nombre_mes,
        "anio": anio,

        "kpis": resumen_kpis(mes, anio),
        "clientes": clientes_top(mes, anio),
        "tipos": tipos_actividad(mes, anio),
        "costos": costos_clientes(mes, anio),
        "equipos": equipos_top_ots(mes, anio),
        "equipos_costos": equipos_top_costos(mes, anio),

        "clientes_img": clientes_img,
        "tipos_img": tipos_img,
        "costos_img": costos_img,
        "equipos_img": equipos_img,
        "equipos_costos_img": equipos_costos_img,
        "comparativo_img": comparativo_img,
        "tendencia_img": tendencia_img,
    }

    # ---------------------------------
    # GENERAR PDF
    # ---------------------------------
    template = get_template("reporte_indicadores.html")
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')

    nombre_archivo = f'Informe_{nombre_mes}_{anio}.pdf'

    response['Content-Disposition'] = (
        f'attachment; filename="{nombre_archivo}"'
    )

    pisa.CreatePDF(html, dest=response)

    return response