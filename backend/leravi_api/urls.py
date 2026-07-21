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
    
    # 1. Obtenemos el ID de Cananea buscando a Lalo (o cualquier usuario que ya tenga empresa)
    usuario = User.objects.filter(empresa_id__isnull=False).first()
    empresa_id = usuario.empresa_id if usuario else 1

    # 2. Lista de todas tus tablas operativas probables
    tablas_operativas = [
        'taller', 'maquinas', 'bitacora', 
        'bitacora_completados', 'completados',
        'herramientas', 'prestamo_herramientas',
        'almacen_inventario', 'almacen_movimientos'
    ]
    
    exitos = []
    
    with connection.cursor() as cursor:
        for tabla in tablas_operativas:
            try:
                # Agregamos la columna que Django exige
                cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN empresa_id BIGINT NULL;")
            except Exception:
                pass # Si la columna ya existe, la ignoramos suavemente
                
            try:
                # Le asignamos todo el historial antiguo a tu empresa (Cananea)
                cursor.execute(f"UPDATE {tabla} SET empresa_id = {empresa_id} WHERE empresa_id IS NULL;")
                exitos.append(tabla)
            except Exception:
                pass # Si la tabla no existe en tu BD con ese nombre exacto, saltamos a la siguiente

    return HttpResponse(f"<h2>¡Datos Rescatados!</h2> <p>Las tablas <b>{', '.join(exitos)}</b> fueron actualizadas y conectadas a tu Sede. Ve a tu panel a ver la magia.</p>")
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
    
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
