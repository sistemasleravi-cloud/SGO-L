from rest_framework import serializers
from .models import Maquina, Bitacora, BitacoraCompletado, PrestamoHerramienta, Taller, ProductoInventario, MovimientoAlmacen
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        fields = '__all__'
        read_only_fields = ['empresa']

class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = '__all__'
        read_only_fields = ['empresa']

class BitacoraCompletadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraCompletado
        fields = '__all__'
        read_only_fields = ['empresa']

class PrestamoHerramientaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrestamoHerramienta
        fields = '__all__'
        read_only_fields = ['empresa']

class TallerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taller
        fields = '__all__'
        read_only_fields = ['empresa']

class ProductoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoInventario
        fields = '__all__'
        read_only_fields = ['empresa']

class MovimientoAlmacenSerializer(serializers.ModelSerializer):
    producto_detalle = ProductoInventarioSerializer(source='producto', read_only=True)
    
    class Meta:
        model = MovimientoAlmacen
        fields = '__all__'
        read_only_fields = ['empresa']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if self.user.empresa:
            data['empresa_nombre'] = self.user.empresa.nombre
        else:
            data['empresa_nombre'] = 'Administración Central'
            
        return data