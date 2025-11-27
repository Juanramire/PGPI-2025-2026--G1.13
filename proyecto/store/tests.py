import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ItemPedido, Pedido, Producto, VarianteProducto


class ProductoModelTests(TestCase):
    fixtures = ['datos.json']

    def test_producto_esta_disponible_con_stock(self):
        producto = Producto.objects.get(pk=1)
        self.assertTrue(producto.esta_disponible)

    def test_producto_no_disponible_cuando_no_hay_stock(self):
        producto = Producto.objects.get(pk=1)
        producto.variantes.update(stock=0)
        self.assertFalse(producto.esta_disponible)

    def test_colores_disponibles_filtra_sin_stock(self):
        producto = Producto.objects.get(pk=1)
        producto.variantes.filter(color='Rojo').update(stock=0)
        self.assertListEqual(list(producto.colores_disponibles), ['Azul'])


class DetalleProductoViewTests(TestCase):
    fixtures = ['datos.json']

    def test_detalle_producto_muestra_datos_y_variantes(self):
        response = self.client.get(reverse('detalle_producto', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['producto'].pk, 1)
        variantes = response.context['variantes_json']
        self.assertTrue(any(variante['color'] == 'Azul' for variante in variantes))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ConfirmarPedidoViewTests(TestCase):
    fixtures = ['datos.json']

    def setUp(self):
        self.user = get_user_model().objects.get(email='cliente.demo@example.com')
        self.variant = VarianteProducto.objects.filter(producto_id=1, color='Azul', talla='S').first()
        self.url = reverse('confirmar_pedido')

    def test_requiere_usuario_autenticado(self):
        payload = {
            'nombre': 'Usuario invitado',
            'productos': [{'id': self.variant.producto_id, 'cantidad': 1}],
            'metodo_pago': 'Efectivo'
        }
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_rechaza_carrito_vacio(self):
        self.client.force_login(self.user)
        payload = {'productos': [], 'metodo_pago': 'Efectivo'}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    @patch('store.views.SendGridAPIClient')
    def test_crea_pedido_y_actualiza_stock(self, sendgrid_mock):
        self.client.force_login(self.user)
        payload = {
            'productos': [{
                'id': self.variant.producto_id,
                'color': self.variant.color,
                'talla': self.variant.talla,
                'cantidad': 2,
                'texto': 'Nota de prueba',
                'imagen': 'imagen.jpg'
            }],
            'coste_envio': '4.99',
            'direccion_envio': 'Calle Uno 123',
            'telefono': '600000000',
            'metodo_pago': 'Efectivo',
            'email': self.user.email,
            'nombre': f'{self.user.first_name} {self.user.last_name}'
        }
        sendgrid_mock.return_value.send.return_value = None
        stock_inicial = self.variant.stock

        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        pedido = Pedido.objects.get(pk=data['pedido_id'])
        self.variant.refresh_from_db()

        self.assertEqual(self.variant.stock, stock_inicial - 2)
        self.assertEqual(ItemPedido.objects.filter(pedido=pedido).count(), 1)
        self.assertEqual(pedido.subtotal, Decimal('49.98'))
        self.assertEqual(pedido.descuento, Decimal('10.00'))
        self.assertEqual(pedido.coste_entrega, Decimal('4.99'))
        self.assertEqual(pedido.total, Decimal('53.37'))


class PedidosViewsTests(TestCase):
    fixtures = ['datos.json']

    def setUp(self):
        user_model = get_user_model()
        producto = Producto.objects.get(pk=1)
        self.owner = user_model.objects.get(email='cliente.demo@example.com')
        self.other = user_model.objects.get(email='admin.demo@example.com')
        self.pedido_owner = Pedido.objects.create(
            email=self.owner.email,
            nombre=f'{self.owner.first_name} {self.owner.last_name}',
            numero_pedido='PED-TEST-1',
            estado='Pendiente',
            subtotal=Decimal('29.99'),
            impuestos=Decimal('6.30'),
            coste_entrega=Decimal('4.99'),
            descuento=Decimal('0.00'),
            total=Decimal('41.28'),
            metodo_pago='Tarjeta',
            direccion_envio='Calle Uno 123',
            telefono='600000000'
        )
        ItemPedido.objects.create(
            pedido=self.pedido_owner,
            producto=producto,
            talla='M',
            cantidad=1,
            precio_unitario=Decimal('29.99'),
            total=Decimal('29.99'),
            texto='',
            color='Azul'
        )
        self.other_order = Pedido.objects.create(
            email=self.other.email,
            nombre=f'{self.other.first_name} {self.other.last_name}',
            numero_pedido='PED-TEST-2',
            estado='Pendiente',
            subtotal=Decimal('19.99'),
            impuestos=Decimal('4.20'),
            coste_entrega=Decimal('4.99'),
            descuento=Decimal('0.00'),
            total=Decimal('29.18'),
            metodo_pago='Tarjeta',
            direccion_envio='Otra Calle 2',
            telefono='600000001'
        )

    def test_mis_pedidos_solo_incluye_pedidos_del_usuario(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('mis_pedidos'))
        self.assertEqual(response.status_code, 200)
        pedidos = list(response.context['pedidos'])
        self.assertEqual(pedidos, [self.pedido_owner])

    def test_detalle_pedido_reservado_al_propietario(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('pedido', args=[self.other_order.id]))
        self.assertEqual(response.status_code, 404)

    def test_detalle_pedido_propio_se_muestra(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('pedido', args=[self.pedido_owner.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pedido'], self.pedido_owner)
