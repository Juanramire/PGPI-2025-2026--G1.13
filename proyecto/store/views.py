from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import Producto, Categoria, VarianteProducto, Pedido, ItemPedido
from django.contrib.auth import logout
from .forms import ClienteRegistroForm
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from datetime import datetime
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
                # 4. Crear el objeto Pedido principal
                pedido = Pedido.objects.create(
                    cliente=request.user,
                    direccion_envio=data.get('direccion_envio'),
                    telefono=data.get('telefono'),
                    metodo_pago=data.get('metodo_pago'),
                    # Los totales se calcularán a continuación
                    subtotal=0,
                    total=0,
                    impuestos=0, # Simplificado por ahora
                    coste_entrega=0 # Simplificado por ahora
                )

                # Generar un número de pedido único y guardarlo
                pedido.numero_pedido = f"PED-{pedido.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                pedido.save()

                subtotal_pedido = 0

                # 5. Iterar sobre los productos del carrito para crear los Items del Pedido
                for item_data in productos_carrito:
                    variante = get_object_or_404(VarianteProducto, producto_id=item_data['id'], color=item_data['color'], talla=item_data['talla'])
                    
                    if variante.stock < item_data['cantidad']:
                        raise Exception(f"No hay stock suficiente para {variante.producto.nombre} ({variante.color}, {variante.talla})")
                    
                    variante.stock -= item_data['cantidad']
                    variante.save()

                    precio_unitario = float(item_data['precio'])
                    total_item = precio_unitario * item_data['cantidad']
                    subtotal_pedido += total_item

                    ItemPedido.objects.create(
                        pedido=pedido, producto=variante.producto, color=variante.color,
                        talla=variante.talla, cantidad=item_data['cantidad'],
                        precio_unitario=precio_unitario, total=total_item
                    )
                
                # 8. Actualizar los totales del pedido y guardarlo
                pedido.subtotal = subtotal_pedido
                pedido.total = subtotal_pedido # Simplificado: total = subtotal
                pedido.save()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        # 9. Si todo fue bien, devolver una respuesta de éxito
        return JsonResponse({'mensaje': 'Pedido creado con éxito', 'pedido_id': pedido.id})
    
    # Si el método es GET, simplemente renderiza la página
    return render(request, 'confirmar_pedido.html', {})
    