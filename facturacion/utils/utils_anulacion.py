from django.conf import settings
from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import requests
from django.utils import timezone
import json
import logging
import time
import uuid
from datetime import datetime
from decimal import Decimal
from collections import OrderedDict
import qrcode
import base64


logger = logging.getLogger(__name__)

# Cache simple en RAM para el token
_token_cache = {"token": None, "expira": 0}

def generar_pdf_anulacion(Anulacion, template_name, context_extra=None):
    context = {"factura": Anulacion}
    if context_extra:
        context.update(context_extra)
        
    template = get_template(template_name)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{Anulacion.codigo_generacion}.pdf"'

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
    if tipo_factura in ["01", "03", "04", "05", "06", "07", "14", "15"]: 
        return 2
    else:
        return 2  
    
def construir_dte_json_Anulacion(Anulacion):
    print("Entrando a construir_dte_json_Anulacion")
    logger.debug("Entrando a construir_dte_json con factura id=%s", Anulacion.id)
    from decimal import Decimal, ROUND_HALF_UP
    from datetime import datetime
    import re
    
    version_dte = get_version_dte(Anulacion.tipo_factura)
    correlativo = int(Anulacion.id or 1)
    numero_control = generar_numero_control(Anulacion.tipo_factura, correlativo)
    
    # ===================== CUERPO DOCUMENTO =====================
    fecha_local = timezone.localtime(Anulacion.fecha_envio)
    
    json_dte = {
        "identificacion": {
            "version": 2,
            "ambiente": settings.AMBIENTE_DTE,
            "codigoGeneracion": Anulacion.codigo_generacion,
            "fecAnula": fecha_local.strftime('%Y-%m-%d'),
            "horAnula": fecha_local.strftime('%H:%M:%S'),
        },
        "emisor": {
            "nit": settings.EMPRESA_NIT,
            "nombre": settings.EMPRESA_NOMBRE,
            "tipoEstablecimiento": "02",
            "nomEstablecimiento": settings.EMPRESA_NOMBRE_COMERCIAL,
            "codEstableMH": settings.EMPRESA_COD_ESTABLE_MH,
            "codEstable": settings.EMPRESA_COD_ESTABLE,
            "codPuntoVentaMH": settings.EMPRESA_COD_PTO_VTA_MH,
            "codPuntoVenta": settings.EMPRESA_COD_PTO_VTA,
            "telefono": settings.EMPRESA_TELEFONO,
            "correo": settings.EMPRESA_CORREO,
        },
        "documento": {
            "tipoDte": Anulacion.factura_anular.tipo_factura,
            "codigoGeneracion": Anulacion.factura_anular.codigo_generacion,
            "selloRecibido": Anulacion.factura_anular.sello_recepcion,
            "numeroControl": Anulacion.factura_anular.numero_control,
            "fecEmi": Anulacion.factura_anular.fecha_envio.strftime('%Y-%m-%d'),
            "montoIva": Anulacion.factura_anular.iva,
            "codigoGeneracionR":  None,
            "tipoDocumento": "36",
            "numDocumento": Anulacion.factura_anular.cliente.nit or "00000000",
            "nombre": Anulacion.factura_anular.cliente.nombre_empresa or "Consumidor Final",
            "telefono": Anulacion.factura_anular.cliente.telefono_contacto or "00000000",
            "correo": Anulacion.factura_anular.cliente.correo or "00000000",
        },
        "motivo": {
            "tipoAnulacion": 2,
            "motivoAnulacion": Anulacion.motivo_anulacion or "Anulación por error en la factura",
            "nombreResponsable": Anulacion.responsable_anulacion.get_full_name() or "Responsable no especificado",
            "tipDocResponsable": "13",
            "numDocResponsable": settings.EMPRESA_NIT,
            "nombreSolicita": Anulacion.factura_anular.cliente.nombre_empresa or "Consumidor Final",
            "tipDocSolicita": "13",
            "numDocSolicita": Anulacion.factura_anular.cliente.nit or "00000000",
        }
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
    
    Anulacion.numero_control = numero_control
    Anulacion.version_dte = Anulacion.tipo_factura
    Anulacion.version_json = str(version_dte)  # o '1' / '3', si lo estás diferenciando
    Anulacion.json_dte = json_dte
    Anulacion.iva = round(Anulacion.factura_anular.iva, 2)
    Anulacion.total_letras = numero_a_letras(Anulacion.factura_anular.total_con_iva)
    Anulacion.save()

    return json_dte

def construir_json_dte_ordenado(factura):
    json_dte = OrderedDict()
    json_dte["identificacion"] = {...}
    json_dte["emisor"] = {...}
    json_dte["receptor"] = {...}
    json_dte["cuerpoDocumento"] = [...]
    json_dte["resumen"] = {...}
    json_dte["extension"] = {...}
    json_dte["apendice"] = [...]

    return json_dte

def firmar_dte_para_factura_Anulacion(Anulacion):
    from facturacion.models import Factura
    
    url = settings.FIRMADOR_URL
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "nit": settings.FIRMADOR_NIT,
        "activo": True,
        "passwordPri": settings.FIRMADOR_PASSWORD,
        "dteJson": construir_dte_json_Anulacion(Anulacion)
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Error al firmar DTE: {response.status_code} {response.text}")

    respuesta = response.json()

    if respuesta.get("estado") == "OK" or respuesta.get("status") == "OK":
        Anulacion.firma = respuesta.get("documento_firmado") or respuesta.get("body")
        Anulacion.respuesta_firmador = "estatus " "OK"
        Anulacion.estado_envio_hacienda = "firmado"
        Anulacion.fecha_envio = timezone.now()
    else:
        Anulacion.estado_envio_hacienda = "rechazado"
        Anulacion.respuesta_firmador = "estatus " "FAIL"
    Anulacion.save()
    return respuesta

def obtener_token_hacienda():
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
        _token_cache["expira"] = time.time() + 5 * 60  # 25 minutos de validez
        print("[DEBUG] Token obtenido:", token)
        return token
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] Error al obtener token: {e}")
        raise


def enviar_dte_a_hacienda_Anulacion(Anulacion):
    from ..models.models_factura import Factura
    try:
        token = obtener_token_hacienda()
    except Exception as e:
        logger.error(f"[TOKEN] Error obteniendo token: {str(e)}")
        Anulacion.estado_envio_hacienda = "rechazado"
        Anulacion.respuesta_hacienda = f"Error al obtener token: {str(e)}"
        Anulacion.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])
        return

    url = settings.HACIENDA_API_ANULACION_DTE
    idenvio = int(time.time())
    headers = {
        "Authorization": token,
        "User-Agent": "SEINS-ERP/1.0",
        "Content-Type": "application/json",
    }

    payload = {
        "version": get_version_dte(Anulacion.tipo_factura),
        "ambiente": settings.AMBIENTE_DTE,
        #"tipoDte": Anulacion.tipo_factura,
        "idEnvio": idenvio,
        "codigoGeneracion": Anulacion.codigo_generacion.upper(),
        "documento": Anulacion.firma,
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
        Anulacion.respuesta_hacienda = json.dumps(data)
        Anulacion.fecha_envio = timezone.now()

        if data.get("estado") == "PROCESADO":
            Anulacion.estado_envio_hacienda = "aprobado"
            Anulacion.sello_recepcion = data.get("selloRecibido", "")
            Anulacion.json_firmado = {
                "json_dte": Anulacion.json_dte,
                "respuesta_hacienda": Anulacion.respuesta_hacienda,
                "firma": Anulacion.firma,
            }
            Anulacion.idenvio_hacienda = idenvio
            Anulacion.save(update_fields=["json_firmado", "idenvio_hacienda"])
            
        elif data.get("estado") == "RECHAZADO":
            Anulacion.estado_envio_hacienda = "rechazado"
        else:
            Anulacion.estado_envio_hacienda = "enviado"

        Anulacion.save(update_fields=[
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
        Anulacion.estado_envio_hacienda = "rechazado"
        Anulacion.respuesta_hacienda = f"Error de red: {str(e)} | Respuesta: {response_text}"
        Anulacion.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])

    except Exception as e:
        logger.exception(f"[ENVIO DTE] Error inesperado: {str(e)}")
        Anulacion.estado_envio_hacienda = "rechazado"
        Anulacion.respuesta_hacienda = f"Error inesperado: {str(e)}"
        Anulacion.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])
        
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