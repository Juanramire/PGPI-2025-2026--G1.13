from django.contrib import admin
from .models import ItemPedido, Pedido, Producto, Categoria, VarianteProducto, Marca, Cliente
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(VarianteProducto)
admin.site.register(Marca)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
