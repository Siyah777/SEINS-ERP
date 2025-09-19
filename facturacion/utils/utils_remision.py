from django.conf import settings
import json
from collections import OrderedDict
from django.db import models
from xhtml2pdf import pisa
import logging
from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO
from django.utils import timezone
import requests
import time
import qrcode
import base64

logger = logging.getLogger(__name__)

# Cache simple en RAM para el token
_token_cache = {"token": None, "expira": 0}

def generar_pdf(NotaRemision, template_name, context_extra=None):
    context = {"Nota de Credito/Debito": NotaRemision}
    if context_extra:
        context.update(context_extra)
        
    template = get_template(template_name)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{NotaRemision.codigo_generacion}.pdf"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response)

    if pisa_status.err:
        return HttpResponse("Error generando el PDF", status=500)
    return response

def numero_a_letras(numero):
    from num2words import num2words
    try:
        parte_entera = int(numero)
        parte_decimal = int(round((numero - parte_entera) * 100))
        texto = f"{num2words(parte_entera, lang='es').capitalize()} dólares"
        if parte_decimal > 0:
            texto += f" con {parte_decimal:02d}/100"
        else:
            texto += " con 00/100"
        return texto
    except Exception:
        return "Cero dólares con 00/100"
    
def generar_numero_control(tipo_dte: str, correlativo: int) -> str:
    from django.conf import settings

    # Obtener códigos y aplicar padding si hace falta
    cod_estable_mh = settings.EMPRESA_COD_ESTABLE_MH.zfill(4)[:4]  # ej: "S001"
    cod_punto_venta_mh = settings.EMPRESA_COD_PTO_VTA_MH.zfill(4)[:4]  # ej: "P001"

    # Forzar correlativo de 15 dígitos con ceros a la izquierda
    correlativo_str = f"{correlativo:015d}"

    # Construcción del número de control
    numero_control = f"DTE-{tipo_dte}-{cod_estable_mh}{cod_punto_venta_mh}-{correlativo_str}"

    # Validación final
    if len(numero_control) != 31:
        raise ValueError(f"[ERROR] numeroControl mal formado: '{numero_control}' (long: {len(numero_control)}). Esperado: 36 caracteres.")

    return numero_control

def get_version_dte(tipo_factura):
    if tipo_factura == "04":  
        return 3
    else:
        return 3
 
# ======================================= JSON PARA NOTAS DE REMISION ====================================
   
def construir_dte_json_notaremision(NotaRemision):

    print("Entrando a construir_dte_json_NR ")
    logger.debug("Entrando a construir_dte_json_NR con factura id=%s", NotaRemision.id)
    from decimal import Decimal, ROUND_HALF_UP
    from datetime import datetime
    import re
    
    version_dte = get_version_dte(NotaRemision.tipo_factura)
    correlativo = int(NotaRemision.id or 1)
    numero_control = generar_numero_control(NotaRemision.tipo_factura, correlativo)
    
    # ===================== CUERPO DOCUMENTO =====================
    cuerpo = []
    iva = (Decimal(NotaRemision.factura_entrega.total_sin_iva) * Decimal('0.13')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    item = {
        "numItem": 1,
        "codigo": NotaRemision.correlativo,
        "tipoItem": 2,
        "numeroDocumento": None, 
        "descripcion": NotaRemision.direccion_entrega or "Sin descripción",
        "precioUni": round(NotaRemision.factura_entrega.total_sin_iva, 2),
        "cantidad": 1,
        "ventaGravada": round(NotaRemision.factura_entrega.total_sin_iva, 2),
        "codTributo": None,
        "uniMedida": 59,
        "montoDescu": 0.0,
        "ventaNoSuj": 0.0,
        "ventaExenta": 0.0,
    }
    
    if version_dte == 1:
        item["tributos"] = None
    elif version_dte == 3:
        item["tributos"] = ["20"]
    cuerpo.append(item)
        
    receptor = {
        "tipoDocumento": "36",  # NIT
        "numDocumento": NotaRemision.cliente.nit or "000000000",
        "bienTitulo": "01",
        "nombre": NotaRemision.cliente.nombre_empresa or "Consumidor Final",
        "nrc": NotaRemision.cliente.nrc or "00000000",
        "nombreComercial": NotaRemision.cliente.nombre_empresa or "Consumidor Final",
        "codActividad": NotaRemision.cliente.actividad_codigo.zfill(5) if NotaRemision.cliente.actividad_codigo else "99999",
        "descActividad": NotaRemision.cliente.actividad_descripcion if NotaRemision.cliente.actividad_descripcion else "Sin especificar",
        "direccion": {
            "departamento": NotaRemision.cliente.departamento or "06",
            "municipio": NotaRemision.cliente.municipio or "02",
            "complemento": NotaRemision.cliente.direccion[:100] if NotaRemision.cliente.direccion else "Dirección no especificada"
        },
        "telefono": NotaRemision.cliente.telefono_contacto or "00000000",
        "correo": NotaRemision.cliente.correo or "correo@ejemplo.com",
    }
        

# ===================== RESUMEN =====================       
    resumen_comun = {
        "porcentajeDescuento": 0.0,
        "totalNoSuj": 0.0,
        "totalExenta": 0.0,
        "descuNoSuj": 0.0,
        "descuExenta": 0.0,
        "descuGravada": 0.0,
        "totalDescu": 0.0,
        "montoTotalOperacion": round(NotaRemision.monto, 2),
        "totalLetras": numero_a_letras(NotaRemision.monto),
        
    }
    

    resumen_comun["tributos"] = [{
        "codigo": "20",
        "descripcion": "Impuesto al Valor Agregado",
        "valor": round(iva, 2),
    }]
    resumen_comun["totalGravada"] = round(NotaRemision.factura_entrega.total_sin_iva, 2)
    resumen_comun["subTotalVentas"] = round(NotaRemision.factura_entrega.total_sin_iva, 2)
    resumen_comun["subTotal"] = round(NotaRemision.factura_entrega.total_sin_iva, 2)  

    json_dte = {
        "identificacion": {
            "version": get_version_dte(NotaRemision.tipo_factura),
            "ambiente": settings.AMBIENTE_DTE,  # "00" pruebas, "01" producción
            "tipoDte": NotaRemision.tipo_factura, 
            "numeroControl": numero_control,
            "codigoGeneracion": NotaRemision.codigo_generacion,
            "tipoModelo": 1,
            "tipoOperacion": 1,
            "fecEmi": NotaRemision.fecha_envio.strftime('%Y-%m-%d'),
            "horEmi": NotaRemision.fecha_envio.strftime('%H:%M:%S'),
            "tipoMoneda": "USD",
            "tipoContingencia": None,
            "motivoContin": None
        },
        
        "documentoRelacionado": None, 
           
        "emisor": {
            "tipoEstablecimiento": "02",
            "nombreComercial": settings.EMPRESA_NOMBRE_COMERCIAL,
            "codEstableMH": settings.EMPRESA_COD_ESTABLE_MH,
            "codEstable": settings.EMPRESA_COD_ESTABLE,
            "codPuntoVentaMH": settings.EMPRESA_COD_PTO_VTA_MH,
            "codPuntoVenta": settings.EMPRESA_COD_PTO_VTA,
            "nit": settings.EMPRESA_NIT,
            "nrc": settings.EMPRESA_NRC,
            "nombre": settings.EMPRESA_NOMBRE,
            "codActividad": settings.EMPRESA_ACTIVIDAD_COD,
            "descActividad": settings.EMPRESA_ACTIVIDAD_DESC,
            "direccion": {
                "departamento": settings.EMPRESA_DEPARTAMENTO,
                "municipio": settings.EMPRESA_MUNICIPIO,
                "complemento": settings.EMPRESA_COMPLEMENTO
            },
            "telefono": settings.EMPRESA_TELEFONO,
            "correo": settings.EMPRESA_CORREO,
        },
        "receptor": receptor,
        "cuerpoDocumento": cuerpo,  # <-- Generado previamente
        "resumen": resumen_comun,  # <-- Resumen de totales
        "extension": {
            "nombEntrega": None,
            "docuEntrega": None,
            "nombRecibe": None,
            "docuRecibe": None,
            "observaciones": None
        },
        "ventaTercero": None,
        "apendice": [
            {
            "campo": "OrdenCompra",
            "etiqueta": "Número Orden de compra:",
            "valor": "0"
            }
        ],
    }

    logger.debug("JSON generado para DTE:\n%s", json.dumps(json_dte, indent=2, ensure_ascii=False, default=float))
    print("JSON generado:", json.dumps(json_dte, indent=2, ensure_ascii=False, default=float))
    
    def convertir_decimales(obj):
        if isinstance(obj, dict):
            return {k: convertir_decimales(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convertir_decimales(elem) for elem in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj

    json_dte = convertir_decimales(json_dte)
    total_pagar = Decimal(NotaRemision.monto).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    NotaRemision.numero_control = numero_control
    NotaRemision.version_dte = NotaRemision.tipo_factura
    NotaRemision.version_json = str(version_dte)  # o '1' / '3', si lo estás diferenciando
    NotaRemision.json_dte = json_dte
    NotaRemision.fecha_envio = timezone.localtime()
    NotaRemision.total_letras = numero_a_letras(NotaRemision.monto)
    NotaRemision.save()

    return json_dte

def construir_json_dte_ordenado(NotaRemision):
    json_dte = OrderedDict()
    json_dte["identificacion"] = {...}
    json_dte["emisor"] = {...}
    json_dte["receptor"] = {...}
    json_dte["cuerpoDocumento"] = [...]
    json_dte["resumen"] = {...}
    json_dte["extension"] = {...}
    json_dte["apendice"] = [...]

    return json_dte

def firmar_dte_para_factura_otros(NotaRemision):
    url = settings.FIRMADOR_URL
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "nit": settings.FIRMADOR_NIT,
        "activo": True,
        "passwordPri": settings.FIRMADOR_PASSWORD,
        "dteJson": construir_dte_json_notaremision(NotaRemision)
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Error al firmar DTE: {response.status_code} {response.text}")

    respuesta = response.json()

    if respuesta.get("estado") == "OK" or respuesta.get("status") == "OK":
        NotaRemision.firma = respuesta.get("documento_firmado") or respuesta.get("body")
        NotaRemision.respuesta_firmador = "estatus " "OK"
        NotaRemision.estado_envio_hacienda = "firmado"
        NotaRemision.fecha_envio = timezone.now()
    else:
        NotaRemision.estado_envio_hacienda = "rechazado"
        NotaRemision.respuesta_firmador = "estatus " "FAIL"
    NotaRemision.save()
    return respuesta

def obtener_token_hacienda_otros():
    if _token_cache.get("token") and _token_cache.get("expira", 0) > time.time():
        return _token_cache["token"]

    url = settings.HACIENDA_API_TOKEN_URL
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "SEINS-ERP"
    }
    data = {
        "user": settings.HACIENDA_USER,
        "pwd": settings.HACIENDA_PASSWORD
    }

    try:
        response = requests.post(url, headers=headers, data=requests.compat.urlencode(data))
        print("[DEBUG] Respuesta status:", response.status_code)
        print("[DEBUG] Respuesta texto:", response.text)
        response.raise_for_status()
        token_data = response.json()
        print("[DEBUG] Token data:", token_data)
        token = token_data['body']['token']
        _token_cache["token"] = token
        _token_cache["expira"] = time.time() + 23 * 3600  # 23 horas de validez
        print("[DEBUG] Token obtenido:", token)
        return token
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] Error al obtener token: {e}")
        raise


def enviar_dte_a_hacienda_otros(NotaRemision):
    try:
        token = obtener_token_hacienda_otros()
    except Exception as e:
        logger.error(f"[TOKEN] Error obteniendo token: {str(e)}")
        NotaRemision.estado_envio_hacienda = "rechazado"
        NotaRemision.respuesta_hacienda = f"Error al obtener token: {str(e)}"
        NotaRemision.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])
        return

    url = settings.HACIENDA_API_ENVIO_DTE
    idenvio = int(time.time())
    headers = {
        "Authorization": token,
        "User-Agent": "SEINS-ERP/1.0",
        "Content-Type": "application/json",
    }

    payload = {
        "version": get_version_dte(NotaRemision.tipo_factura),
        "ambiente": settings.AMBIENTE_DTE,
        "tipoDte": NotaRemision.tipo_factura,
        "idEnvio": idenvio,
        "codigoGeneracion": NotaRemision.codigo_generacion.upper(),
        "documento": NotaRemision.firma,
    }

    try:
        # Mostrar headers y payload antes de enviar
        logger.debug(f"[DEBUG][HEADERS HACIENDA] Headers usados:\n{json.dumps(headers, indent=2)}")
        logger.debug(f"[DEBUG][PAYLOAD HACIENDA] Payload enviado:\n{json.dumps(payload, indent=2)}")

        print("[DEBUG][HEADERS HACIENDA]:", json.dumps(headers, indent=2))
        print("[DEBUG][PAYLOAD HACIENDA]:", json.dumps(payload, indent=2))

        # Enviar petición
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        logger.debug(f"[ENVIO DTE] Respuesta exitosa:\n{json.dumps(data, indent=2)}")
        NotaRemision.respuesta_hacienda = json.dumps(data)
        NotaRemision.fecha_envio = timezone.now()

        if data.get("estado") == "PROCESADO":
            NotaRemision.estado_envio_hacienda = "aprobado"
            NotaRemision.sello_recepcion = data.get("selloRecibido", "")
            NotaRemision.json_firmado = {
                "json_dte": NotaRemision.json_dte,
                "respuesta_hacienda": NotaRemision.respuesta_hacienda,
                "firma": NotaRemision.firma,
            }
            NotaRemision.idenvio_hacienda = idenvio
            NotaRemision.save(update_fields=["json_firmado", "idenvio_hacienda"])
            
        elif data.get("estado") == "RECHAZADO":
            NotaRemision.estado_envio_hacienda = "rechazado"
        else:
            NotaRemision.estado_envio_hacienda = "enviado"

        NotaRemision.save(update_fields=[
            "estado_envio_hacienda", "respuesta_hacienda", "fecha_envio", "sello_recepcion"
        ])

    except requests.exceptions.RequestException as e:
        response_text = ""
        if hasattr(e, 'response') and e.response is not None:
            try:
                response_text = e.response.text
                logger.debug(f"[ERROR 400 HACIENDA] Respuesta:\n{response_text}")
            except Exception:
                response_text = "No se pudo leer la respuesta de error."

        logger.error(f"[ENVIO DTE] Error al enviar DTE: {str(e)} | Respuesta: {response_text}")
        NotaRemision.estado_envio_hacienda = "rechazado"
        NotaRemision.respuesta_hacienda = f"Error de red: {str(e)} | Respuesta: {response_text}"
        NotaRemision.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])

    except Exception as e:
        logger.exception(f"[ENVIO DTE] Error inesperado: {str(e)}")
        NotaRemision.estado_envio_hacienda = "rechazado"
        NotaRemision.respuesta_hacienda = f"Error inesperado: {str(e)}"
        NotaRemision.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])
        
def generar_qr_base64(url_qr):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url_qr)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()
