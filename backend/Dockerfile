# Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# Variables de entorno para que Python no genere archivos .pyc y no use buffer de consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema requeridas para mysqlclient
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el resto del código del backend
COPY . /app/

# Exponer el puerto (Render lo detectará automáticamente)
EXPOSE 8000

# Comando para encender el servidor en producción usando Gunicorn
CMD ["gunicorn", "leravi_api.wsgi:application", "--bind", "0.0.0.0:8000"]
