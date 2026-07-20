from datetime import date
from rest_framework import viewsets
from .models import Maquina, Bitacora, BitacoraCompletado, PrestamoHerramienta, Taller, ProductoInventario, MovimientoAlmacen
from .serializers import (
    MaquinaSerializer, 
    BitacoraSerializer, 
    BitacoraCompletadoSerializer,
    PrestamoHerramientaSerializer, 
    TallerSerializer,
    ProductoInventarioSerializer, 
    MovimientoAlmacenSerializer
)

class MaquinaViewSet(viewsets.ModelViewSet):
    serializer_class = MaquinaSerializer

    def get_queryset(self):
        return Maquina.objects.filter(empresa=self.request.user.empresa).order_by('nombre')

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)


class BitacoraViewSet(viewsets.ModelViewSet):
    serializer_class = BitacoraSerializer

    def get_queryset(self):
        return Bitacora.objects.filter(empresa=self.request.user.empresa)

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)

    def perform_update(self, serializer):
        instance = serializer.save()
        hoy = date.today()
        hubo_cambios = False
        
        for i in range(1, 6):
            avance = getattr(instance, f'avance_{i}')
            tarea = getattr(instance, f'tarea_{i}')
            
            if avance == 100 and tarea and tarea != '-':
                fecha_inicio = getattr(instance, f'fecha_inicio_{i}')
                maquina = getattr(instance, f'maquina_{i}')
                
                dias = (hoy - fecha_inicio).days if fecha_inicio else 0
                
                BitacoraCompletado.objects.create(
                    empresa=instance.empresa,
                    nombre=instance.nombre,
                    tarea=tarea,
                    maquina=maquina,
                    fecha_inicio=fecha_inicio or hoy,
                    fecha_cierre=hoy,
                    dias_duracion=dias
                )
                
                setattr(instance, f'tarea_{i}', '-')
                setattr(instance, f'avance_{i}', 0)
                setattr(instance, f'fecha_inicio_{i}', None)
                setattr(instance, f'maquina_{i}', '-')
                
                hubo_cambios = True
        
        if hubo_cambios:
            instance.save()


class BitacoraCompletadoViewSet(viewsets.ModelViewSet):
    serializer_class = BitacoraCompletadoSerializer

    def get_queryset(self):
        return BitacoraCompletado.objects.filter(empresa=self.request.user.empresa).order_by('-fecha_cierre')

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)


class PrestamoHerramientaViewSet(viewsets.ModelViewSet):
    serializer_class = PrestamoHerramientaSerializer

    def get_queryset(self):
        return PrestamoHerramienta.objects.filter(empresa=self.request.user.empresa).order_by('-fecha_prestamo')

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)


class TallerViewSet(viewsets.ModelViewSet):
    serializer_class = TallerSerializer

    def get_queryset(self):
        return Taller.objects.filter(empresa=self.request.user.empresa).order_by('-fecha_ingreso')

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)


class ProductoInventarioViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoInventarioSerializer

    def get_queryset(self):
        return ProductoInventario.objects.filter(empresa=self.request.user.empresa).order_by('clave')

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)


class MovimientoAlmacenViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoAlmacenSerializer

    def get_queryset(self):
        return MovimientoAlmacen.objects.filter(empresa=self.request.user.empresa).order_by('-fecha')

    def perform_create(self, serializer):
        movimiento = serializer.save(empresa=self.request.user.empresa)
        producto = movimiento.producto
        
        if movimiento.tipo == 'Entrada':
            producto.stock += movimiento.piezas
            if movimiento.orden:
                producto.orden = movimiento.orden
            if movimiento.obra:
                producto.obra = movimiento.obra
                
        elif movimiento.tipo == 'Salida':
            producto.stock -= movimiento.piezas
            
        producto.save()