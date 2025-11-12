from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import Producto, Categoria
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

    contexto = {
        'producto': producto,
        'categorias_navbar': categorias,
        'ahorro': ahorro
    }
    return render(request, 'detalle_producto.html', contexto)

