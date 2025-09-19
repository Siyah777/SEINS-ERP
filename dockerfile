FROM python:3.12.7


ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias de sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs

EXPOSE 8000



# No seteamos aquí DJANGO_SETTINGS_MODULE, lo hará docker-compose o en producción

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]






