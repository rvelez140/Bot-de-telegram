# 🔧 Guía de Uso Avanzado

## Configuración Avanzada de yt-dlp

### Mejorar calidad de descarga

Edita `bot.py` en la función `download_video()`:

```python
# Para YouTube - mejor calidad
ydl_opts['format'] = 'bestvideo[height<=2160]+bestaudio/best'

# Para mantener audio original
ydl_opts['postprocessors'] = [{
    'key': 'FFmpegVideoConvertor',
    'preferedformat': 'mp4',
}]
```

### Agregar subtítulos automáticamente

```python
ydl_opts['writesubtitles'] = True
ydl_opts['subtitleslangs'] = ['es', 'en']
```

### Descargar solo audio

```python
ydl_opts['format'] = 'bestaudio/best'
ydl_opts['postprocessors'] = [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
}]
```

## Configuración de Docker

### Limitar recursos del contenedor

Edita `docker-compose.yml`:

```yaml
services:
  telegram-downloader-bot:
    # ... configuración existente ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
```

### Usar red host (para mejor rendimiento)

```yaml
services:
  telegram-downloader-bot:
    network_mode: "host"
    # Elimina la sección networks
```

### Montar múltiples volúmenes

```yaml
volumes:
  - ./downloads:/downloads
  - ./logs:/app/logs
  - ./config:/app/config
```

## Personalización del Bot

### Agregar comando para estadísticas

Agrega en `bot.py`:

```python
import psutil

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar estadísticas del sistema"""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    stats_text = f"""
📊 *Estadísticas del Sistema*

🖥️ CPU: {cpu}%
💾 Memoria: {memory}%
💿 Disco: {disk}%
    """
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# En main(), agregar:
application.add_handler(CommandHandler("stats", stats))
```

No olvides agregar en `requirements.txt`:
```
psutil==5.9.6
```

### Limitar usuarios autorizados

```python
AUTHORIZED_USERS = [123456789, 987654321]  # IDs de Telegram

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text(
            "❌ No estás autorizado para usar este bot."
        )
        return
    
    # Resto del código...
```

### Agregar sistema de logs a archivo

```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging a archivo
file_handler = RotatingFileHandler(
    '/app/logs/bot.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)
```

## Integración con Base de Datos

### Agregar SQLite para tracking

```python
import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('/app/data/bot.db')
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                platform TEXT,
                url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def log_download(self, user_id, username, platform, url):
        self.conn.execute(
            'INSERT INTO downloads (user_id, username, platform, url) VALUES (?, ?, ?, ?)',
            (user_id, username, platform, url)
        )
        self.conn.commit()

db = Database()
```

## Despliegue en Producción

### Usar Docker Swarm

```bash
# Inicializar swarm
docker swarm init

# Desplegar stack
docker stack deploy -c docker-compose.yml telegram-bot

# Ver servicios
docker service ls

# Escalar el servicio
docker service scale telegram-bot_telegram-downloader-bot=3
```

### Configurar restart policies

En `docker-compose.yml`:

```yaml
deploy:
  restart_policy:
    condition: on-failure
    delay: 5s
    max_attempts: 3
    window: 120s
```

### Backups automáticos

Crear `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup de la base de datos
docker-compose exec -T telegram-downloader-bot \
    tar czf - /app/data | \
    cat > "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# Mantener solo últimos 7 backups
ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +8 | xargs rm -f
```

### Monitoreo con Prometheus

Agrega en `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

## Optimizaciones de Rendimiento

### Cache de videos descargados

```python
import hashlib

def get_cache_key(url):
    return hashlib.md5(url.encode()).hexdigest()

async def download_video(self, url, chat_id):
    cache_key = get_cache_key(url)
    cache_file = f"/cache/{cache_key}.mp4"
    
    if os.path.exists(cache_file):
        return {'success': True, 'filename': cache_file, 'cached': True}
    
    # Descargar normalmente...
```

### Procesamiento en paralelo

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def download_video_async(self, url, chat_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        self.download_video_sync,
        url,
        chat_id
    )
```

### Compresión de videos

```python
ydl_opts['postprocessors'].append({
    'key': 'FFmpegVideoConvertor',
    'preferedformat': 'mp4',
})

# Agregar opciones de ffmpeg para comprimir
ydl_opts['postprocessor_args'] = [
    '-c:v', 'libx264',
    '-crf', '28',
    '-preset', 'fast',
    '-c:a', 'aac',
    '-b:a', '128k'
]
```

## Troubleshooting Avanzado

### Debug mode

Activa logs detallados:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Para yt-dlp
ydl_opts['verbose'] = True
```

### Capturar errores específicos

```python
from yt_dlp.utils import DownloadError, ExtractorError

try:
    # código de descarga
except DownloadError as e:
    logger.error(f"Error de descarga: {e}")
except ExtractorError as e:
    logger.error(f"Error del extractor: {e}")
```

## Variables de Entorno Adicionales

Crea un `.env` más completo:

```env
# Bot
TELEGRAM_BOT_TOKEN=tu_token
AUTHORIZED_USERS=123456,789012

# Paths
DOWNLOAD_DIR=/downloads
CACHE_DIR=/cache
LOG_DIR=/logs

# Configuración
MAX_FILE_SIZE=50
ENABLE_CACHE=true
CACHE_EXPIRY_HOURS=24

# Calidad
VIDEO_QUALITY=1080p
AUDIO_BITRATE=192k
```

## CI/CD con GitHub Actions

Crear `.github/workflows/deploy.yml`:

```yaml
name: Deploy Bot

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/bot
            git pull
            docker-compose up -d --build
```

---

¿Necesitas ayuda con alguna configuración específica? ¡Pregunta!
