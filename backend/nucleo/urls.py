from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MaquinaViewSet, 
    BitacoraViewSet, 
    BitacoraCompletadoViewSet,
    PrestamoHerramientaViewSet, 
    TallerViewSet,
    ProductoInventarioViewSet,
    MovimientoAlmacenViewSet
)

router = DefaultRouter()

router.register(r'maquinas', MaquinaViewSet, basename='maquinas')
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')
router.register(r'completados', BitacoraCompletadoViewSet, basename='completados')
router.register(r'herramientas', PrestamoHerramientaViewSet, basename='herramientas')
router.register(r'taller', TallerViewSet, basename='taller')
router.register(r'inventario', ProductoInventarioViewSet, basename='inventario')
router.register(r'movimientos', MovimientoAlmacenViewSet, basename='movimientos')

urlpatterns = [
    path('', include(router.urls)),
]