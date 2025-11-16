from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import Producto, Categoria, TallaProducto
from django.contrib.auth import logout
from .forms import ClienteRegistroForm
from django.contrib import messages
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
    COLOR_CHOICES = [
    ('Rojo', 'Rojo'),
    ('Azul', 'Azul'),
    ('Verde', 'Verde'),
    ('Negro', 'Negro'),
    ('Blanco', 'Blanco'),
    ('Amarillo', 'Amarillo'),
    ('Rosa', 'Rosa'),
    ('Morado', 'Morado'),
    ('Gris', 'Gris'),
    ]
    contexto = {
        'producto': producto,
        'categorias_navbar': categorias,
        'ahorro': ahorro,
        'COLOR_CHOICES':COLOR_CHOICES
    }

    return render(request, 'detalle_producto.html', contexto)
def confirmar_pedido(request):
    return render(request,'confirmar_pedido.html',{})


@login_required
def gestionar_stock(request):
    if not request.user.is_staff:
        raise PermissionDenied("Necesitas permisos administrativos para acceder a esta sección.")

    categorias = Categoria.objects.all()
    tallas = TallaProducto.objects.select_related('producto', 'producto__marca', 'producto__categoria').order_by('producto__nombre', 'talla')

    if request.method == 'POST':
        talla_id = request.POST.get('talla_id')
        nuevo_stock = request.POST.get('stock')

        if talla_id and nuevo_stock is not None:
            try:
                talla_obj = TallaProducto.objects.get(pk=talla_id)
            except TallaProducto.DoesNotExist:
                messages.error(request, "La talla seleccionada no existe.")
            else:
                try:
                    nuevo_valor = int(nuevo_stock)
                    if nuevo_valor < 0:
                        raise ValueError
                    talla_obj.stock = nuevo_valor
                    talla_obj.save()
                    messages.success(
                        request,
                        f"Stock actualizado a {nuevo_valor} para {talla_obj.producto.nombre} ({talla_obj.talla})."
                    )
                    return redirect('gestionar_stock')
                except ValueError:
                    messages.error(request, "Introduce un número entero válido igual o mayor que cero.")
        else:
            messages.warning(request, "Selecciona una talla y una cantidad para actualizar.")

    contexto = {
        'tallas': tallas,
        'categorias_navbar': categorias,
    }
    return render(request, 'admin_stock.html', contexto)
