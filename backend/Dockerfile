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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la carpeta backend al directorio de trabajo /app
COPY . .

# Crear un enlace simbólico de 'backend' apuntando al directorio actual (.)
# Esto permite que las importaciones absolutas del tipo 'from backend.xxx import yyy'
# sigan funcionando sin problemas al ejecutar uvicorn localmente como 'main:app'
RUN ln -s . backend

# Exponer el puerto configurado por Cloud Run
EXPOSE 8080

# Ejecutar de forma local el archivo main:app
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
