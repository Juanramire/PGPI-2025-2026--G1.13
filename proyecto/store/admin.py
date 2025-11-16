from django.contrib import admin
from .models import Producto, Categoria, VarianteProducto, Marca,Cliente
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(VarianteProducto)
admin.site.register(Marca)
admin.site.register(Cliente)
