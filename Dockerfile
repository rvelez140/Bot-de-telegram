FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    wget \
    curl \
    ca-certificates \
    git \
    build-essential \
    # Dependencias para Playwright/Chromium
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Actualizar pip y instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar navegadores de Playwright (solo chromium)
RUN playwright install chromium

# Actualizar yt-dlp a la última versión
RUN pip install --no-cache-dir --upgrade yt-dlp

# Copiar el código del bot
COPY bot.py .

# Copiar cookies si existe (el workflow crea uno vacío si no existe)
COPY cookies.txt /app/cookies.txt

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
