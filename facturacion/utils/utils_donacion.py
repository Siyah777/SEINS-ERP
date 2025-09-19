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
from datetime import datetime
from decimal import Decimal
from collections import OrderedDict
import qrcode
import base64


logger = logging.getLogger(__name__)

# Cache simple en RAM para el token
_token_cache = {"token": None, "expira": 0}

def generar_pdf(ComprobanteDonacion, template_name, context_extra=None):
    context = {"factura": ComprobanteDonacion}
    if context_extra:
        context.update(context_extra)
        
    template = get_template(template_name)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{ComprobanteDonacion.codigo_generacion}.pdf"'

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
    if tipo_factura == "15":  # Donacion
        return 1
    else:
        return 1  
    
def construir_dte_json_ComprobanteDonacion(ComprobanteDonacion):
    print("Entrando a construir_dte_json_Donacion")
    logger.debug("Entrando a construir_dte_json con factura id=%s", ComprobanteDonacion.id)
    from decimal import Decimal, ROUND_HALF_UP
    from datetime import datetime
    import re
    
    version_dte = get_version_dte(ComprobanteDonacion.tipo_factura)
    correlativo = int(ComprobanteDonacion.id or 1)
    numero_control = generar_numero_control(ComprobanteDonacion.tipo_factura, correlativo)
    
    # ===================== CUERPO DOCUMENTO =====================
    cuerpo = []
    total_gravada = Decimal("0.00")
    total_iva = Decimal("0.00")
    item_num = 1

    #if ComprobanteRetencion.cotizacion:
    monto = Decimal(ComprobanteDonacion.monto)
    iva_item = (monto * Decimal("0.13")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    item = {
        "tipoDonacion": 1,
        "cantidad": 1,
        "valorUni": round(monto, 2),
        "valor": round(monto, 2),
        "depreciacion": 0.0,
        "numItem": item_num,
        "codigo": ComprobanteDonacion.correlativo,
        "descripcion": ComprobanteDonacion.descripcion_donacion,
        "uniMedida": 99,

    }
    
    cuerpo.append(item)
    total_gravada += monto
    total_iva += iva_item 
    item_num += 1
            
    # 🛑 Validación para evitar DTE sin líneas
    if not cuerpo:
        raise ValueError("La factura no contiene cotizaciones. No se puede generar un DTE vacío.")

    # ✅ Ahora sí se puede calcular IVA y total a pagar
    if version_dte == 1:
     iva = (total_iva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
     iva = (total_gravada * Decimal("0.13")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    total_pagar = round(total_gravada + iva, 2)
 
    #if version_dte == 1:
    donatario = {
        "tipoDocumento": "36",  
        "tipoEstablecimiento": "02",
        "codEstableMH": "S001",
        "codEstable": "0001",
        "codPuntoVentaMH": "P001",
        "codPuntoVenta": "001",
        "numDocumento": settings.EMPRESA_NIT, 
        "nombre": settings.EMPRESA_NOMBRE, 
        "nrc": settings.EMPRESA_NRC, #
        "nombreComercial": settings.EMPRESA_NOMBRE_COMERCIAL, 
        "codActividad": settings.EMPRESA_ACTIVIDAD_COD,
        "descActividad": settings.EMPRESA_ACTIVIDAD_DESC, 
        "telefono": settings.EMPRESA_TELEFONO, 
        "correo": settings.EMPRESA_CORREO, 
        "direccion": {
            "departamento": settings.EMPRESA_DEPARTAMENTO, #"06",
            "municipio": settings.EMPRESA_MUNICIPIO, #"02",
            "complemento": settings.EMPRESA_COMPLEMENTO, 
        }
    }
  
# ===================== RESUMEN =====================       
    resumen_comun = {
    
        "pagos": [
            {
                "codigo": "01",
                "montoPago": round(ComprobanteDonacion.monto, 2),
                "referencia": None,
            }
        ], 
        "valorTotal" : round(ComprobanteDonacion.monto, 2),
        "totalLetras": numero_a_letras(ComprobanteDonacion.monto),
        
    }
    
    json_dte = {
        "identificacion": {
            "version": get_version_dte(ComprobanteDonacion.tipo_factura),
            "ambiente": settings.AMBIENTE_DTE,  # "00" pruebas, "01" producción
            "tipoDte": ComprobanteDonacion.tipo_factura, 
            "numeroControl": numero_control,
            "codigoGeneracion": ComprobanteDonacion.codigo_generacion,
            "tipoModelo": 1,
            "tipoOperacion": 1,
            "fecEmi": ComprobanteDonacion.fecha_envio.strftime('%Y-%m-%d'),
            "horEmi": ComprobanteDonacion.fecha_envio.strftime('%H:%M:%S'),
            "tipoMoneda": "USD",
        },

        "donante": {
            "numDocumento": ComprobanteDonacion.donatario.nit or "00000000", #
            "tipoDocumento": "36",  # 36=NIT
            "nrc": ComprobanteDonacion.donatario.nrc or "00000000", 
            "nombre": ComprobanteDonacion.donatario.nombre_empresa or "Consumidor Final", 
            "codActividad": ComprobanteDonacion.donatario.actividad_codigo.zfill(5) if ComprobanteDonacion.donatario.actividad_codigo else "99999", 
            "descActividad": ComprobanteDonacion.donatario.actividad_economica if ComprobanteDonacion.donatario.actividad_economica else "Sin especificar", 
            "codDomiciliado": 1,
            "codPais": "SV",
            "direccion": {
                "departamento": "06", 
                "municipio": "02", 
                "complemento": ComprobanteDonacion.donatario.direccion[:100] if ComprobanteDonacion.donatario.direccion else "Dirección no especificada" 
            },
            "telefono": ComprobanteDonacion.donatario.telefono_contacto or "00000000", 
            "correo": ComprobanteDonacion.donatario.correo, 
        },
        "donatario": donatario,
        "cuerpoDocumento": cuerpo,  # <-- Generado previamente
        "resumen": resumen_comun,  # <-- Resumen de totales
        "otrosDocumentos": [
            {
                "codDocAsociado": 2,
                "descDocumento" : "Documento DOC-0001",
                "detalleDocumento": "Documento donde se detalla la donación",
            }
        ],
    
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
    
    ComprobanteDonacion.numero_control = numero_control
    ComprobanteDonacion.version_dte = ComprobanteDonacion.tipo_factura
    ComprobanteDonacion.version_json = str(version_dte)  # o '1' / '3', si lo estás diferenciando
    ComprobanteDonacion.json_dte = json_dte
    ComprobanteDonacion.fecha_envio = timezone.localtime()
    ComprobanteDonacion.iva = iva
    ComprobanteDonacion.total_letras = numero_a_letras(total_pagar)
    ComprobanteDonacion.save()
    return json_dte

def construir_json_dte_ordenado(ComprobanteRetencion):
    json_dte = OrderedDict()
    json_dte["identificacion"] = {...}
    json_dte["emisor"] = {...}
    json_dte["receptor"] = {...}
    json_dte["cuerpoDocumento"] = [...]
    json_dte["resumen"] = {...}
    json_dte["extension"] = {...}
    json_dte["apendice"] = [...]

    return json_dte

def firmar_dte_para_factura_otros(ComprobanteDonacion):
    
    url = settings.FIRMADOR_URL
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "nit": settings.FIRMADOR_NIT,
        "activo": True,
        "passwordPri": settings.FIRMADOR_PASSWORD,
        "dteJson": construir_dte_json_ComprobanteDonacion(ComprobanteDonacion)
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Error al firmar DTE: {response.status_code} {response.text}")

    respuesta = response.json()

    if respuesta.get("estado") == "OK" or respuesta.get("status") == "OK":
        ComprobanteDonacion.firma = respuesta.get("documento_firmado") or respuesta.get("body")
        ComprobanteDonacion.respuesta_firmador = "estatus " "OK"
        ComprobanteDonacion.estado_envio_hacienda = "firmado"
        ComprobanteDonacion.fecha_envio = timezone.now()
    else:
        ComprobanteDonacion.estado_envio_hacienda = "rechazado"
        ComprobanteDonacion.respuesta_firmador = "estatus " "FAIL"
    ComprobanteDonacion.save()
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
        _token_cache["expira"] = time.time() + 23 * 3600  # 23 horas de validez
        print("[DEBUG] Token obtenido:", token)
        return token
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] Error al obtener token: {e}")
        raise


def enviar_dte_a_hacienda_otros(ComprobanteDonacion):
    try:
        token = obtener_token_hacienda()
    except Exception as e:
        logger.error(f"[TOKEN] Error obteniendo token: {str(e)}")
        ComprobanteDonacion.estado_envio_hacienda = "rechazado"
        ComprobanteDonacion.respuesta_hacienda = f"Error al obtener token: {str(e)}"
        ComprobanteDonacion.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])
        return

    url = settings.HACIENDA_API_ENVIO_DTE
    idenvio = int(time.time())
    headers = {
        "Authorization": token,
        "User-Agent": "SEINS-ERP/1.0",
        "Content-Type": "application/json",
    }

    payload = {
        "version": get_version_dte(ComprobanteDonacion.tipo_factura),
        "ambiente": settings.AMBIENTE_DTE,
        "tipoDte": ComprobanteDonacion.tipo_factura,
        "idEnvio": idenvio,
        "codigoGeneracion": ComprobanteDonacion.codigo_generacion.upper(),
        "documento": ComprobanteDonacion.firma,
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
        ComprobanteDonacion.respuesta_hacienda = json.dumps(data)
        ComprobanteDonacion.fecha_envio = timezone.now()

        if data.get("estado") == "PROCESADO":
            ComprobanteDonacion.estado_envio_hacienda = "aprobado"
            ComprobanteDonacion.sello_recepcion = data.get("selloRecibido", "")
            ComprobanteDonacion.json_firmado = {
                "json_dte": ComprobanteDonacion.json_dte,
                "respuesta_hacienda": ComprobanteDonacion.respuesta_hacienda,
                "firma": ComprobanteDonacion.firma,
            }
            ComprobanteDonacion.idenvio_hacienda = idenvio
            ComprobanteDonacion.save(update_fields=["json_firmado", "idenvio_hacienda"])
            
        elif data.get("estado") == "RECHAZADO":
            ComprobanteDonacion.estado_envio_hacienda = "rechazado"
        else:
            ComprobanteDonacion.estado_envio_hacienda = "enviado"

        ComprobanteDonacion.save(update_fields=[
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
        ComprobanteDonacion.estado_envio_hacienda = "rechazado"
        ComprobanteDonacion.respuesta_hacienda = f"Error de red: {str(e)} | Respuesta: {response_text}"
        ComprobanteDonacion.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])

    except Exception as e:
        logger.exception(f"[ENVIO DTE] Error inesperado: {str(e)}")
        ComprobanteDonacion.estado_envio_hacienda = "rechazado"
        ComprobanteDonacion.respuesta_hacienda = f"Error inesperado: {str(e)}"
        ComprobanteDonacion.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda"])
        
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