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
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.core.mail import send_mail
from django.conf import settings
import traceback
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

@csrf_exempt # Usar con precaución. Idealmente, se configuraría el envío de token CSRF desde JS.
def confirmar_pedido(request):
    if request.method == 'POST':
        # 1. Validar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

        pedido = None # Declaramos la variable pedido aquí

        try:
            # 2. Cargar los datos enviados desde el frontend
            data = json.loads(request.body)
            productos_carrito = data.get('productos', [])
            
            if not productos_carrito:
                return JsonResponse({'error': 'El carrito está vacío'}, status=400)

            # 3. Usar una transacción para asegurar la integridad de los datos
            with transaction.atomic():
                # 4. Crear el objeto Pedido principal (inicializamos totales a 0)
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    direccion_envio=data.get('direccion_envio'),
                    telefono=data.get('telefono'),
                    metodo_pago=data.get('metodo_pago'),
                    subtotal=Decimal('0.00'),
                    total=Decimal('0.00'),
                    impuestos=Decimal('0.00'),
                    coste_entrega=Decimal('0.00'),
                    descuento=Decimal('0.00')
                )

                # Generar un número de pedido único y guardarlo
                pedido.numero_pedido = f"PED-{pedido.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                pedido.save()

                subtotal_pedido = Decimal('0.00')
                descuento_total = Decimal('0.00')
                items_response = []

                # 5. Iterar sobre los productos del carrito para crear los Items del Pedido
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
                    subtotal_pedido += total_item

                    descuento_item = Decimal('0.00')
                    if producto.precio_oferta is not None:
                        descuento_item = (Decimal(producto.precio) - Decimal(producto.precio_oferta)) * Decimal(cantidad)
                        descuento_item = descuento_item.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        descuento_total += descuento_item
                    imagen=item_data.get('imagen')
                    texto=item_data.get('texto')
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

                # 6. Cálculo de envío/impuestos
                coste_envio = Decimal(str(data.get('coste_envio'))) if data.get('coste_envio') is not None else Decimal('4.99')
                umbral_envio_gratis = Decimal('50.00')
                if subtotal_pedido >= umbral_envio_gratis:
                    coste_envio = Decimal('0.00')

                base_imponible = (subtotal_pedido - descuento_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                impuesto_rate = Decimal('0.21')
                impuestos = (base_imponible * impuesto_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                total_pedido = (base_imponible + impuestos + coste_envio).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                # 7. Guardar totales
                pedido.subtotal = subtotal_pedido
                pedido.descuento = descuento_total
                pedido.coste_entrega = coste_envio
                pedido.impuestos = impuestos
                pedido.total = total_pedido
                pedido.save()

                resumen = {
                    'subtotal': str(subtotal_pedido),
                    'descuento': str(descuento_total),
                    'coste_envio': str(coste_envio),
                    'impuestos': str(impuestos),
                    'total': str(total_pedido)
                }

                # 8. Enviar correo de confirmación (no bloqueante)
                try:
                    subject = f"Confirmación pedido {pedido.numero_pedido}"
                    lines = [f"Pedido: {pedido.numero_pedido}", "", "Resumen:"]
                    lines.append(f"Subtotal: {resumen['subtotal']} €")
                    lines.append(f"Descuento: {resumen['descuento']} €")
                    lines.append(f"Coste envío: {resumen['coste_envio']} €")
                    lines.append(f"Impuestos: {resumen['impuestos']} €")
                    lines.append(f"Total: {resumen['total']} €")
                    lines.append("")
                    lines.append("Productos:")
                    for it in items_response:
                        lines.append(f"- {it['nombre']} ({it['color']}, {it['talla']}) x{it['cantidad']}: {it['subtotal_item']} €")
                    message = "\n".join(lines)
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@example.com'
                    send_mail(subject, message, from_email, [request.user.email], fail_silently=False)
                except Exception as e:
                    # Imprimimos el error para depuración pero no detenemos la creación del pedido
                    print('Error enviando email de confirmación:', e)
                    traceback.print_exc()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        # 9. Si todo fue bien, devolver una respuesta de éxito con desglose
        return JsonResponse({'mensaje': 'Pedido creado con éxito', 'pedido_id': pedido.id, 'items': items_response, 'resumen': resumen})
    
    # Si el método es GET, simplemente renderiza la página
    return render(request, 'confirmar_pedido.html', {})


@login_required
def mis_pedidos(request):
    pedidos = request.user.pedidos.all().order_by('-fecha_creacion')
    return render(request, "pedidos.html", {"pedidos": pedidos})
@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    return render(request, "detalle_pedido.html", {"pedido": pedido})