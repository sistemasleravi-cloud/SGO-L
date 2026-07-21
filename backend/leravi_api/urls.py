from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from nucleo.serializers import CustomTokenObtainPairSerializer

# -------------------------------------------------------------------------------------
# --- INICIO DE CÓDIGO TEMPORAL (ELIMINAR DESPUÉS DE REPARAR) ---
# -------------------------------------------------------------------------------------
from django.http import HttpResponse
from django.core.management import call_command
from django.db import connection

def reparar_base_datos(request):
    try:
        with connection.cursor() as cursor:
            # 1. Destruimos la tabla zombi si es que se volvió a crear a medias
            cursor.execute("DROP TABLE IF EXISTS django_admin_log;")
            
            # 2. Ensanchamos el ID de tu tabla usuarios para que Django lo acepte
            cursor.execute("ALTER TABLE usuarios MODIFY id BIGINT NOT NULL AUTO_INCREMENT;")
            
        # 3. Engañamos a Django diciéndole que las tablas de 'nucleo' ya están instaladas
        call_command('migrate', 'nucleo', fake=True)
        
        # 4. Instalamos todo lo demás con los tamaños correctos
        call_command('migrate')
        
        return HttpResponse("<h2>¡VICTORIA DEFINITIVA!</h2> <p>La columna ID fue ensanchada y todas las tablas del sistema están listas. Ya puedes iniciar sesión.</p>")
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
