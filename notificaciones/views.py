from django.shortcuts import render
from notificaciones.models import Notificacion
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def notificaciones_admin(request):
    return render(request, "admin/notificaciones.html")
