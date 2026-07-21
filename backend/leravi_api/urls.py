from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from nucleo.serializers import CustomTokenObtainPairSerializer

# -------------------------------------------------------------------------------------
# --- INICIO DE CÓDIGO TEMPORAL (ELIMINAR DESPUÉS DE REPARAR) ---
# -------------------------------------------------------------------------------------
from django.http import HttpResponse
from django.core.management import call_command

def reparar_base_datos(request):
    try:
        # Obligamos a Django a crear sus tablas internas de sistema en Aiven
        call_command('migrate', 'sessions')
        call_command('migrate', 'admin')
        
        return HttpResponse("<h2>¡Tablas de sistema listas!</h2> <p>La tabla django_session fue creada exitosamente. Ya puedes iniciar sesión en el panel.</p>")
    except Exception as e:
        return HttpResponse(f"Fallo al crear las tablas internas: {str(e)}")
# -------------------------------------------------------------------------------------
# --- FIN DE CÓDIGO TEMPORAL ---
# -------------------------------------------------------------------------------------

# 1. Tu vista personalizada
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('nucleo.urls')), # Las rutas de tu app
    
    # ---------------------------------------------------------------------------------
    # --- RUTA TEMPORAL (ELIMINAR TAMBIÉN) ---
    path('reparar-db/', reparar_base_datos),
    # ---------------------------------------------------------------------------------
    
    # 2. La ruta apuntando a tu nueva vista personalizada
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
