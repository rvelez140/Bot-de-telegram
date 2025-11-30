# ⚡ Guía de Referencia Rápida

## 🚀 Inicio Rápido (3 pasos)

```bash
# 1. Extraer archivos
tar -xzf telegram_downloader_bot.tar.gz
cd telegram_downloader_bot

# 2. Configurar token
cp .env.example .env
nano .env  # Agregar tu TELEGRAM_BOT_TOKEN

# 3. Iniciar bot
docker compose up -d
```

## 📱 Obtener Token de Telegram

1. Busca `@BotFather` en Telegram
2. Envía `/newbot`
3. Sigue instrucciones
4. Copia el token

## 🐳 Comandos Docker Esenciales

### Gestión Básica
```bash
# Iniciar bot
docker compose up -d

# Detener bot
docker compose stop

# Reiniciar bot
docker compose restart

# Ver logs
docker compose logs -f

# Ver estado
docker compose ps
```

### Actualización
```bash
# Reconstruir
docker compose build

# Aplicar cambios
docker compose up -d --build
```

### Limpieza
```bash
# Detener y eliminar
docker compose down

# Limpiar recursos
docker system prune -a
```

## 🔧 Resolución Rápida de Problemas

### Bot no responde
```bash
# 1. Ver logs
docker compose logs -f

# 2. Verificar estado
docker compose ps

# 3. Reiniciar
docker compose restart
```

### Token inválido
```bash
# 1. Verificar token
cat .env

# 2. Corregir token
nano .env

# 3. Reiniciar
docker compose down && docker compose up -d
```

### Sin espacio en disco
```bash
# Limpiar descargas
rm -rf ./downloads/*

# Limpiar Docker
docker system prune -a
```

## 📊 Monitoreo

```bash
# Ver uso de recursos
docker stats telegram-video-downloader

# Ver logs con timestamps
docker compose logs -f --timestamps

# Ver últimas 50 líneas
docker compose logs --tail=50
```

## ⚙️ Personalización Común

### Cambiar tamaño máximo de archivo
Edita `bot.py` línea ~40:
```python
'max_filesize': 100 * 1024 * 1024,  # 100MB
```

### Limitar usuarios autorizados
Agrega al inicio de `bot.py`:
```python
AUTHORIZED_USERS = [123456789, 987654321]
```

### Cambiar calidad de video
Edita `bot.py` en la función `download_video()`:
```python
# 720p máximo
ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
```

## 🔐 Seguridad

```bash
# Proteger .env
chmod 600 .env

# Ver permisos
ls -la .env
```

## 📁 Estructura de Archivos

```
telegram_downloader_bot/
├── bot.py                      # Código principal
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Orquestación
├── requirements.txt            # Dependencias
├── .env                        # Tu token (no compartir)
├── README.md                   # Documentación completa
├── INSTALACION_DOCKER.md       # Guía de instalación
├── FAQ.md                      # Preguntas frecuentes
├── ADVANCED.md                 # Configuración avanzada
├── ARQUITECTURA.md             # Diagrama del sistema
└── setup.sh                    # Instalación automática
```

## 🌐 Plataformas Soportadas

- ✅ TikTok (sin marca de agua)
- ✅ YouTube (hasta 1080p)
- ✅ X/Twitter
- ✅ Instagram (posts y reels)

## 💡 Tips Útiles

### Agregar más plataformas
yt-dlp soporta 1000+ sitios. Solo agrega el dominio en `bot.py`:
```python
self.supported_platforms = {
    'tiktok': ['tiktok.com'],
    'youtube': ['youtube.com'],
    'nuevaplataforma': ['ejemplo.com'],
}
```

### Backup rápido
```bash
tar -czf backup-$(date +%F).tar.gz .env bot.py
```

### Ver ID de Telegram
Busca `@userinfobot` en Telegram

### Actualizar yt-dlp
```bash
docker compose exec telegram-downloader-bot pip install --upgrade yt-dlp
```

## 🆘 Enlaces Útiles

- **Docker Docs**: https://docs.docker.com/
- **Telegram Bot API**: https://core.telegram.org/bots
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **python-telegram-bot**: https://docs.python-telegram-bot.org/

## 📞 Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/help` | Ayuda |
| `/platforms` | Plataformas soportadas |
| `[URL]` | Descargar video |

## 🎯 Flujo de Uso

1. Copiar enlace de video
2. Enviar al bot en Telegram
3. Esperar procesamiento
4. Recibir video sin marca de agua

## 📈 Requisitos del Servidor

**Mínimo:**
- 1 CPU core
- 1GB RAM
- 10GB disco

**Recomendado:**
- 2 CPU cores
- 2GB RAM
- 20GB disco

## 🔄 Actualizaciones

```bash
# Si usas git
git pull

# Reconstruir
docker compose up -d --build
```

## 🐛 Diagnóstico Completo

```bash
echo "=== DIAGNÓSTICO ==="
docker --version
docker compose version
docker ps
cat .env | grep TOKEN | sed 's/=.*/=***/'
docker compose logs --tail=20
df -h
echo "=== FIN ==="
```

---

## ⚡ Comandos de Una Línea

```bash
# Instalación completa
./setup.sh

# Reinicio completo
docker compose down && docker compose up -d --build

# Ver todo
docker compose ps && docker compose logs --tail=10

# Backup
tar -czf bot-backup.tar.gz bot.py .env docker-compose.yml

# Limpiar todo
docker compose down && docker system prune -a && rm -rf downloads/*
```

---

**¿Necesitas más ayuda?** Consulta:
- `README.md` - Documentación completa
- `FAQ.md` - Preguntas frecuentes
- `INSTALACION_DOCKER.md` - Guía detallada
- `ADVANCED.md` - Configuración avanzada
