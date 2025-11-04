from django.contrib import admin
from .models import Producto, Categoria, TallaProducto, Marca,Cliente
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(TallaProducto)
admin.site.register(Marca)
admin.site.register(Cliente)
