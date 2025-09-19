from django.conf import settings
from django.utils import timezone
import json
import logging
import time
import requests

logger = logging.getLogger(__name__)

# Cache simple en RAM para el token
_token_cache = {"token": None, "expira": 0}


def _to_local(dt):
    """Asegura aware y convierte a tz local."""
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_default_timezone())
    return timezone.localtime(dt)


def generar_json_contingencia(contingencia):
    """
    Genera el JSON del evento de contingencia
    usando SOLO las facturas vinculadas a esta contingencia.
    """
    facturas = [f for f in contingencia.facturas_contingencia.all() if f.estado_envio_hacienda == "contingencia"]
    
    if not facturas:
        logger.info("[CONTINGENCIA] No hay facturas en estado 'contingencia'.")
        return None

    # Fechas/hora (local)
    f_inicio_dt = min(f.fecha_envio for f in facturas)
    f_inicio_local = _to_local(f_inicio_dt)
    f_fin_local = _to_local(timezone.now())

    # Valores agregados
    tipo_cont = facturas[0].tipo_contingencia or 1  # <-- corregido
    motivos = [f.motivo_contingencia for f in facturas if getattr(f, "motivo_contingencia", None)]
    motivo_cont = ", ".join(sorted(set(motivos))) or "Falla de conexión"

    # Persistimos en el objeto Contingencia
    contingencia.fecha_inicio_contingencia = f_inicio_local
    contingencia.fecha_fin_contingencia = f_fin_local
    contingencia.tipo_contingencia = tipo_cont
    contingencia.motivo_contingencia = motivo_cont
    contingencia.detalle_contingencia = [
        {
            "codigoGeneracion": f.codigo_generacion,
            "tipoDoc": f.tipo_factura,
            "fecha_envio": _to_local(f.fecha_envio).isoformat(),
        }
        for f in facturas
    ]
    contingencia.save(update_fields=[
        "fecha_inicio_contingencia",
        "fecha_fin_contingencia",
        "tipo_contingencia",
        "motivo_contingencia",
        "detalle_contingencia",
    ])

    # Detalle del lote
    detalle_dte = [
        {
            "noItem": idx + 1,
            "codigoGeneracion": f.codigo_generacion.upper(),
            "tipoDoc": f.tipo_factura,
        }
        for idx, f in enumerate(facturas)
    ]

    ahora_local = timezone.localtime()

    json_dte = {
        "identificacion": {
            "version": 3,
            "ambiente": settings.AMBIENTE_DTE,
            "codigoGeneracion": contingencia.codigo_generacion,
            "fTransmision": ahora_local.strftime("%Y-%m-%d"),
            "hTransmision": ahora_local.strftime("%H:%M:%S"),
        },
        "emisor": {
            "nit": settings.EMPRESA_NIT,
            "nombre": settings.EMPRESA_NOMBRE,
            "nombreResponsable": "Sergio Erazo",
            "tipoDocResponsable": "13",
            "numeroDocResponsable": settings.EMPRESA_NIT,
            "tipoEstablecimiento": "01",
            "codEstableMH": settings.EMPRESA_COD_ESTABLE_MH,
            "codPuntoVenta": settings.EMPRESA_COD_PTO_VTA_MH,
            "telefono": settings.EMPRESA_TELEFONO,
            "correo": settings.EMPRESA_CORREO,
        },
        "detalleDTE": detalle_dte,
        "motivo": {
            "fInicio": f_inicio_local.strftime("%Y-%m-%d"),
            "fFin": f_fin_local.strftime("%Y-%m-%d"),
            "hInicio": f_inicio_local.strftime("%H:%M:%S"),
            "hFin": f_fin_local.strftime("%H:%M:%S"),
            "tipoContingencia": tipo_cont,
            "motivoContingencia": motivo_cont,
        },
    }

    print("JSON generado:", json.dumps(json_dte, indent=2, ensure_ascii=False, default=float))
    logger.info("[CONTINGENCIA] JSON generado:\n%s", json.dumps(json_dte, indent=2, ensure_ascii=False))
    return json_dte

def firmar_contingencia(contingencia):
    """Firma la contingencia con el firmador y guarda firma/respuesta."""
    url = settings.FIRMADOR_URL
    headers = {"Content-Type": "application/json"}

    json_dte = generar_json_contingencia(contingencia)
    if not json_dte:
        logger.warning("[FIRMAR] No hay facturas para generar JSON.")
        return None

    logger.info("[FIRMAR] JSON generado para firmar:\n%s", json.dumps(json_dte, indent=2, ensure_ascii=False))

    payload = {
        "nit": settings.FIRMADOR_NIT,
        "activo": True,
        "passwordPri": settings.FIRMADOR_PASSWORD,
        "dteJson": json_dte,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        logger.info("[FIRMADOR] Status: %s | Body: %s", resp.status_code, resp.text)
        resp.raise_for_status()
        data = resp.json()

        ok = (data.get("estado") == "OK") or (data.get("status") == "OK")
        if ok:
            firma = data.get("documento_firmado") or data.get("body")
            contingencia.firma = firma
            contingencia.respuesta_firmador = "estatus " "OK"
            contingencia.estado_envio_hacienda = "firmado"
            contingencia.fecha_envio = timezone.now()
            contingencia.save()
            logger.info("[FIRMAR] Firma generada (longitud=%s).", len(firma) if firma else 0)
        else:
            contingencia.estado_envio_hacienda = "rechazado"
            contingencia.respuesta_firmador = "estatus " "FAIL"
            contingencia.save(update_fields=["estado_envio_hacienda", "respuesta_firmador"])
            logger.warning("[FIRMAR] Firmador rechazó: %s", json.dumps(data, ensure_ascii=False))
        return data

    except requests.RequestException as e:
        logger.exception("[FIRMAR] Error al firmar contingencia: %s", e)
        return None


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

def enviar_contingencia_a_hacienda(contingencia):
    try:
        token = obtener_token_hacienda()
    except Exception as e:
        logger.error(f"[TOKEN] Error obteniendo token: {str(e)}")
        contingencia.estado_envio_hacienda = "contingencia"
        contingencia.motivo_contingencia = "Token no disponible"
        contingencia.detalle_contingencia = {"error": str(e)}
        contingencia.save()
        return

    # 🔄 Refrescar de base de datos para garantizar que ya existan las facturas relacionadas
    contingencia.refresh_from_db()

    facturas_qs = contingencia.facturas_contingencia.all()
    documentos = [f.firma.strip() for f in facturas_qs if f.firma]

    if not documentos:
        logger.warning("[ENVIO DTE] No hay facturas firmadas ligadas a la contingencia; no se envía nada.")
        return

    url = settings.HACIENDA_API_CONTINGENCIA_DTE
    idenvio = int(time.time())
    headers = {
        "Authorization": token,
        "User-Agent": "SEINS-ERP/1.0",
        "Content-Type": "application/json",
    }

    payload = {
        "nit": settings.EMPRESA_NIT,
        "documento": contingencia.firma
    }
    
    print(payload)

    try:
        logger.debug(f"[ENVIO DTE] Payload generado: {json.dumps(payload, indent=2)}")

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        logger.debug(f"[ENVIO DTE] Respuesta status: {response.status_code}")
        logger.debug(f"[ENVIO DTE] Respuesta texto: {response.text}")

        response.raise_for_status()
        data = response.json()

        contingencia.respuesta_hacienda = json.dumps(data, ensure_ascii=False)
        contingencia.fecha_envio = timezone.now()
        contingencia.save()

        if data.get("estado") == "PROCESADO":
            contingencia.estado_envio_hacienda = "aprobado"
            contingencia.sello_recepcion = data.get("selloRecibido", "")
            contingencia.idenvio_hacienda = idenvio

        elif data.get("estado") == "RECHAZADO":
            contingencia.estado_envio_hacienda = "rechazado"

        else:
            contingencia.estado_envio_hacienda = "aprobado"

        contingencia.save(update_fields=["estado_envio_hacienda", "sello_recepcion", "idenvio_hacienda"])

    except requests.exceptions.RequestException as e:
        logger.error(f"[ENVIO DTE] Error de red: {str(e)}")
        contingencia.estado_envio_hacienda = "rechazado"
        contingencia.motivo_contingencia = "Error de red o timeout"
        contingencia.tipo_contingencia = "3"
        contingencia.detalle_contingencia = {"error": str(e)}
        contingencia.save()
