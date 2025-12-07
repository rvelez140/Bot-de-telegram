import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import re

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot (desde variable de entorno)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DOWNLOAD_DIR = '/downloads'

# Asegurar que el directorio de descargas existe
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class VideoDownloader:
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
            # Opciones para TikTok sin marca de agua
            'nocheckcertificate': True,
            # Limitar tamaño para Telegram (50MB)
            'max_filesize': 50 * 1024 * 1024,
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
            # Intenta obtener versión sin marca de agua
            ydl_opts['format'] = 'best[ext=mp4]/best'
        elif platform == 'instagram':
            ydl_opts['format'] = 'best[ext=mp4]/best'
        elif platform == 'youtube':
            # Para YouTube, obtener mejor calidad hasta 1080p
            ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif platform == 'twitter':
            # Configuración específica para Twitter/X
            ydl_opts['format'] = 'best[ext=mp4]/best'
            # Añadir extractor args específicos para Twitter
            ydl_opts['extractor_args'] = {
                'twitter': {
                    'api': ['syndication', 'graphql']
                }
            }
            # Intentar diferentes métodos de extracción
            ydl_opts['cookiesfrombrowser'] = None  # No usar cookies del navegador por defecto
            # Forzar IPv4 para evitar problemas de conexión
            ydl_opts['source_address'] = '0.0.0.0'
        
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
                
                return {
                    'success': True,
                    'filename': filename,
                    'title': info.get('title', 'video'),
                    'platform': platform
                }
        except Exception as e:
            logger.error(f"Error descargando video: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

downloader = VideoDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_message = """
🎥 *Bot de Descarga de Videos*

Envíame un enlace de cualquiera de estas plataformas:
✅ TikTok (sin marca de agua cuando sea posible)
✅ YouTube
✅ X (Twitter)
✅ Instagram

Simplemente envía el enlace y yo me encargaré del resto.

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
1. Copia el enlace del video que quieres descargar
2. Envíamelo directamente
3. Espera mientras lo proceso
4. Recibirás el video sin marca de agua (cuando sea posible)

*Limitaciones:*
- Tamaño máximo: 50MB (limitación de Telegram)
- Algunos videos pueden tener restricciones de copyright

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

✅ *YouTube*
   - youtube.com
   - youtu.be
   - Hasta 1080p

✅ *X (Twitter)*
   - twitter.com
   - x.com

✅ *Instagram*
   - instagram.com
   - Posts y Reels
    """
    await update.message.reply_text(platforms_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja URLs enviados por el usuario"""
    url = update.message.text.strip()
    
    # Validar que sea un URL
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    if not url_pattern.match(url):
        await update.message.reply_text(
            "❌ Por favor envía un enlace válido de video."
        )
        return
    
    # Detectar plataforma
    platform = downloader.get_platform(url)
    if not platform:
        await update.message.reply_text(
            "❌ Esta plataforma no está soportada.\n"
            "Usa /platforms para ver las plataformas disponibles."
        )
        return
    
    # Mensaje de procesamiento
    processing_msg = await update.message.reply_text(
        f"⏳ Descargando video de *{platform.upper()}*...\n"
        "Esto puede tomar unos momentos.",
        parse_mode='Markdown'
    )
    
    try:
        # Descargar video
        result = await downloader.download_video(url, update.effective_chat.id)
        
        if not result['success']:
            await processing_msg.edit_text(
                f"❌ Error al descargar el video:\n`{result['error']}`",
                parse_mode='Markdown'
            )
            return
        
        # Enviar video
        await processing_msg.edit_text("📤 Enviando video...")
        
        with open(result['filename'], 'rb') as video_file:
            caption = f"✅ *{result['title']}*\n\n🌐 Plataforma: {result['platform'].upper()}"
            if result['platform'] == 'tiktok':
                caption += "\n🚫 Sin marca de agua"
            
            await update.message.reply_video(
                video=video_file,
                caption=caption,
                parse_mode='Markdown',
                supports_streaming=True
            )
        
        # Eliminar archivo temporal
        try:
            os.remove(result['filename'])
        except:
            pass
        
        # Eliminar mensaje de procesamiento
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Error procesando video: {str(e)}")
        await processing_msg.edit_text(
            f"❌ Error al procesar el video:\n`{str(e)}`\n\n"
            "El video puede ser muy grande o tener restricciones.",
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
