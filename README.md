# Tienda Virtual – Guía y Estructura del Proyecto

Este repositorio contiene una tienda virtual desarrollada con Django. A continuación se describe la organización general del código y los pasos necesarios para poner el proyecto en marcha desde cero.

## Vista general

- `manage.py`: punto de entrada para los comandos administrativos de Django.
- `db.sqlite3`: base de datos SQLite generada tras ejecutar las migraciones.
- `tienda_virtual/`: configuración global del proyecto.
- `store/`: aplicación principal con la lógica de negocio de la tienda.

```
proyecto/
├── manage.py
├── db.sqlite3
├── tienda_virtual/
│   ├── __init__.py
│   ├── settings.py      # Configuración del proyecto (apps registradas, base de datos, plantillas, estáticos, etc.)
│   ├── urls.py          # Rutas principales del sitio; delegan en la app store.
│   ├── wsgi.py / asgi.py
│   └── __pycache__/
└── store/
    ├── __init__.py
    ├── admin.py         # Registro de modelos para el panel de administración.
    ├── apps.py
    ├── forms.py         # Formularios para registro de clientes.
    ├── models.py        # Definición de Cliente, Producto y demás entidades.
    ├── views.py         # Vistas para login, logout, registro y listado de productos.
    ├── tests.py
    ├── migrations/      # Historial de cambios en el esquema.
    ├── fixtures/        # Datos de ejemplo (datos.json) para poblar la base.
    ├── templates/       # `base.html`, `login.html`, `register.html`, `productos.html`.
    └── static/          # Archivos estáticos (CSS, imágenes, etc.).
```

### Configuración (`tienda_virtual/settings.py`)
- Registra la app `store` en `INSTALLED_APPS`.
- Define la conexión a la base de datos (SQLite por defecto) y las rutas de plantillas/estáticos.

### Aplicación `store`
- **Modelos (`models.py`)**: encapsulan la persistencia de productos, clientes y relaciones.
- **Formularios (`forms.py`)**: proporcionan validación y creación de usuarios/Clientes.
- **Vistas (`views.py`)**: gestionan autenticación (login/logout/registro) y listado de productos, incluido un filtro por nombre a través de query string.
- **Templates**: 
  - `base.html` actúa como layout principal.
  - `productos.html` consume el listado de productos devuelto por la vista.
  - `login.html` y `register.html` renderizan los formularios de autenticación.
- **Recursos adicionales**:
  - `fixtures/datos.json` permite cargar datos iniciales con `loaddata`.
  - `static/css/` aloja estilos para la interfaz.

## Puesta en marcha

Los siguientes comandos son los utilizados para preparar y ejecutar el proyecto:

```powershell
# (Opcional) Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instalar dependencias principales
pip install django
pip install Pillow

# Generar migraciones (se creó 0002_alter_cliente_email_alter_producto_marca)
python manage.py makemigrations

# Aplicar migraciones a la base de datos SQLite
python manage.py migrate

# (Opcional) Cargar datos de ejemplo
python manage.py loaddata store/fixtures/datos.json

# Iniciar el servidor de desarrollo
python manage.py runserver
```

Tras ejecutar `runserver`, el proyecto queda disponible en `http://127.0.0.1:8000/`.  
- La página principal (`/`) muestra el catálogo de productos, con soporte para filtrar por nombre usando la query `?nombre=...`.  
- La autenticación se maneja a través de `/login/`, `/logout/` y `/register/`.
