from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from nucleo.serializers import CustomTokenObtainPairSerializer

# -------------------------------------------------------------------------------------
# --- INICIO DE CÓDIGO TEMPORAL (ELIMINAR DESPUÉS DE REPARAR) ---
# -------------------------------------------------------------------------------------
from django.http import HttpResponse
from django.db import connection

def reparar_base_datos(request):
    try:
        with connection.cursor() as cursor:
            # Hacemos que la columna antigua 'password_hash' sea opcional permitiendo NULL
            cursor.execute("ALTER TABLE usuarios MODIFY password_hash VARCHAR(255) NULL;")
            
        return HttpResponse("<h2>¡ÚLTIMO FANTASMA ELIMINADO!</h2> <p>La columna password_hash ya no es obligatoria. Intenta agregar el usuario nuevamente.</p>")
    except Exception as e:
        return HttpResponse(f"Fallo en la base de datos: {str(e)}")
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
