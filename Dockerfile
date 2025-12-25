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

# Entrypoint kopieren und ausführbar machen
COPY entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Environment Variable für Production
ENV DJANGO_SETTINGS_MODULE=shg.settings

# Entrypoint setzen
ENTRYPOINT ["/app/entrypoint.sh"]

# Startbefehl
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn shg.wsgi:application --bind 0.0.0.0:8000"]
