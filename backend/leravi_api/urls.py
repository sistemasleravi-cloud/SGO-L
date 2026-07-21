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
from django.utils import timezone

def reparar_base_datos(request):
    User = get_user_model()
    
    # 1. Inyectamos TODAS las columnas que Django exige
    consultas = [
        "ALTER TABLE usuarios ADD COLUMN password VARCHAR(128) NOT NULL DEFAULT '';",
        "ALTER TABLE usuarios ADD COLUMN last_login DATETIME(6) NULL;",
        "ALTER TABLE usuarios ADD COLUMN is_superuser TINYINT(1) NOT NULL DEFAULT 0;",
        "ALTER TABLE usuarios ADD COLUMN is_staff TINYINT(1) NOT NULL DEFAULT 0;",
        "ALTER TABLE usuarios ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1;",
        "ALTER TABLE usuarios ADD COLUMN username VARCHAR(150) NULL;",
        "ALTER TABLE usuarios ADD COLUMN first_name VARCHAR(150) NULL;",
        "ALTER TABLE usuarios ADD COLUMN last_name VARCHAR(150) NULL;",
        "ALTER TABLE usuarios ADD COLUMN email VARCHAR(254) NULL;",
        "ALTER TABLE usuarios ADD COLUMN date_joined DATETIME(6) NULL;"
    ]
    with connection.cursor() as cursor:
        for sql in consultas:
            try:
                cursor.execute(sql)
            except Exception:
                pass # Si la columna ya existe, la ignora silenciosamente

    # 2. Creamos tu cuenta maestra
    try:
        user = User.objects.filter(username='AdminChristian').first()
        if not user:
            user = User(
                username='AdminChristian', 
                is_superuser=True, 
                is_staff=True, 
                is_active=True,
                date_joined=timezone.now()
            )
        
        user.set_password('LeraviChris0611') 
        user.save()
        
        return HttpResponse("<h2>¡ÉXITO DEFINITIVO!</h2> <p>Base de datos lista. Ya puedes entrar con:<br><b>Usuario:</b> AdminChristian<br><b>Contraseña:</b> LeraviChris0611</p>")
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
