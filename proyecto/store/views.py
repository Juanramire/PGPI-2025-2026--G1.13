from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Producto
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
    productos = Producto.objects.all()
    contexto = {'productos': productos}
    return HttpResponse(render(request, 'productos.html',contexto))