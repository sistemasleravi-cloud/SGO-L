from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from nucleo.serializers import CustomTokenObtainPairSerializer

# -------------------------------------------------------------------------------------
# --- INICIO DE CÓDIGO TEMPORAL (ELIMINAR DESPUÉS DE INICIALIZAR) ---
# -------------------------------------------------------------------------------------
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth import get_user_model

def inicializar_base_datos(request):
    try:
        # 1. Ejecutamos todas las migraciones desde cero en tu nueva BD
        call_command('migrate')
        
        # 2. Creamos tu superusuario automáticamente
        User = get_user_model()
        
        # Verificamos si el usuario ya existe para no duplicarlo
        if not User.objects.filter(username='AdminChristian').exists():
            User.objects.create_superuser(
                username='AdminChristian',
                email='admin@leravi.com',
                password='LeraviChris0611'
            )
            mensaje_usuario = "Superusuario 'AdminChristian' creado con éxito."
        else:
            mensaje_usuario = "El superusuario ya existía."

        return HttpResponse(f"<h2>¡NUEVA BASE DE DATOS LISTA!</h2> <p>Migraciones completadas impecablemente.</p> <p>{mensaje_usuario}</p>")
    except Exception as e:
        return HttpResponse(f"Error al inicializar: {str(e)}")
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
    # --- RUTA TEMPORAL (ELIMINAR DESPUÉS) ---
    path('inicializar-db/', inicializar_base_datos),
    # ---------------------------------------------------------------------------------
    
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
