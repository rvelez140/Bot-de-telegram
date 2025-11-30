# ❓ Preguntas Frecuentes (FAQ)

## General

### ¿Qué plataformas soporta el bot?

El bot actualmente soporta:
- **TikTok** (con eliminación de marca de agua)
- **YouTube** (hasta 1080p)
- **X/Twitter**
- **Instagram** (posts y reels)

### ¿Es legal descargar videos con este bot?

Debes respetar los derechos de autor y las políticas de cada plataforma. Descarga solo contenido que:
- Sea de tu propiedad
- Tengas permiso para descargar
- Sea de dominio público
- Esté permitido por las políticas de la plataforma

### ¿El bot almacena mis videos?

No. Los videos se descargan temporalmente, se envían a tu chat de Telegram y luego se eliminan automáticamente del servidor.

## Instalación

### ¿Necesito conocimientos de programación?

No necesariamente. Si sabes usar comandos básicos de terminal y seguir instrucciones, puedes instalarlo. El script `install.sh` automatiza la mayoría del proceso.

### ¿Puedo instalar el bot en Windows?

Sí, pero necesitas:
- Docker Desktop para Windows
- WSL2 (Windows Subsystem for Linux)

O puedes usar un VPS Linux que es más simple.

### ¿Qué especificaciones de servidor necesito?

**Mínimo:**
- 1 CPU core
- 1GB RAM
- 10GB disco
- Conexión a internet estable

**Recomendado:**
- 2 CPU cores
- 2GB RAM
- 20GB disco
- 10Mbps+ de ancho de banda

### ¿Dónde puedo alojar el bot?

Opciones populares:
- **VPS económicos**: DigitalOcean, Linode, Vultr ($5-10/mes)
- **Cloud gratuito**: Oracle Cloud (siempre gratis con límites)
- **Servidor casero**: Raspberry Pi 4, PC viejo
- **Hosting compartido**: Si soporta Docker

## Uso

### ¿Cómo elimino la marca de agua de TikTok?

El bot lo hace automáticamente usando yt-dlp, que intenta obtener la versión sin marca de agua directamente de los servidores de TikTok.

### ¿Por qué algunos videos de TikTok aún tienen marca de agua?

Algunos videos no tienen versión sin marca de agua disponible en los servidores de TikTok. Esto depende de:
- Configuración de privacidad del creador
- Región del video
- Tipo de cuenta

### ¿Puedo descargar videos privados?

No. El bot solo puede descargar videos públicamente accesibles.

### ¿Cuál es el límite de tamaño?

Por defecto, 50MB (limitación de Telegram). Puedes aumentarlo en el código, pero Telegram no permitirá enviar archivos mayores a 2GB.

### ¿Puedo descargar playlists completas?

No en la versión actual. El bot descarga videos individuales. Puedes enviar múltiples enlaces uno por uno.

### ¿Por qué algunos videos tardan mucho en descargar?

Factores que afectan la velocidad:
- Tamaño del video
- Calidad seleccionada
- Velocidad de internet del servidor
- Carga del servidor de origen

## Problemas Técnicos

### El bot no responde

**Soluciones:**

```bash
# 1. Verificar que está corriendo
docker ps

# 2. Ver los logs
docker-compose logs -f

# 3. Reiniciar el bot
docker-compose restart

# 4. Verificar el token
cat .env
```

### Error: "Max filesize exceeded"

El video es muy grande. Opciones:
1. Pedir una calidad menor al bot (necesitas modificar el código)
2. Aumentar el límite en `bot.py`:
   ```python
   'max_filesize': 100 * 1024 * 1024,  # 100MB
   ```

### Error: "This video is unavailable"

Posibles causas:
- Video privado o eliminado
- Restricción geográfica
- Restricción de edad
- Problemas con yt-dlp (intenta actualizar)

### El bot descarga pero no envía el video

Revisa:
1. Permisos del directorio `/downloads`
2. Espacio en disco disponible
3. Logs para ver el error específico

### Error: "Unable to extract video data"

La plataforma cambió su formato. Solución:
```bash
# Actualizar yt-dlp en el contenedor
docker-compose exec telegram-downloader-bot pip install --upgrade yt-dlp
```

O reconstruir la imagen:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Configuración

### ¿Cómo cambio la calidad de descarga?

Edita `bot.py` en la función `download_video()`:

```python
# Para 720p máximo
ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'

# Para 480p máximo
ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best'

# Mejor calidad disponible
ydl_opts['format'] = 'bestvideo+bestaudio/best'
```

### ¿Cómo limito quién puede usar el bot?

Agrega esta lista en `bot.py`:

```python
# Al inicio del archivo
AUTHORIZED_USERS = [123456789, 987654321]  # Tus IDs de Telegram

# En la función handle_url
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ No autorizado")
        return
    # ... resto del código
```

Para obtener tu ID de Telegram:
1. Busca @userinfobot en Telegram
2. Envíale `/start`
3. Te dará tu ID

### ¿Cómo agrego más plataformas?

yt-dlp soporta [1000+ sitios](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

Para agregar uno:

```python
# En bot.py, dentro de __init__ de VideoDownloader
self.supported_platforms = {
    'tiktok': ['tiktok.com', 'vm.tiktok.com'],
    'youtube': ['youtube.com', 'youtu.be'],
    'twitter': ['twitter.com', 'x.com'],
    'instagram': ['instagram.com'],
    'facebook': ['facebook.com', 'fb.watch'],  # Agregar nueva
    'vimeo': ['vimeo.com'],  # Agregar nueva
}
```

### ¿Puedo cambiar el puerto de Docker?

Telegram bots no usan puertos HTTP. Se comunican via API de Telegram. No necesitas exponer puertos.

## Mantenimiento

### ¿Cómo actualizo el bot?

```bash
# Si usas git
git pull

# Reconstruir
docker-compose up -d --build
```

### ¿Cómo actualizo yt-dlp?

```bash
# Método 1: Desde el contenedor
docker-compose exec telegram-downloader-bot pip install --upgrade yt-dlp

# Método 2: Reconstruir la imagen
docker-compose build --no-cache
docker-compose up -d
```

### ¿Cómo hago backup?

```bash
# Backup del código y configuración
tar -czf bot-backup-$(date +%F).tar.gz \
    bot.py \
    requirements.txt \
    Dockerfile \
    docker-compose.yml \
    .env

# Si tienes base de datos
docker-compose exec telegram-downloader-bot \
    tar -czf - /app/data > db-backup-$(date +%F).tar.gz
```

### ¿Cómo veo el uso de recursos?

```bash
# Stats en tiempo real
docker stats telegram-video-downloader

# Espacio en disco
docker system df
```

### ¿Cómo limpio archivos viejos?

```bash
# Limpiar contenedores parados
docker container prune

# Limpiar imágenes no usadas
docker image prune -a

# Limpiar todo (cuidado!)
docker system prune -a --volumes
```

## Seguridad

### ¿Es seguro mi token?

Sí, si:
- Nunca lo compartes públicamente
- Está en `.env` (que está en `.gitignore`)
- Tu servidor está protegido

Si se compromete:
1. Ve a @BotFather
2. Envía `/mybots`
3. Selecciona tu bot
4. "API Token" → "Revoke current token"
5. Actualiza tu `.env` con el nuevo token

### ¿Puedo usar HTTPS?

Los bots de Telegram ya usan HTTPS por defecto en su comunicación con los servidores de Telegram. No necesitas configurar nada adicional.

### ¿Qué datos se registran?

Por defecto, solo logs de sistema. Si quieres privacidad total:
- Desactiva logs: `logging.disable(logging.CRITICAL)`
- No implementes base de datos de tracking

## Rendimiento

### ¿Cuántos usuarios puede manejar?

Depende de tu servidor:
- **VPS básico (1GB RAM)**: 5-10 usuarios simultáneos
- **VPS medio (2GB RAM)**: 20-30 usuarios simultáneos
- **Servidor dedicado**: 100+ usuarios

### ¿Cómo mejoro la velocidad?

1. **Servidor más rápido**: Mejor CPU y red
2. **Cache de videos**: Implementar sistema de cache
3. **Calidad menor**: Descargar 720p en vez de 1080p
4. **Compresión**: Activar compresión de video

### El servidor se queda sin espacio

```bash
# Ver uso de espacio
df -h

# Limpiar descargas viejas
rm -rf ./downloads/*

# Limpiar Docker
docker system prune -a
```

## Desarrollo

### ¿Puedo agregar funcionalidades?

¡Sí! El código está diseñado para ser extensible. Algunas ideas:
- Sistema de cola para múltiples descargas
- Conversión de formato
- Subtítulos automáticos
- Estadísticas de uso
- Base de datos de favoritos

### ¿Dónde reporto bugs?

Si encuentras un problema:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica que yt-dlp esté actualizado
3. Intenta con otro video de la misma plataforma
4. Documenta el error completo

### ¿Puedo contribuir?

¡Por supuesto! Algunas áreas donde puedes ayudar:
- Agregar nuevas plataformas
- Mejorar la documentación
- Optimizar el código
- Crear tests
- Traducir a otros idiomas

## Comparación con Alternativas

### ¿Por qué usar este bot en vez de servicios web?

**Ventajas:**
- ✅ Privacidad total (auto-alojado)
- ✅ Sin límites de uso
- ✅ Sin publicidad
- ✅ Gratis (después del VPS)
- ✅ Personalizable

**Desventajas:**
- ❌ Requiere servidor
- ❌ Mantenimiento técnico
- ❌ Costo del hosting

### ¿Es mejor que descargar desde navegador?

**Ventajas del bot:**
- Más rápido (un solo mensaje)
- Automático (sin marca de agua)
- Desde móvil fácilmente
- Historial en Telegram

---

## ¿No encuentras tu pregunta?

Revisa:
1. README.md - Documentación principal
2. ADVANCED.md - Configuración avanzada
3. Los logs del bot - Muchas veces el error está ahí

O busca ayuda en:
- Documentación de yt-dlp: https://github.com/yt-dlp/yt-dlp
- python-telegram-bot: https://docs.python-telegram-bot.org/
