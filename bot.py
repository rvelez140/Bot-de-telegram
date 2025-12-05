import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import re
import math
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot (desde variable de entorno)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DOWNLOAD_DIR = '/downloads'

# Límites de Telegram
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB en bytes
CHUNK_SIZE = 1900 * 1024 * 1024     # 1.9GB por parte (margen de seguridad)

# Asegurar que el directorio de descargas existe
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class MediaDownloader:
    def __init__(self):
        self.supported_platforms = {
            'tiktok': ['tiktok.com', 'vm.tiktok.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'twitter': ['twitter.com', 'x.com', 't.co'],
            'instagram': ['instagram.com']
        }
    
    def get_platform(self, url):
        """Detecta la plataforma del URL"""
        url_lower = url.lower()
        for platform, domains in self.supported_platforms.items():
            if any(domain in url_lower for domain in domains):
                return platform
        return None
    
    def split_video(self, filename, chunk_size=CHUNK_SIZE):
        """Divide un video en partes si es muy grande"""
        file_size = os.path.getsize(filename)
        
        if file_size <= MAX_FILE_SIZE:
            return [filename]
        
        # Calcular número de partes necesarias
        num_parts = math.ceil(file_size / chunk_size)
        
        logger.info(f"Archivo de {file_size / (1024*1024):.2f}MB, dividiendo en {num_parts} partes")
        
        base_name = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        
        parts = []
        
        try:
            import subprocess
            
            # Usar ffmpeg para dividir el video
            for i in range(num_parts):
                start_time = i * (chunk_size / (file_size / self.get_duration(filename)))
                part_filename = f"{base_name}_parte{i+1}de{num_parts}{ext}"
                
                cmd = [
                    'ffmpeg', '-i', filename,
                    '-ss', str(start_time),
                    '-t', str(chunk_size / (file_size / self.get_duration(filename))),
                    '-c', 'copy',
                    '-avoid_negative_ts', '1',
                    part_filename
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                parts.append(part_filename)
            
            return parts
            
        except Exception as e:
            logger.error(f"Error dividiendo video: {e}")
            # Si falla, devolver archivo original
            return [filename]
    
    def get_duration(self, filename):
        """Obtiene la duración del video en segundos"""
        try:
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', filename],
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip())
        except:
            return 3600  # Default 1 hora si no se puede obtener
    
    async def download_image(self, url, chat_id):
        """Descarga imágenes"""
        output_path = os.path.join(DOWNLOAD_DIR, f'{chat_id}_%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'quiet': False,
            'cookiefile': '/app/cookies.txt',  # Soporte para cuentas privadas
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Si no existe con la extensión esperada, buscar variantes
                if not os.path.exists(filename):
                    base = os.path.splitext(filename)[0]
                    for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                        alt_filename = base + ext
                        if os.path.exists(alt_filename):
                            filename = alt_filename
                            break
                
                return {
                    'success': True,
                    'filename': filename,
                    'title': info.get('title', 'image'),
                    'type': 'image'
                }
        except Exception as e:
            logger.error(f"Error descargando imagen: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def download_video(self, url, chat_id):
        """Descarga el video usando yt-dlp"""
        output_path = os.path.join(DOWNLOAD_DIR, f'{chat_id}_%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            # Soporte para cuentas privadas
            'cookiefile': '/app/cookies.txt',  # Si existe, usar cookies
            # Headers para evitar bloqueos
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
        }
        
        platform = self.get_platform(url)
        
        # Configuraciones específicas por plataforma
        if platform == 'tiktok':
            ydl_opts['format'] = 'best[ext=mp4]/best'
            # TikTok específico
            ydl_opts['extractor_args'] = {'tiktok': {'api_hostname': 'api22-normal-c-useast2a.tiktokv.com'}}
        elif platform == 'instagram':
            ydl_opts['format'] = 'best[ext=mp4]/best'
            # Instagram necesita cookies para cuentas privadas
        elif platform == 'youtube':
            ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif platform == 'twitter':
            # Twitter/X configuración mejorada
            ydl_opts['format'] = 'best'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Si el archivo no existe con la extensión esperada, buscar variantes
                if not os.path.exists(filename):
                    base = os.path.splitext(filename)[0]
                    for ext in ['.mp4', '.mkv', '.webm', '.mov']:
                        alt_filename = base + ext
                        if os.path.exists(alt_filename):
                            filename = alt_filename
                            break
                
                # Verificar tamaño y dividir si es necesario
                file_size = os.path.getsize(filename)
                parts = []
                
                if file_size > MAX_FILE_SIZE:
                    logger.info(f"Archivo muy grande ({file_size / (1024*1024):.2f}MB), dividiendo...")
                    parts = self.split_video(filename)
                else:
                    parts = [filename]
                
                return {
                    'success': True,
                    'filename': filename,
                    'parts': parts,
                    'title': info.get('title', 'video'),
                    'platform': platform,
                    'file_size': file_size,
                    'type': 'video'
                }
        except Exception as e:
            logger.error(f"Error descargando video: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

downloader = MediaDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_message = """
🎥 *Bot de Descarga de Videos e Imágenes*

Envíame un enlace (o varios) de cualquiera de estas plataformas:
✅ TikTok (sin marca de agua)
✅ YouTube (hasta 1080p)
✅ X (Twitter)
✅ Instagram (posts, reels e imágenes)

*Características especiales:*
📹 Videos grandes (>2GB) se dividen automáticamente en partes
🖼️ Soporte para descargar imágenes
📎 Envía múltiples enlaces a la vez (uno por línea)

*Ejemplos:*
• Un enlace: `https://tiktok.com/...`
• Varios enlaces:
```
https://tiktok.com/...
https://youtube.com/...
https://instagram.com/...
```

*Comandos disponibles:*
/start - Mostrar este mensaje
/help - Ayuda
/platforms - Ver plataformas soportadas
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = """
📖 *Ayuda*

*Cómo usar:*
1. Copia el enlace del video o imagen que quieres descargar
2. Envíamelo directamente
3. Espera mientras lo proceso
4. Recibirás el archivo sin marca de agua (cuando sea posible)

*Características:*
🎥 Videos: Hasta 2GB, automáticamente divididos en partes si son más grandes
🖼️ Imágenes: Descarga en máxima calidad
📎 Múltiples enlaces: Envía varios enlaces a la vez (uno por línea)

*Ejemplos:*

Un enlace:
`https://www.tiktok.com/@usuario/video/123`

Varios enlaces:
```
https://www.youtube.com/watch?v=abc123
https://www.instagram.com/p/xyz789/
https://twitter.com/user/status/456
```

*Limitaciones:*
- Videos >2GB se dividen en partes de ~1.9GB
- Algunos videos pueden tener restricciones de copyright
- Videos muy largos pueden tardar más en procesarse

*Nota:* Para TikTok, intento obtener la versión sin marca de agua automáticamente.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def platforms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /platforms"""
    platforms_text = """
🌐 *Plataformas Soportadas*

✅ *TikTok*
   - tiktok.com
   - vm.tiktok.com
   - Sin marca de agua (cuando está disponible)
   - Videos e imágenes

✅ *YouTube*
   - youtube.com
   - youtu.be
   - Hasta 1080p
   - Videos >2GB se dividen automáticamente

✅ *X (Twitter)*
   - twitter.com
   - x.com
   - Videos e imágenes

✅ *Instagram*
   - instagram.com
   - Posts, Reels e Imágenes
   - Stories (si están disponibles públicamente)

*Funciones especiales:*
📹 División automática de videos grandes
🖼️ Descarga de imágenes en máxima calidad
📎 Procesamiento múltiple de enlaces
    """
    await update.message.reply_text(platforms_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja URLs enviados por el usuario (uno o múltiples)"""
    message_text = update.message.text.strip()
    
    # Extraer todos los URLs del mensaje
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    urls = url_pattern.findall(message_text)
    
    if not urls:
        await update.message.reply_text(
            "❌ No se encontraron enlaces válidos.\n"
            "Envía uno o más enlaces de video/imagen."
        )
        return
    
    # Filtrar URLs soportados
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        platform = downloader.get_platform(url)
        if platform:
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    if not valid_urls:
        await update.message.reply_text(
            "❌ Ninguno de los enlaces es de una plataforma soportada.\n"
            "Usa /platforms para ver las plataformas disponibles."
        )
        return
    
    # Informar al usuario
    total = len(valid_urls)
    status_msg = f"📥 Procesando {total} enlace(s)...\n"
    
    if invalid_urls:
        status_msg += f"⚠️ {len(invalid_urls)} enlace(s) no soportado(s) serán ignorados.\n"
    
    processing_msg = await update.message.reply_text(status_msg)
    
    # Procesar cada URL
    for index, url in enumerate(valid_urls, 1):
        try:
            platform = downloader.get_platform(url)
            
            # Actualizar mensaje de progreso
            await processing_msg.edit_text(
                f"⏳ Procesando {index}/{total} - {platform.upper()}...\n"
                f"URL: {url[:50]}..."
            )
            
            # Determinar si es imagen o video (intentar como video primero)
            result = await downloader.download_video(url, update.effective_chat.id)
            
            # Si falla como video, intentar como imagen
            if not result['success']:
                logger.info(f"Intentando descargar como imagen: {url}")
                result = await downloader.download_image(url, update.effective_chat.id)
            
            if not result['success']:
                await update.message.reply_text(
                    f"❌ Error [{index}/{total}] al descargar:\n"
                    f"🌐 Plataforma: {platform.upper()}\n"
                    f"❗ Error: `{result['error']}`",
                    parse_mode='Markdown'
                )
                continue
            
            # Actualizar progreso
            await processing_msg.edit_text(
                f"📤 Enviando {index}/{total}...\n"
                f"📝 {result['title'][:50]}"
            )
            
            # Enviar según el tipo
            if result.get('type') == 'image':
                # Enviar imagen
                with open(result['filename'], 'rb') as photo_file:
                    caption = f"✅ *Imagen {index}/{total}*\n\n📝 {result['title']}\n🌐 {platform.upper()}"
                    
                    await update.message.reply_photo(
                        photo=photo_file,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                
                # Eliminar archivo
                try:
                    os.remove(result['filename'])
                except:
                    pass
                    
            else:
                # Enviar video(s)
                parts = result.get('parts', [result['filename']])
                num_parts = len(parts)
                
                for part_index, part_file in enumerate(parts, 1):
                    with open(part_file, 'rb') as video_file:
                        file_size_mb = os.path.getsize(part_file) / (1024 * 1024)
                        
                        caption = f"✅ *Video {index}/{total}*"
                        if num_parts > 1:
                            caption += f" - *Parte {part_index}/{num_parts}*"
                        caption += f"\n\n📝 {result['title']}\n🌐 {platform.upper()}"
                        if result.get('platform') == 'tiktok':
                            caption += "\n🚫 Sin marca de agua"
                        caption += f"\n💾 Tamaño: {file_size_mb:.1f}MB"
                        
                        await update.message.reply_video(
                            video=video_file,
                            caption=caption,
                            parse_mode='Markdown',
                            supports_streaming=True
                        )
                    
                    # Eliminar parte
                    try:
                        os.remove(part_file)
                    except:
                        pass
                
                # Si había archivo original (antes de dividir), eliminarlo también
                if num_parts > 1 and os.path.exists(result['filename']):
                    try:
                        os.remove(result['filename'])
                    except:
                        pass
            
            # Pequeña pausa entre archivos para no saturar
            if index < total:
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Error procesando URL {index}/{total}: {str(e)}")
            await update.message.reply_text(
                f"❌ Error inesperado [{index}/{total}]:\n`{str(e)}`",
                parse_mode='Markdown'
            )
            continue
    
    # Eliminar mensaje de procesamiento
    try:
        await processing_msg.delete()
    except:
        pass
    
    # Mensaje final
    if total > 1:
        await update.message.reply_text(
            f"✅ *Procesamiento completado*\n\n"
            f"📊 Total: {total} archivo(s)\n"
            f"✅ Exitosos: {len(valid_urls)}\n"
            f"❌ Fallidos: {total - len(valid_urls)}",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja errores"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Función principal"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado")
        return
    
    # Crear aplicación
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("platforms", platforms))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_error_handler(error_handler)
    
    # Iniciar bot
    logger.info("Bot iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
