from django.db import models

class TallaProducto(models.Model):
    talla = models.CharField(max_length=30)
    stock = models.PositiveIntegerField()
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='tallas')
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    marca = models.CharField(max_length=100)
    genero=models.CharField(max_length=50)
    color=models.CharField(max_length=50)
    material=models.CharField(max_length=100)
    stock= models.PositiveIntegerField()
    esta_disponible=models.BooleanField(default=True)
    es_destacado=models.BooleanField(default=False)
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    fecha_actualizacion=models.DateTimeField(auto_now=True)
    categoria=models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='productos')
    def __str__(self):
        return self.nombre
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.TextField()
    def __str__(self):
        return self.nombre
class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.TextField()

    def __str__(self):
        return str(self.articulo.id)