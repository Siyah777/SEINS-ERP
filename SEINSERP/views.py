from django.http import HttpResponse
from django.conf import settings
import os

def react_app(request):
    # Lee el contenido de index.html y devuélvelo como respuesta
    index_file = os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html')
    with open(index_file, 'r') as file:
        content = file.read()
    return HttpResponse(content)
