# 🎥 Bot de Telegram para Descargar Videos e Imágenes

Bot de Telegram que descarga videos e imágenes de TikTok, YouTube, X (Twitter) e Instagram, eliminando marcas de agua cuando es posible. Videos grandes (>2GB) se dividen automáticamente. Soporta múltiples enlaces simultáneos. Completamente auto-alojable usando Docker.

**🌐 NUEVO:** Ahora incluye una aplicación web para gestionar cuentas y descargar videos desde el navegador. Ver [WEB_APP_README.md](WEB_APP_README.md) para más información.

## ✨ Características

### Bot de Telegram
- 📥 Descarga videos de múltiples plataformas:
  - TikTok (sin marca de agua)
  - YouTube (hasta 1080p)
  - X/Twitter
  - Instagram (posts y reels)
- 🖼️ Descarga de imágenes en máxima calidad
- 📦 División automática de videos grandes (>2GB) en partes iguales
- 📎 Procesamiento múltiple de enlaces (envía varios a la vez)
- 🔐 Login para cuentas privadas de Twitter/X
- 🎤 Transcripción de audio con Whisper AI
- 🚫 Elimina marcas de agua automáticamente (TikTok)
- 🐳 Completamente containerizado con Docker
- 🔄 Procesamiento asíncrono
- 📱 Interfaz simple de Telegram
- 🔒 Auto-alojable y privado

### 🌐 Aplicación Web (NUEVO)
- 👤 Sistema de autenticación de usuarios
- 🔐 Gestión de cuentas de redes sociales (Twitter/X)
- 📥 Descarga de videos directamente desde el navegador
- 📊 Historial de descargas
- 🎨 Interfaz moderna y responsive
- 🔒 Almacenamiento seguro de cookies
- Ver documentación completa en [WEB_APP_README.md](WEB_APP_README.md)

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Una cuenta de Telegram
- Acceso a @BotFather en Telegram

## 🚀 Instalación y Configuración

### 1. Clonar o descargar este proyecto

```bash
mkdir telegram-video-bot
cd telegram-video-bot
# Copia todos los archivos del proyecto aquí
```

### 2. Crear tu bot en Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/botfather)
2. Envía el comando `/newbot`
3. Sigue las instrucciones para nombrar tu bot
4. Copia el token que te proporciona (se ve así: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Configurar variables de entorno

```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita el archivo .env y agrega tu token
nano .env
```

Contenido del archivo `.env`:
```
TELEGRAM_BOT_TOKEN=tu_token_aqui
```

### 4. Construir y ejecutar el contenedor

```bash
# Construir la imagen
docker-compose build

# Iniciar el bot
docker-compose up -d

# Ver los logs
docker-compose logs -f
```

## 📱 Uso

### Comandos disponibles

- `/start` - Mensaje de bienvenida
- `/help` - Ayuda y instrucciones
- `/platforms` - Ver plataformas soportadas

### Descargar contenido

**Un solo enlace:**
1. Copia el enlace del video o imagen
2. Envíaselo al bot directamente
3. Espera mientras procesa
4. Recibirás el archivo sin marca de agua (cuando sea posible)

**Múltiples enlaces (NUEVO):**
Envía varios enlaces en un solo mensaje (uno por línea):
```
https://www.tiktok.com/@usuario/video/123
https://www.youtube.com/watch?v=abc
https://www.instagram.com/p/xyz/
```

El bot procesará todos los enlaces automáticamente.

### Videos grandes (NUEVO)

Videos que superan los 2GB se dividen automáticamente en partes:
```
✅ Video - Parte 1/3 (1.9GB)
✅ Video - Parte 2/3 (1.9GB)  
✅ Video - Parte 3/3 (0.2GB)
```

### Ejemplos de enlaces soportados

```
# TikTok (videos e imágenes)
https://www.tiktok.com/@usuario/video/1234567890
https://vm.tiktok.com/ZMabcdefg/

# YouTube (hasta 1080p, división automática si >2GB)
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ

# X (Twitter) - videos e imágenes
https://twitter.com/usuario/status/1234567890
https://x.com/usuario/status/1234567890

# Instagram (posts, reels e imágenes)
https://www.instagram.com/reel/AbCdEfGhIjK/
https://www.instagram.com/p/AbCdEfGhIjK/
```

## 🔧 Gestión del Contenedor

```bash
# Detener el bot
docker-compose stop

# Reiniciar el bot
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f

# Detener y eliminar contenedores
docker-compose down

# Reconstruir después de cambios
docker-compose up -d --build
```

## 📊 Estructura del Proyecto

```
telegram-video-bot/
├── bot.py                  # Código principal del bot
├── requirements.txt        # Dependencias de Python
├── Dockerfile             # Configuración de Docker
├── docker-compose.yml     # Orquestación de contenedores
├── .env                   # Variables de entorno (no incluir en git)
├── .env.example           # Plantilla de variables
├── .gitignore            # Archivos ignorados por git
├── downloads/            # Directorio temporal de descargas
└── README.md            # Esta documentación
```

## ⚙️ Configuración Avanzada

### Cambiar directorio de descargas

Edita `docker-compose.yml`:

```yaml
volumes:
  - ./tu_directorio_personalizado:/downloads
```

### Limitar tamaño de archivos

Edita `bot.py` y modifica:

```python
'max_filesize': 50 * 1024 * 1024,  # 50MB por defecto
```

### Agregar más plataformas

El bot usa `yt-dlp` que soporta [más de 1000 sitios](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md). Para agregar más:

1. Edita `bot.py`
2. Agrega el dominio en `supported_platforms`
3. Opcionalmente, configura opciones específicas en `download_video()`

## 🐛 Solución de Problemas

### El bot no responde

```bash
# Verificar que el contenedor está corriendo
docker ps

# Ver los logs
docker-compose logs -f

# Verificar el token
cat .env
```

### Error al descargar videos

- **Video muy grande**: Telegram tiene un límite de 50MB
- **Video privado**: No se pueden descargar videos privados
- **Copyright**: Algunos videos tienen restricciones

### Error de codificación (Unicode/UTF-8) en Docker

Si ves errores de codificación durante `docker-compose build` o al ejecutar el contenedor:

```bash
# reconstruye sin caché
docker-compose build --no-cache

# levanta servicios nuevamente
docker-compose up -d
```

Este proyecto ya fuerza UTF-8 en los contenedores (`LANG`, `LC_ALL`, `PYTHONUTF8`, `PYTHONIOENCODING`) para evitar fallos por locale/codificación en entornos Linux mínimos.

### Error instalando `openai-whisper` (`No module named 'pkg_resources'`)

Si en el build aparece un error como:

```text
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'openai-whisper' when getting requirements to build wheel
```

La imagen ya está ajustada para instalar `setuptools`/`wheel` y usar `--no-build-isolation` al instalar dependencias. Si vienes de caché antigua, reconstruye así:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### El contenedor se reinicia constantemente

```bash
# Ver los logs para identificar el error
docker-compose logs

# Verificar que el token es correcto
docker-compose exec telegram-downloader-bot printenv TELEGRAM_BOT_TOKEN
```

## 📝 Limitaciones

- Tamaño máximo de archivo: 2GB por parte (Telegram)
- Videos >2GB se dividen automáticamente en partes de ~1.9GB
- No se pueden descargar videos privados o con restricciones de copyright
- La eliminación de marca de agua en TikTok depende de la disponibilidad de la versión sin marca
- Procesamiento múltiple recomendado: hasta 10 enlaces por mensaje

## 🔒 Seguridad y Privacidad

- El bot procesa videos localmente en tu servidor
- No se almacenan videos permanentemente (se eliminan después de enviar)
- El token del bot debe mantenerse seguro
- Nunca compartas tu archivo `.env`

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica la configuración del token
3. Asegúrate de que Docker tiene suficientes recursos
4. Comprueba la conectividad de red

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente para fines personales.

## ⚠️ Aviso Legal

Este bot es para uso personal. Respeta los derechos de autor y las políticas de uso de las plataformas. Descarga solo contenido que tengas derecho a descargar.

## 🙏 Créditos

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Framework del bot
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Descargador de videos

---

Desarrollado con ❤️ para la comunidad
