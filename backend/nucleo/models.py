from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. EL NUEVO MODELO DE EMPRESA
class Empresa(models.Model):
    nombre = models.CharField(max_length=150)
    ciudad = models.CharField(max_length=100)
    # Aquí puedes agregar logotipos o configuraciones específicas después

    class Meta:
        db_table = 'empresas'

    def __str__(self):
        return self.nombre


# 2. EL USUARIO VINCULADO A LA EMPRESA
class Usuario(AbstractUser):
    # Se hereda el usuario base de Django y se le agrega a qué empresa pertenece
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'usuarios'


# 3. TUS MODELOS OPERATIVOS ACTUALIZADOS
class Maquina(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'maquinas'
        # Evita que haya dos máquinas con el mismo nombre en la MISMA empresa
        unique_together = ('empresa', 'nombre') 

    def __str__(self):
        return self.nombre


class Bitacora(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()

    # Espacio 1
    tarea_1 = models.CharField(max_length=255, default='-')
    avance_1 = models.IntegerField(default=0)
    fecha_inicio_1 = models.DateField(null=True, blank=True)
    maquina_1 = models.CharField(max_length=255, default='-')

    # Espacio 2
    tarea_2 = models.CharField(max_length=255, default='-')
    avance_2 = models.IntegerField(default=0)
    fecha_inicio_2 = models.DateField(null=True, blank=True)
    maquina_2 = models.CharField(max_length=255, default='-')

    # Espacio 3
    tarea_3 = models.CharField(max_length=255, default='-')
    avance_3 = models.IntegerField(default=0)
    fecha_inicio_3 = models.DateField(null=True, blank=True)
    maquina_3 = models.CharField(max_length=255, default='-')

    # Espacio 4
    tarea_4 = models.CharField(max_length=255, default='-')
    avance_4 = models.IntegerField(default=0)
    fecha_inicio_4 = models.DateField(null=True, blank=True)
    maquina_4 = models.CharField(max_length=255, default='-')

    # Espacio 5
    tarea_5 = models.CharField(max_length=255, default='-')
    avance_5 = models.IntegerField(default=0)
    fecha_inicio_5 = models.DateField(null=True, blank=True)
    maquina_5 = models.CharField(max_length=255, default='-')

    class Meta:
        db_table = 'bitacora'

    def __str__(self):
        return self.nombre


class BitacoraCompletado(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    tarea = models.CharField(max_length=255)
    maquina = models.CharField(max_length=255, default='-')
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    dias_duracion = models.IntegerField(default=0)

    class Meta:
        db_table = 'bitacora_completados'

    def __str__(self):
        return f"{self.nombre} - {self.tarea}"


class PrestamoHerramienta(models.Model):
    ESTADO_CHOICES = [
        ('Prestado', 'Prestado'),
        ('Devuelto', 'Devuelto'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    trabajador = models.CharField(max_length=100)
    herramienta = models.CharField(max_length=255)
    tarea = models.CharField(max_length=255)
    fecha_prestamo = models.DateTimeField()
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Prestado')

    class Meta:
        db_table = 'prestamo_herramientas'

    def __str__(self):
        return f"{self.herramienta} - {self.trabajador}"


class Taller(models.Model):
    ESTADO_CHOICES = [
        ('En Taller', 'En Taller'),
        ('Reparado', 'Reparado'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    maquina = models.CharField(max_length=255)
    motivo = models.CharField(max_length=255)
    fecha_ingreso = models.DateTimeField()
    fecha_salida = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='En Taller')

    class Meta:
        db_table = 'taller'

    def __str__(self):
        return f"{self.maquina} - {self.estado}"


class ProductoInventario(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    clave = models.CharField(max_length=50, primary_key=True)
    descripcion = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    orden = models.CharField(max_length=100, blank=True, null=True)
    obra = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.clave} - {self.descripcion}"


class MovimientoAlmacen(models.Model):
    TIPO_CHOICES = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    producto = models.ForeignKey(ProductoInventario, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    piezas = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    solicitante = models.CharField(max_length=100, blank=True, null=True)
    maquina = models.CharField(max_length=100, blank=True, null=True)
    obra = models.CharField(max_length=100, blank=True, null=True)
    orden = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.clave} ({self.piezas} pz)"