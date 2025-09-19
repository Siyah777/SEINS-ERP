from .models import Notificacion

#def notificaciones_context(request):
    #if request.user.is_authenticated:
        #return {
            #'notificaciones_pendientes': Notificacion.objects.filter(
                #leido=False, usuario_destino=request.user
            #).count()
       # }
    #return {'notificaciones_pendientes': 0}


def notificaciones_pendientes(request):
    if request.user.is_authenticated:
        total = Notificacion.objects.filter(leido=False).count()
        return {'notificaciones_pendientes': total}
    return {}