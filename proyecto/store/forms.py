from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente

class ClienteRegistroForm(UserCreationForm):
    class Meta:
        model = Cliente
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'telefono', 'direccion', 'ciudad', 'codigo_postal',
            'password1', 'password2',
        ]
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'password': 'Contraseña',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'codigo_postal': 'Código postal',
            'password': 'Contraseña',
        }
        widgets = {
            'direccion': forms.TextInput(attrs={'placeholder': 'Calle, número...'}),
            'ciudad': forms.TextInput(attrs={'placeholder': 'Ciudad'}),
            'codigo_postal': forms.TextInput(attrs={'placeholder': 'Código postal'}),
        }