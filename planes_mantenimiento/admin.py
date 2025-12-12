from django.contrib import admin
from .models import PlanMantenimiento, DetallePlanMantenimiento
from django.utils.html import format_html
from django.urls import reverse

class DetallePlanMantenimientoInline(admin.StackedInline):
    model = DetallePlanMantenimiento
    extra = 1

@admin.action(description="Generar OTs de mantenimiento")
def generar_ots(modeladmin, request, queryset):
    from planes_mantenimiento.utils import generar_ot_desde_plan

    total = 0
    for plan in queryset:
        ot = generar_ot_desde_plan(plan)
        if ot:
            total += 1

    modeladmin.message_user(request, f"{total} OTs generadas.")

@admin.register(PlanMantenimiento)
class PlanMantenimientoAdmin(admin.ModelAdmin):
    list_display = ( 'codigo_plan', 'descripcion', 'fecha_modificacion', "btn_generar_ots",)
    search_fields = ('equipo__nombre', 'codigo_plan')
    actions = [generar_ots]
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    inlines = [DetallePlanMantenimientoInline]
    
    def btn_generar_ots(self, obj):
        return format_html(
            '<a class="button" href="{}">Generar OTs</a>',
            reverse('planes_mantenimiento:generar_ots', args=[obj.id])
        )
    btn_generar_ots.short_description = "Generar OTs"
    btn_generar_ots.allow_tags = True
    
@admin.register(DetallePlanMantenimiento)
class DetallePlanMantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'plan', 'frecuencia', 'mostrar_proveedores', 'fechainicio', 'cantidad_autogenerada')
    readonly_fields = ('proxima_fecha',)
    list_filter = ('plan', 'proveedores')
    
    def mostrar_proveedores(self, obj):
        return ", ".join(e.nombre_empresa for e in obj.proveedores.all())

    mostrar_proveedores.short_description = "proveedores"
    
    def mostrar_herramientas(self, obj):
        return ", ".join(e.nombre for e in obj.herramientas.all())

    mostrar_herramientas.short_description = "herramientas"
    search_fields = ('plan__equipo__nombre', 'actividad', 'especialista')
   
