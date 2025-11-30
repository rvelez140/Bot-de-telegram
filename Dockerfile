FROM python:3.11-slim

# Instalar ffmpeg (necesario para procesar videos)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del bot
COPY bot.py .

# Crear directorio para descargas
RUN mkdir -p /downloads

# Variable de entorno para el token (se debe configurar al ejecutar)
ENV TELEGRAM_BOT_TOKEN=""

# Ejecutar el bot
CMD ["python", "bot.py"]
