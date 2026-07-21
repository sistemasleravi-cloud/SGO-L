from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from nucleo.serializers import CustomTokenObtainPairSerializer

# -------------------------------------------------------------------------------------
# --- INICIO DE CÓDIGO TEMPORAL (ELIMINAR DESPUÉS DE REPARAR) ---
# -------------------------------------------------------------------------------------
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth import get_user_model

def reparar_base_datos(request):
    try:
        User = get_user_model()
        with connection.schema_editor() as schema_editor:
            # 1. Creamos la tabla de relaciones de grupos (usuarios_groups)
            try:
                schema_editor.create_model(User.groups.through)
            except Exception:
                pass 
            
            # 2. Creamos la tabla de relaciones de permisos (usuarios_user_permissions)
            try:
                schema_editor.create_model(User.user_permissions.through)
            except Exception:
                pass

        return HttpResponse("<h2>¡Tablas de Permisos Listas!</h2> <p>Las tablas secundarias fueron creadas con éxito. Ya puedes guardar a tu usuario.</p>")
    except Exception as e:
        return HttpResponse(f"Fallo al crear tablas de permisos: {str(e)}")
# -------------------------------------------------------------------------------------
# --- FIN DE CÓDIGO TEMPORAL ---
# -------------------------------------------------------------------------------------

# 1. Tu vista personalizada
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('nucleo.urls')),
    
    # ---------------------------------------------------------------------------------
    # --- RUTA TEMPORAL (ELIMINAR TAMBIÉN) ---
    path('reparar-db/', reparar_base_datos),
    # ---------------------------------------------------------------------------------
    
    # 2. La ruta apuntando a tu nueva vista personalizada
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
