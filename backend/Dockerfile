# Usa una imagen oficial de Python ligera
FROM python:3.11-slim

# Evitar que Python escriba archivos pyc y habilitar modo sin búfer para logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema requeridas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias de Python
# En este contexto, requirements.txt estará directamente en la raíz si el build se lanza desde la carpeta backend
COPY requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copiar todo el contenido del contexto de construcción (que es la carpeta backend) a /app/backend
COPY . /app/backend

# Exponer el puerto por defecto de Cloud Run (8080)
EXPOSE 8080

# Ejecutar FastAPI usando uvicorn con la ruta absoluta del módulo
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
