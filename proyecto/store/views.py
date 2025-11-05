from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import Producto
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
    nombre=request.GET.get('nombre')
    if nombre:
        productos = Producto.objects.filter(nombre__icontains=nombre)
    else:
        productos = Producto.objects.all()
    contexto = {'productos': productos}
    return HttpResponse(render(request, 'productos.html',contexto))
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
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
