from django.shortcuts import get_object_or_404, redirect
from facturacion.models import Factura
from facturacion.utils import generar_pdf_factura, firmar_dte_para_factura
import os
import base64
from django.conf import settings
from django.http import JsonResponse
from facturacion.utils import firmar_dte_para_factura
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import json
from django.views import View
from collections import OrderedDict
from facturacion.utils import generar_qr_base64
from django.utils.timezone import localtime


def obtener_logo_base64():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    with open(logo_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def descargar_factura_pdf(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)

    if factura.tipo_factura == '01':
        template_path = 'factura_consumidor_final.html'
    elif factura.tipo_factura == '03':
        template_path = 'factura_credito_fiscal.html'
    else:
        return JsonResponse({'error': 'Factura no encontrada'}, status=404)
        
    logo_base64 = obtener_logo_base64()
    
    fecha_emision_str = localtime(factura.fecha_envio).date().isoformat()
    
    url_qr = f"https://admin.factura.gob.sv/consultaPublica?ambiente={settings.AMBIENTE_DTE}&codGen={factura.codigo_generacion}&fechaEmi={fecha_emision_str}"
    qr_base64 = generar_qr_base64(url_qr)

    return generar_pdf_factura(factura, template_path, context_extra={'logo_base64': logo_base64, 'qr_base64': qr_base64,})

def prueba_firma_dte(request, factura_id):
    try:
        factura = get_object_or_404(Factura, id=factura_id)
        resultado = firmar_dte_para_factura(factura)
        estado = resultado.get("estado") or resultado.get("status")
        documento = resultado.get("documento_firmado") or resultado.get("body")

        return JsonResponse({
            "estado": estado,
            "documento_firmado": documento
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def firmar_factura_admin(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    try:
        firmar_dte_para_factura(factura)
        messages.success(request, f'Factura {factura.correlativo} firmada con éxito.')
    except Exception as e:
        messages.error(request, f'Error al firmar factura: {e}')
    return redirect(f'/admin/facturacion/factura/{factura_id}/change/')

class DescargarJSONView(View):
    def get(self, request, pk):
        try:
            factura = Factura.objects.get(pk=pk)

            json_data = OrderedDict([
                ("json_dte", factura.json_dte),
                ("respuesta_hacienda", factura.respuesta_hacienda),
                ("firma", factura.firma),
            ])

            json_string = json.dumps(json_data, indent=4, ensure_ascii=False)
            response = HttpResponse(json_string, content_type='application/json')
            filename = f"{factura.codigo_generacion}.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        except Factura.DoesNotExist:
            return JsonResponse({'error': 'Factura no encontrada'}, status=404)