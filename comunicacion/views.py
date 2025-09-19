import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import MensajeContacto
from notificaciones.models import Notificacion
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
import re



@csrf_exempt
@require_POST
def enviar_mensaje_api(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

    nombre = data.get('nombre', '').strip()
    correo = data.get('correo', '').strip()
    mensaje = data.get('mensaje', '').strip()
    telefono = data.get('telefono', '').strip()  # Honeypot

    # Verificación del honeypot
    if telefono:
        return JsonResponse({'error': 'Bot detectado'}, status=400)

    # Validaciones básicas
    if not nombre or not correo or not mensaje:
        return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

    # Validación de correo (opcional)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        return JsonResponse({'error': 'Correo electrónico inválido'}, status=400)

    # Guardar mensaje en la base de datos
    try:
        nuevo_mensaje = MensajeContacto.objects.create(nombre=nombre, correo=correo, mensaje=mensaje)
    except Exception as e:
        return JsonResponse({'error': f'Error al guardar el mensaje: {str(e)}'}, status=500)

    # Crear una notificación en la base de datos (usando get_or_create para evitar duplicados)
    #notificacion_texto = f'Nuevo mensaje de contacto recibido de {nombre} ({correo})'
    notificacion_texto = f'Nuevo mensaje de contacto #{nuevo_mensaje.id} de {nombre} ({correo})'
    modulo_enlace = f"https://seinsv.com/admin/comunicacion/mensajecontacto/{nuevo_mensaje.id}/change/"
    admin_users = User.objects.filter(is_staff=True)
    
    for admin in admin_users:
        notificacion=Notificacion.objects.create(
            nombre=nombre,
            mensaje=notificacion_texto,
            modulo_enlace=modulo_enlace,
            usuario_destino=admin,
        )

    # Buscar una notificación con el mismo mensaje (debe ser único)
    #notificacion = Notificacion.objects.filter(mensaje=notificacion_texto).first()
    
    #if not notificacion:
        # Crear la notificación con el nombre y el mensaje
        #notificacion = Notificacion.objects.create(
            #nombre=nombre,
            #mensaje=notificacion_texto,
            #modulo_enlace=modulo_enlace
        #)

    # Enviar correo
    #try:
    #    send_mail(
    #        subject="Nuevo mensaje de pagina WEB de SEINS",
    #        message=f"Nombre: {nombre}\nCorreo: {correo}\n\nMensaje:\n{mensaje}",
    #        from_email=settings.DEFAULT_FROM_EMAIL,
    #        recipient_list=['sierazo7@gmail.com'],  # Cámbialo si es necesario
    #        fail_silently=False
    #   )
    #except Exception as e:
     #   return JsonResponse({'error': f'Error al enviar el correo: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Mensaje enviado correctamente'})


