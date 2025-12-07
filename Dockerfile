FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    wget \
    curl \
    ca-certificates \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Actualizar pip y instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Actualizar yt-dlp a la última versión
RUN pip install --no-cache-dir --upgrade yt-dlp

# Copiar el código del bot
COPY bot.py .

# Crear directorio para descargas
RUN mkdir -p /downloads && chmod 777 /downloads

# Variable de entorno para el token (se debe configurar al ejecutar)
ENV TELEGRAM_BOT_TOKEN=""
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Ejecutar el bot
CMD ["python", "-u", "bot.py"]
