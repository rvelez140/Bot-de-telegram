# 🐳 Configuración de Docker para Bot de Telegram

Esta guía te ayudará a desplegar el bot de descarga de videos de Telegram usando Docker.

## 📋 Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 1.29 o superior)
- Token de bot de Telegram (obtenerlo de @BotFather)

## 🚀 Inicio Rápido

### 1. Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd Bot-de-telegram
```

### 2. Configurar Variables de Entorno

Copia el archivo de ejemplo y edítalo con tu token:

```bash
cp .env.example .env
nano .env  # o usa tu editor favorito
```

Edita el archivo `.env` y agrega tu token:

```
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
```

### 3. Construir y Ejecutar con Docker Compose

```bash
docker-compose up -d
```

¡Eso es todo! El bot ahora está corriendo en segundo plano.

## 📦 Comandos Útiles

### Ver Logs del Bot

```bash
docker-compose logs -f
```

### Detener el Bot

```bash
docker-compose down
```

### Reiniciar el Bot

```bash
docker-compose restart
```

### Reconstruir la Imagen

Si hiciste cambios en el código:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Ver Estado del Contenedor

```bash
docker-compose ps
```

## 🔧 Construcción Manual (sin docker-compose)

Si prefieres usar Docker directamente:

### Construir la Imagen

```bash
docker build -t telegram-bot .
```

### Ejecutar el Contenedor

```bash
docker run -d \
  --name telegram-video-downloader \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN="tu_token_aqui" \
  -v $(pwd)/downloads:/downloads \
  telegram-bot
```

### Ver Logs

```bash
docker logs -f telegram-video-downloader
```

### Detener el Contenedor

```bash
docker stop telegram-video-downloader
docker rm telegram-video-downloader
```

## 🐛 Solución de Problemas

### El bot no inicia

1. Verifica que el token sea correcto:
   ```bash
   docker-compose logs
   ```

2. Asegúrate de que el archivo `.env` existe y tiene el token correcto

### Error al descargar videos de X/Twitter

El bot ahora incluye configuraciones mejoradas para X/Twitter:

- ✅ Usa las últimas APIs de Twitter (syndication y graphql)
- ✅ Headers personalizados para evitar bloqueos
- ✅ yt-dlp siempre actualizado a la última versión

Si aún tienes problemas:

1. Algunos tweets pueden tener videos privados o restringidos
2. Verifica que el tweet realmente contenga video
3. Actualiza yt-dlp a la última versión:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### El contenedor se detiene constantemente

```bash
docker-compose logs
```

Busca errores en los logs. Los problemas comunes son:
- Token inválido o expirado
- Problemas de red
- Falta de espacio en disco

### Limpiar descargas temporales

```bash
rm -rf ./downloads/*
```

## 🔐 Seguridad

- **NUNCA** compartas tu token de Telegram
- **NUNCA** subas el archivo `.env` a Git
- El archivo `.gitignore` ya está configurado para ignorar `.env`

## 📊 Monitoreo

### Ver uso de recursos

```bash
docker stats telegram-video-downloader
```

### Ver espacio usado por el contenedor

```bash
docker system df
```

## 🆕 Actualizar el Bot

Para actualizar a la última versión:

```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 Plataformas Soportadas

El bot puede descargar videos de:

- ✅ **TikTok** (sin marca de agua cuando es posible)
- ✅ **YouTube** (hasta 1080p)
- ✅ **X/Twitter** (con configuración mejorada)
- ✅ **Instagram** (posts y reels)

## 📝 Notas Adicionales

- Las descargas se guardan temporalmente en `/downloads` dentro del contenedor
- Los archivos se eliminan automáticamente después de enviarlos
- El límite de tamaño es 50MB (restricción de Telegram)
- El bot se reiniciará automáticamente si hay algún error

## 🆘 Obtener Ayuda

Si tienes problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica la documentación de yt-dlp: https://github.com/yt-dlp/yt-dlp
3. Crea un issue en el repositorio con los logs del error

## 📄 Licencia

Ver archivo LICENSE del proyecto.
