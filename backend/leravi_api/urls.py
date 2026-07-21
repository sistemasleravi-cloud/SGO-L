from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from nucleo.serializers import CustomTokenObtainPairSerializer

# -------------------------------------------------------------------------------------
# --- INICIO DE CÓDIGO TEMPORAL (ELIMINAR DESPUÉS DE REPARAR) ---
# -------------------------------------------------------------------------------------
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def reparar_base_datos(request):
    User = get_user_model()
    try:
        # Tomamos el usuario que ya existe en tu tabla (el id 1 que vimos en tu captura)
        user = User.objects.first()
        
        if user:
            # Lo actualizamos para que Django lo reconozca como administrador maestro
            user.username = 'AdminChristian'
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            
            # Encriptamos la nueva contraseña al formato que Django exige
            user.set_password('LeraviChris0611') 
            user.save()
            
            return HttpResponse("<h2>¡ÉXITO DEFINITIVO!</h2> <p>Tu usuario anterior fue ascendido. Ya puedes entrar al panel con:<br><b>Usuario:</b> AdminChristian<br><b>Contraseña:</b> LeraviChris0611</p>")
        else:
            return HttpResponse("No se encontró al usuario ID 1 para actualizar.")
            
    except Exception as e:
        return HttpResponse(f"Fallo al actualizar el usuario: {str(e)}")
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
