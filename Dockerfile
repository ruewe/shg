# Dockerfile
FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten installieren
# netcat-openbsd wird oft für wartende Entrypoints (wait-for-it) genutzt
RUN apt-get update && apt-get install -y netcat-openbsd gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt whitenoise gunicorn

# Projektcode kopieren
COPY . .

# Environment Variable für Production (kann im Compose überschrieben werden)
ENV DJANGO_SETTINGS_MODULE=shg.settings

# Startbefehl
# Führt Migrationen aus, sammelt Statics und startet Gunicorn
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn shg.wsgi:application --bind 0.0.0.0:8000"]
