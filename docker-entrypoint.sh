#!/bin/sh
set -e

# Entrypoint script to prepare the Django app before serving requests.

python manage.py migrate --noinput
python manage.py loaddata store/fixtures/datos.json

# Create or update the admin user with the provided credentials.
python - <<'PY'
import django
from django.contrib.auth import get_user_model

django.setup()

User = get_user_model()
email = "admin@gmail.com"
username = "admin"
password = "admin"

defaults = {
    "username": username,
    "first_name": "Admin",
    "last_name": "User",
    "direccion": "Admin Street 123",
    "ciudad": "Admin City",
    "codigo_postal": "00000",
    "telefono": "000000000",
}

user, created = User.objects.get_or_create(email=email, defaults=defaults)

if created:
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
else:
    updated = False
    if user.username != username:
        user.username = username
        updated = True
    if not user.is_staff or not user.is_superuser:
        user.is_staff = True
        user.is_superuser = True
        updated = True
    if not user.check_password(password):
        user.set_password(password)
        updated = True
    for field, value in defaults.items():
        if getattr(user, field) in (None, ""):
            setattr(user, field, value)
            updated = True
    if updated:
        user.save()
PY

# Collect static files into STATIC_ROOT for serving in production setups.
python manage.py collectstatic --noinput --clear

PORT="${PORT:-8000}"
if [ "$#" -eq 0 ]; then
    exec python manage.py runserver "0.0.0.0:${PORT}"
fi

exec "$@"
