FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Sistema base para compilar dependencias de Pillow.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ajustamos permisos del entrypoint.
RUN chmod +x /app/docker-entrypoint.sh

WORKDIR /app/proyecto

# Preparamos carpetas de medios/estáticos que usará Django.
RUN python - <<'PY'
import pathlib
for folder in ("media", "staticfiles"):
    pathlib.Path(folder).mkdir(exist_ok=True)
PY

ENTRYPOINT ["/app/docker-entrypoint.sh"]
# El script lanza runserver si no se pasa otro comando.
CMD []
