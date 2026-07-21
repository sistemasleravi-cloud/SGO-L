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
    User = get_user_model()
    
    # 1. Inyectamos las columnas en Aiven
    consultas = [
        "ALTER TABLE usuarios ADD COLUMN password VARCHAR(128) NOT NULL DEFAULT '';",
        "ALTER TABLE usuarios ADD COLUMN last_login DATETIME(6) NULL;",
        "ALTER TABLE usuarios ADD COLUMN is_superuser TINYINT(1) NOT NULL DEFAULT 0;",
        "ALTER TABLE usuarios ADD COLUMN is_staff TINYINT(1) NOT NULL DEFAULT 0;",
        "ALTER TABLE usuarios ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1;"
    ]
    with connection.cursor() as cursor:
        for sql in consultas:
            try:
                cursor.execute(sql)
            except Exception:
                pass # Si la columna ya existe, la ignora silenciosamente

    # 2. Creamos tu cuenta maestra
    try:
        user = User.objects.filter(username='admin_leravi').first()
        if not user:
            user = User(username='admin_leravi', is_superuser=True, is_staff=True, is_active=True)
        
        user.set_password('Sistemas2026!') 
        user.save()
        
        return HttpResponse("<h2>¡ÉXITO!</h2> <p>Base de datos lista. Ya puedes entrar con:<br><b>Usuario:</b> admin_leravi<br><b>Contraseña:</b> Sistemas2026!</p>")
    except Exception as e:
        return HttpResponse(f"Columnas inyectadas, pero el usuario falló por este motivo: {str(e)}")
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
