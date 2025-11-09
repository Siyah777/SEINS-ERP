from django.contrib import admin
from .models import Empleado, DetalleCompetenciaUsuario
import base64
from django.core.files.base import ContentFile
import os

class DetalleCompetenciaUsuarioInline(admin.StackedInline): 
    model = DetalleCompetenciaUsuario
    extra = 1

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo', 'fecha_ingreso', 'numero_dui')
    
    class Media:
        js = ('js/firma.js',)
    
    list_per_page = 20
        
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'cargo')
    list_filter = ('cargo', 'fecha_ingreso')
    
    inlines = [DetalleCompetenciaUsuarioInline]
    
    def save_model(self, request, obj, form, change):
        

        firma_data = form.cleaned_data.get('firma_tecnico')

        if firma_data and isinstance(firma_data, str):
            try:
                # Limpiar encabezado base64 si viene con 'data:image/png;base64,'
                if 'base64,' in firma_data:
                    firma_data = firma_data.split('base64,')[1]
                
                # Ruta del archivo actual (si ya existe)
                if obj.firma_tecnico_img and hasattr(obj.firma_tecnico_img, 'path'):
                    old_path = obj.firma_tecnico_img.path
                    if os.path.isfile(old_path):
                        os.remove(old_path)  # 🔹 Eliminar firma anterior

                # Guardar nueva firma (mismo nombre, sobreescribe)
                data = ContentFile(base64.b64decode(firma_data), name=f'{obj.usuario.username}_firma.png')
                obj.firma_tecnico_img.save(f'{obj.usuario.username}_firma.png', data, save=False)

            except Exception as e:
                print(f"⚠️ Error al guardar la firma: {e}")

        super().save_model(request, obj, form, change)




