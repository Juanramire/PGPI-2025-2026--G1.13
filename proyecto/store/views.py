from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from itertools import groupby
from .models import Producto, Categoria, VarianteProducto, Pedido, ItemPedido, VarianteProducto
from django.contrib.auth import logout
from .forms import ClienteRegistroForm
from django.contrib import messages
import json
from django.db import transaction
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.core.mail import send_mail
from django.conf import settings
import traceback
import stripe

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
""" def index(request):
    escaparates = Escaparate.objects.all()
    contexto={'escaparates':list(escaparates)}
    plantilla=loader.get_template('index.html')
    return HttpResponse(plantilla.render(contexto,request))
def escaparates_api(request):
    escaparates = Escaparate.objects.select_related('articulo').all()
    serializer = EscaparateSerializer(escaparates, many=True)
    return JsonResponse(serializer.data, safe=False) """


""" def articulo(request, id):
    articulo_obj = get_object_or_404(Articulo, pk=id)
    return render(request, 'articulo.html', {'articulo': articulo_obj}) """
def productos(request):
    nombre = request.GET.get('nombre')
    categoria_id = request.GET.get('categoria')
    
    productos = Producto.objects.all()
    
    if nombre:
        productos = productos.filter(nombre__icontains=nombre)

    categorias = Categoria.objects.all()
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    contexto = {'productos': productos, 'categorias_navbar': categorias}
    return HttpResponse(render(request, 'productos.html', contexto))

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # redirige a tu página principal
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')  # redirige a tu página principal


def registro_view(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()  # Aquí Django usa set_password automáticamente
            login(request, user)  # Inicia sesión después del registro
            messages.success(request, 'Tu cuenta ha sido creada correctamente.')
            return redirect('/')  # redirige a la página principal o donde quieras
    else:
        form = ClienteRegistroForm()
    
    return render(request, 'register.html', {'form': form})

def detalle_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    categorias = Categoria.objects.all()

    ahorro = None
    if producto.precio_oferta:
        ahorro = producto.precio - producto.precio_oferta
    
    variantes_json = list(producto.variantes.values('color', 'talla', 'stock'))
    
    contexto = {
        'producto': producto,
        'categorias_navbar': categorias,
        'ahorro': ahorro,
        'colores_disponibles': producto.colores_disponibles,
        'variantes_json': variantes_json, # Pasamos las variantes al contexto
    }

    return render(request, 'detalle_producto.html', contexto)

def calcular_resumen_pedido(productos_carrito, coste_envio_override=None):
    subtotal_pedido = Decimal('0.00')
    subtotal_original = Decimal('0.00')
    descuento_total = Decimal('0.00')

    for item_data in productos_carrito:
        producto_id = item_data.get('id')
        if producto_id is None:
            raise ValueError('Producto sin identificador (id)')

        producto = Producto.objects.get(pk=producto_id)
        cantidad = int(item_data.get('cantidad', 1) or 1)

        precio_original = Decimal(str(producto.precio))
        precio_unitario = Decimal(str(producto.precio_oferta)) if producto.precio_oferta is not None else precio_original

        subtotal_original += (precio_original * cantidad)
        subtotal_pedido += (precio_unitario * cantidad)
        descuento_total += (precio_original - precio_unitario) * cantidad

    subtotal_pedido = subtotal_pedido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    subtotal_original = subtotal_original.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    descuento_total = descuento_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    if coste_envio_override is not None:
        coste_envio = Decimal(str(coste_envio_override))
    else:
        umbral_envio_gratis = Decimal('50.00')
        coste_envio = Decimal('0.00') if subtotal_pedido >= umbral_envio_gratis else Decimal('4.99')

    coste_envio = coste_envio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    base_imponible = (subtotal_pedido - descuento_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    impuesto_rate = Decimal('0.21')
    impuestos = (base_imponible * impuesto_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (base_imponible + impuestos + coste_envio).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return {
        'subtotal': subtotal_pedido,
        'subtotal_original': subtotal_original,
        'descuento': descuento_total,
        'coste_envio': coste_envio,
        'impuestos': impuestos,
        'total': total,
    }

def crear_payment_intent(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

    if not settings.STRIPE_SECRET_KEY:
        return JsonResponse({'error': 'Stripe no está configurado'}, status=500)

    try:
        data = json.loads(request.body)
        productos_carrito = data.get('productos', [])
        if not productos_carrito:
            return JsonResponse({'error': 'El carrito está vacío'}, status=400)

        resumen = calcular_resumen_pedido(productos_carrito, data.get('coste_envio'))
        total_cents = int((resumen['total'] * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        intent = stripe.PaymentIntent.create(
            amount=total_cents,
            currency='eur',
            payment_method_types=['card'],
            metadata={
                'cliente_id': request.user.id,
                'correo': request.user.email,
            }
        )

        resumen_str = {key: str(value) for key, value in resumen.items()}
        return JsonResponse({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'resumen': resumen_str
        })
    except stripe.error.StripeError as stripe_err:
        return JsonResponse({'error': str(stripe_err)}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=400)


def confirmar_pedido(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

        try:
            data = json.loads(request.body)
            productos_carrito = data.get('productos', [])
            if not productos_carrito:
                return JsonResponse({'error': 'El carrito está vacío'}, status=400)

            metodo_pago = data.get('metodo_pago')

            resumen = calcular_resumen_pedido(productos_carrito, data.get('coste_envio'))

            if metodo_pago == 'Tarjeta':
                if not settings.STRIPE_SECRET_KEY:
                    return JsonResponse({'error': 'Stripe no está configurado'}, status=500)

                payment_intent_id = data.get('payment_intent_id')
                if not payment_intent_id:
                    return JsonResponse({'error': 'Falta el identificador del pago.'}, status=400)

                try:
                    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                except stripe.error.StripeError as err:
                    return JsonResponse({'error': str(err)}, status=400)

                if intent.status != 'succeeded':
                    return JsonResponse({'error': 'El pago aún no ha sido confirmado.'}, status=400)

                importe_intent = (Decimal(intent.amount) / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if importe_intent != resumen['total']:
                    return JsonResponse({'error': 'El importe cargado no coincide con el total del pedido.'}, status=400)

            pedido = None
            items_response = []

            with transaction.atomic():
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    direccion_envio=data.get('direccion_envio'),
                    telefono=data.get('telefono'),
                    metodo_pago=metodo_pago,
                    subtotal=Decimal('0.00'),
                    total=Decimal('0.00'),
                    impuestos=Decimal('0.00'),
                    coste_entrega=Decimal('0.00'),
                    descuento=Decimal('0.00')
                )

                pedido.numero_pedido = f"PED-{pedido.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                pedido.save()

                for item_data in productos_carrito:
                    producto_id = item_data.get('id')
                    if producto_id is None:
                        raise Exception('Producto sin identificador (id)')

                    producto = Producto.objects.get(pk=producto_id)

                    color = item_data.get('color')
                    talla = item_data.get('talla')
                    cantidad = int(item_data.get('cantidad', 1) or 1)

                    variantes = VarianteProducto.objects.filter(producto=producto)
                    variante = None
                    if color and talla:
                        variante = variantes.filter(color=color, talla=talla).first()
                    if not variante:
                        variante = variantes.filter(stock__gt=0).first() or variantes.first()
                    if not variante:
                        raise Exception(f'No existen variantes para el producto {producto.nombre}')

                    if variante.stock < cantidad:
                        raise Exception(f"No hay stock suficiente para {producto.nombre} ({variante.color}, {variante.talla})")

                    variante.stock -= cantidad
                    variante.save()

                    precio_unitario = producto.precio_oferta if producto.precio_oferta is not None else producto.precio
                    precio_unitario = Decimal(precio_unitario)

                    total_item = (precio_unitario * Decimal(cantidad)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                    imagen = item_data.get('imagen')
                    texto = item_data.get('texto')
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        color=variante.color,
                        talla=variante.talla,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        total=total_item,
                        texto=texto,
                        imagen=imagen
                    )

                    descuento_item = Decimal('0.00')
                    if producto.precio_oferta is not None:
                        descuento_item_calc = (Decimal(producto.precio) - Decimal(producto.precio_oferta)) * Decimal(cantidad)
                        descuento_item = descuento_item_calc.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                    items_response.append({
                        'producto_id': producto.id,
                        'nombre': producto.nombre,
                        'color': variante.color,
                        'talla': variante.talla,
                        'cantidad': cantidad,
                        'precio_unitario': str(precio_unitario),
                        'subtotal_item': str(total_item),
                        'descuento_item': str(descuento_item)
                    })

                pedido.subtotal = resumen['subtotal']
                pedido.descuento = resumen['descuento']
                pedido.coste_entrega = resumen['coste_envio']
                pedido.impuestos = resumen['impuestos']
                pedido.total = resumen['total']
                pedido.save()

                resumen_str = {key: str(value) for key, value in resumen.items()}

                try:
                    subject = f"Confirmación pedido {pedido.numero_pedido}"
                    lines = [f"Pedido: {pedido.numero_pedido}", "", "Resumen:"]
                    lines.append(f"Subtotal: {resumen_str['subtotal']} €")
                    lines.append(f"Descuento: {resumen_str['descuento']} €")
                    lines.append(f"Coste envío: {resumen_str['coste_envio']} €")
                    lines.append(f"Impuestos: {resumen_str['impuestos']} €")
                    lines.append(f"Total: {resumen_str['total']} €")
                    lines.append("")
                    lines.append("Productos:")
                    for it in items_response:
                        lines.append(f"- {it['nombre']} ({it['color']}, {it['talla']}) x{it['cantidad']}: {it['subtotal_item']} €")
                    message = "\n".join(lines)
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@example.com'
                    send_mail(subject, message, from_email, [request.user.email], fail_silently=False)
                except Exception as e:
                    print('Error enviando email de confirmación:', e)
                    traceback.print_exc()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({
            'mensaje': 'Pedido creado con éxito',
            'pedido_id': pedido.id,
            'items': items_response,
            'resumen': resumen_str
        })

    categorias = Categoria.objects.all()
    return render(request, 'confirmar_pedido.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'categorias_navbar': categorias,
    })

@login_required
def mis_pedidos(request):
    pedidos = request.user.pedidos.all().order_by('-fecha_creacion')
    return render(request, "pedidos.html", {"pedidos": pedidos})
@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    return render(request, "detalle_pedido.html", {"pedido": pedido})