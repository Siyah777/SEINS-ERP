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

def generar_pdf_factura(factura, template_name, context_extra=None):
    context = {"factura": factura}
    if context_extra:
        context.update(context_extra)
        
    template = get_template(template_name)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{factura.codigo_generacion}.pdf"'

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
    if tipo_factura == "01":  # Consumidor Final
        return 1
    elif tipo_factura in ["03", "05", "06", "04", "07", "14", "15"]:
        return 3  # o 3 si estás usando estructura 3
    else:
        return 3  # Default conservador
    
def construir_dte_json(factura):
    print("Entrando a construir_dte_json")
    logger.debug("Entrando a construir_dte_json con factura id=%s", factura.id)
    from decimal import Decimal, ROUND_HALF_UP
    from datetime import datetime
    import re
    
    version_dte = get_version_dte(factura.tipo_factura)
    correlativo = int(factura.id or 1)
    numero_control = generar_numero_control(factura.tipo_factura, correlativo)
    
    # ===================== CUERPO DOCUMENTO =====================
    cuerpo = []
    total_gravada = Decimal("0.00")
    total_iva = Decimal("0.00")
    item_num = 1

    if factura.cotizacion:
        monto = Decimal(factura.cotizacion.total)
        iva_item = (monto * Decimal("0.13")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        item = {
            "psv": 0.0,
            "noGravado": 0.0,
            "numItem": item_num,
            "codigo": factura.cotizacion.correlativo,
            "tipoItem": 2,
            "numeroDocumento": None,
            "descripcion": factura.cotizacion.Descripcion,
            "cantidad": 1,
            "codTributo": None,
            "uniMedida": 59,
            "montoDescu": 0.0,
            "ventaNoSuj": 0.0,
            "ventaExenta": 0.0,
        }
        
        if version_dte == 1:
            item["precioUni"] = round(monto + iva_item, 2)
            item["ivaItem"] = round(iva_item, 2) 
            item["tributos"] = None
            item["ventaGravada"] = float(monto + iva_item)
        elif version_dte == 3:
            item["precioUni"] = round(monto)
            item["tributos"] = ["20"]
            item["ventaGravada"] = round(monto)
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
 
    if version_dte == 1:
        receptor = {
            "tipoDocumento": "36",  # Código para consumidor final sin DUI/NIT
            "numDocumento": factura.cliente.nit or "00000000",
            "nombre": factura.cliente.nombre_empresa or "Consumidor Final",
            "nrc": factura.cliente.nrc or "00000000",
            "codActividad": factura.cliente.actividad_codigo.zfill(5) if factura.cliente.actividad_codigo else "99999",
            "descActividad": factura.cliente.actividad_economica if factura.cliente.actividad_economica else "Sin especificar",
            "telefono": factura.cliente.telefono_contacto or "00000000",
            "correo": factura.cliente.correo,
            "direccion": {
                "departamento": "06",
                "municipio": "02",
                "complemento": factura.cliente.direccion[:100] if factura.cliente.direccion else "Dirección no especificada"
            }
        }
    else:
        receptor = {
            "nombre": factura.cliente.nombre_empresa or "Consumidor Final",
            "nit": factura.cliente.nit,
            "nrc": factura.cliente.nrc,
            "nombreComercial": factura.cliente.nombre_empresa or "Consumidor Final",
            "codActividad": factura.cliente.actividad_codigo.zfill(5) if factura.cliente.actividad_codigo else "99999",
            "descActividad": factura.cliente.actividad_descripcion if factura.cliente.actividad_descripcion else "Sin especificar",
            "direccion": {
                "departamento": factura.cliente.departamento or "06",
                "municipio": factura.cliente.municipio or "02",
                "complemento": factura.cliente.direccion[:100] if factura.cliente.direccion else "Dirección no especificada"
            },
            "telefono": factura.cliente.telefono_contacto or "00000000",
            "correo": factura.cliente.correo or "correo@ejemplo.com",
        }
        

# ===================== RESUMEN =====================       
    resumen_comun = {
        "porcentajeDescuento": 0.0,
        "ivaRete1": 0.0,
        "reteRenta": 0.0,
        "totalNoGravado": 0.0,
        "totalPagar": round(total_pagar, 2),
        "condicionOperacion": 1,
        "pagos": None,
        "saldoFavor": 0.0,
        "numPagoElectronico": None,
        "totalNoSuj": 0.0,
        "totalExenta": 0.0,
        "descuNoSuj": 0.0,
        "descuExenta": 0.0,
        "descuGravada": 0.0,
        "totalDescu": 0.0,
        "montoTotalOperacion": round(total_pagar, 2),
        "totalLetras": numero_a_letras(total_pagar),
        
    }
    
    if version_dte == 1:
        resumen_comun["totalIva"] = round(iva, 2)
        resumen_comun["tributos"] = None
        resumen_comun["totalGravada"] = round(total_pagar, 2)
        resumen_comun["subTotalVentas"] = round(total_pagar, 2)
        resumen_comun["subTotal"] = round(total_pagar, 2)   
    else:
        resumen_comun["tributos"] = [{
            "codigo": "20",
            "descripcion": "Impuesto al Valor Agregado",
            "valor": round(iva, 2),
        }]
        resumen_comun["ivaPerci1"] = 0.0
        resumen_comun["totalGravada"] = round(total_gravada, 2)
        resumen_comun["subTotalVentas"] = round(total_gravada, 2)
        resumen_comun["subTotal"] = round(total_gravada, 2)   
        
    identificacion = {
        "version": get_version_dte(factura.tipo_factura),
        "ambiente": settings.AMBIENTE_DTE,  # "00" pruebas, "01" producción
        "tipoDte": factura.tipo_factura, 
        "tipoModelo": 1,
        "numeroControl": numero_control,
        "codigoGeneracion": factura.codigo_generacion,
        "fecEmi": factura.fecha_envio.strftime('%Y-%m-%d'),
        "horEmi": factura.fecha_envio.strftime('%H:%M:%S'),
        "tipoMoneda": "USD",
        "tipoOperacion": 1,
        "tipoContingencia": None,
        "motivoContin": None
    }
    
    json_dte = {
        "identificacion": identificacion,
        
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
            "placaVehiculo": None,
            "nombEntrega": None,
            "docuEntrega": None,
            "nombRecibe": None,
            "docuRecibe": None,
            "observaciones": None
        },
        "otrosDocumentos": None,
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
    
    factura.numero_control = numero_control
    factura.version_dte = factura.tipo_factura
    factura.version_json = str(version_dte)  # o '1' / '3', si lo estás diferenciando
    factura.json_dte = json_dte
    factura.fecha_envio = timezone.localtime()
    factura.iva = iva
    factura.total_letras = numero_a_letras(total_pagar)
    factura.save()

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

def firmar_dte_para_factura(factura):
    from facturacion.models import Factura
    
    url = settings.FIRMADOR_URL
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "nit": settings.FIRMADOR_NIT,
        "activo": True,
        "passwordPri": settings.FIRMADOR_PASSWORD,
        "dteJson": construir_dte_json(factura)
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Error al firmar DTE: {response.status_code} {response.text}")

    respuesta = response.json()

    if respuesta.get("estado") == "OK" or respuesta.get("status") == "OK":
        factura.firma = respuesta.get("documento_firmado") or respuesta.get("body")
        factura.respuesta_firmador = "estatus " "OK"
        factura.estado_envio_hacienda = "firmado"
        factura.fecha_envio = timezone.now()
    else:
        factura.estado_envio_hacienda = "rechazado"
        factura.respuesta_firmador = "estatus " "FAIL"
    factura.save()
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


def enviar_dte_a_hacienda(factura):
    try:
        token = obtener_token_hacienda()
    except Exception as e:
        logger.error(f"[TOKEN] Error obteniendo token: {str(e)}")
        factura.estado_envio_hacienda = "contingencia"
        factura.motivo_contingencia = "Token no disponible"
        factura.detalle_contingencia = {"error": str(e)}
        factura.save(update_fields=["estado_envio_hacienda", "motivo_contingencia", "detalle_contingencia"])
        return

    url = settings.HACIENDA_API_ENVIO_DTE
    idenvio = int(time.time())
    headers = {
        "Authorization": token,
        "User-Agent": "SEINS-ERP/1.0",
        "Content-Type": "application/json",
    }

    payload = {
        "version": get_version_dte(factura.tipo_factura),
        "ambiente": settings.AMBIENTE_DTE,
        "tipoDte": factura.tipo_factura,
        "idEnvio": idenvio,
        "codigoGeneracion": factura.codigo_generacion.upper(),
        "documento": factura.firma,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        factura.respuesta_hacienda = json.dumps(data)
        factura.fecha_envio = timezone.now()

        if data.get("estado") == "PROCESADO":
            factura.estado_envio_hacienda = "aprobado"
            factura.sello_recepcion = data.get("selloRecibido", "")
            factura.idenvio_hacienda = idenvio
        elif data.get("estado") == "RECHAZADO":
            factura.estado_envio_hacienda = "rechazado"
        else:
            factura.estado_envio_hacienda = "enviado"

        factura.save(update_fields=["estado_envio_hacienda", "respuesta_hacienda", "fecha_envio", "sello_recepcion", "idenvio_hacienda"])

    except requests.exceptions.RequestException as e:
        # Activar contingencia por error de red
        logger.error(f"[ENVIO DTE] Error de red, activando contingencia: {str(e)}")
        factura.estado_envio_hacienda = "contingencia"
        factura.motivo_contingencia = "Error de red o timeout"
        factura.tipo_contingencia = "3"
        factura.detalle_contingencia = {"error": str(e)}
        factura.save(update_fields=["estado_envio_hacienda", "motivo_contingencia", "tipo_contingencia", "detalle_contingencia"])

    except Exception as e:
        logger.exception(f"[ENVIO DTE] Error inesperado, activando contingencia: {str(e)}")
        factura.estado_envio_hacienda = "contingencia"
        factura.motivo_contingencia = "Error inesperado"
        factura.tipo_contingencia = "1"
        factura.detalle_contingencia = {"error": str(e)}
        factura.save(update_fields=["estado_envio_hacienda", "motivo_contingencia", "tipo_contingencia", "detalle_contingencia"])
        
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