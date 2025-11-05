from django.db import models
from django.contrib.auth.models import AbstractUser

class TallaProducto(models.Model):
    talla = models.CharField(max_length=30)
    stock = models.PositiveIntegerField()
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='tallas')
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    genero=models.CharField(max_length=50)
    color=models.CharField(max_length=50)
    material=models.CharField(max_length=100)
    stock= models.PositiveIntegerField()
    esta_disponible=models.BooleanField(default=True)
    es_destacado=models.BooleanField(default=False)
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    fecha_actualizacion=models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria=models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='productos')
    marca = models.ForeignKey('Marca', on_delete=models.CASCADE, related_name='productos')
    def __str__(self):
        return self.nombre
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    def __str__(self):
        return self.nombre
class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='marcas/', blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class Cliente(AbstractUser):
    # Hereda todos los campos de User (username, email, password, etc.)
    
    # Añade los campos que NO tiene AbstractUser:
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    # Ya tiene first_name, last_name, email, password.
    USERNAME_FIELD = 'email'  # Usa el email como campo de inicio de sesión
    REQUIRED_FIELDS = ['username']  # username es obligatorio además de email y password
    # No es necesario el campo fecha_creacion, AbstractUser ya tiene date_joined.

    def __str__(self):
        return self.email

class Pedido(models.Model):
    # Relación de 'uno a muchos': Un cliente puede tener muchos pedidos.
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    numero_pedido = models.CharField(max_length=50, unique=True)
    
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Procesando', 'Procesando'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Pendiente')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    coste_entrega = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    METODO_PAGO_CHOICES = [
        ('Tarjeta', 'Tarjeta de Crédito/Débito'),
        ('PayPal', 'PayPal'),
        ('Transferencia', 'Transferencia Bancaria'),
        ('Efectivo', 'Efectivo (Contra Entrega)'),
    ]
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES)
    
    direccion_envio = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Pedido N° {self.numero_pedido} de {self.cliente.nombre}"

class ItemPedido(models.Model):
    # Relación de 'uno a muchos': Un pedido tiene múltiples ítems.
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    # Relación de 'uno a muchos': Un producto puede estar en muchos ítems de pedido.
    # Aquí se relaciona con tu modelo Producto original.
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT, related_name='items') # Se usa PROTECT para no borrar el Producto si se borra el Item
    
    talla = models.CharField(max_length=30) # El detalle de la talla para este ítem específico
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Precio del producto en el momento de la compra
    total = models.DecimalField(max_digits=10, decimal_places=2) # cantidad * precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.numero_pedido}"
