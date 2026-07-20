from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empresa, Usuario, Maquina, Bitacora, BitacoraCompletado, PrestamoHerramienta, Taller, ProductoInventario, MovimientoAlmacen

# Configuramos el administrador de usuarios para que muestre el campo 'empresa'
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Sede', {'fields': ('empresa',)}),
    )

# Registramos los modelos en el panel de control
admin.site.register(Empresa)
admin.site.register(Usuario, CustomUserAdmin)

# Registramos el resto de tus modelos operativos para que también puedas verlos ahí
admin.site.register(Maquina)
admin.site.register(Bitacora)
admin.site.register(BitacoraCompletado)
admin.site.register(PrestamoHerramienta)
admin.site.register(Taller)
admin.site.register(ProductoInventario)
admin.site.register(MovimientoAlmacen)