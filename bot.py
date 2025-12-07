import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import re
import whisper
import subprocess
from datetime import datetime, timedelta

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot (desde variable de entorno)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DOWNLOAD_DIR = '/downloads'
WHISPER_MODEL = None  # Se carga bajo demanda

# Asegurar que el directorio de descargas existe
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Almacenar datos temporales de usuario (URL y tiempo de expiración)
user_data_store = {}

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

    async def extract_audio(self, video_path):
        """Extrae el audio de un video"""
        try:
            audio_path = video_path.rsplit('.', 1)[0] + '.mp3'
            command = [
                'ffmpeg', '-i', video_path,
                '-vn', '-acodec', 'libmp3lame',
                '-ab', '192k', '-ar', '44100',
                '-y', audio_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return {'success': True, 'audio_path': audio_path}
        except Exception as e:
            logger.error(f"Error extrayendo audio: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def transcribe_audio(self, audio_path):
        """Transcribe audio usando Whisper"""
        global WHISPER_MODEL
        try:
            # Cargar modelo si no está cargado
            if WHISPER_MODEL is None:
                logger.info("Cargando modelo Whisper (puede tomar unos minutos)...")
                WHISPER_MODEL = whisper.load_model("base")

            logger.info(f"Transcribiendo audio: {audio_path}")
            result = WHISPER_MODEL.transcribe(audio_path, language='es', fp16=False)

            return {
                'success': True,
                'text': result['text'],
                'language': result.get('language', 'es')
            }
        except Exception as e:
            logger.error(f"Error transcribiendo audio: {str(e)}")
            return {'success': False, 'error': str(e)}

downloader = VideoDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_message = """
🎥 *Bot de Descarga y Transcripción de Videos*

Envíame un enlace de cualquiera de estas plataformas:
✅ TikTok (sin marca de agua cuando sea posible)
✅ YouTube
✅ X (Twitter)
✅ Instagram

*¿Qué puedo hacer?*
📥 Descargar videos
📝 Transcribir el audio a texto
📥+📝 Ambas cosas

Simplemente envía el enlace y tendrás *30 segundos* para elegir qué hacer.

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
3. Elige una opción en 30 segundos:
   📥 *Solo Descargar* - Recibe el video
   📝 *Solo Transcribir* - Recibe el texto del audio
   📥+📝 *Ambos* - Recibe video y transcripción

*Características:*
✅ Descarga de videos sin marca de agua (TikTok)
✅ Transcripción automática de audio a texto
✅ Soporte para múltiples idiomas
✅ División automática de transcripciones largas

*Limitaciones:*
- Tamaño máximo: 50MB (limitación de Telegram)
- Algunos videos pueden tener restricciones de copyright
- La transcripción puede tomar varios minutos

*Nota:* La transcripción usa IA para convertir el audio a texto con alta precisión.
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

    # Guardar URL en el almacén temporal (expira en 30 segundos)
    user_id = update.effective_user.id
    expiration_time = datetime.now() + timedelta(seconds=30)
    user_data_store[user_id] = {
        'url': url,
        'platform': platform,
        'expires_at': expiration_time
    }

    # Crear botones inline
    keyboard = [
        [
            InlineKeyboardButton("📥 Solo Descargar", callback_data=f"download_{user_id}"),
            InlineKeyboardButton("📝 Solo Transcribir", callback_data=f"transcribe_{user_id}")
        ],
        [
            InlineKeyboardButton("📥+📝 Descargar y Transcribir", callback_data=f"both_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎬 Video detectado de *{platform.upper()}*\n\n"
        "¿Qué deseas hacer con este video?\n"
        "⏱️ _Tienes 30 segundos para elegir_",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los callbacks de los botones inline"""
    query = update.callback_query
    await query.answer()

    # Parsear el callback data
    action, user_id_str = query.data.split('_', 1)
    user_id = int(user_id_str)

    # Verificar que el usuario que presionó el botón es el correcto
    if query.from_user.id != user_id:
        await query.answer("⚠️ Este botón no es para ti", show_alert=True)
        return

    # Verificar si los datos aún están disponibles
    if user_id not in user_data_store:
        await query.edit_message_text(
            "❌ El tiempo para seleccionar ha expirado (30 segundos).\n"
            "Por favor, envía el enlace nuevamente."
        )
        return

    user_data = user_data_store[user_id]

    # Verificar expiración
    if datetime.now() > user_data['expires_at']:
        del user_data_store[user_id]
        await query.edit_message_text(
            "❌ El tiempo para seleccionar ha expirado (30 segundos).\n"
            "Por favor, envía el enlace nuevamente."
        )
        return

    url = user_data['url']
    platform = user_data['platform']
    chat_id = query.message.chat_id

    # Limpiar datos del almacén
    del user_data_store[user_id]

    # Procesar según la acción seleccionada
    if action == 'download':
        await process_download_only(query, url, platform, chat_id)
    elif action == 'transcribe':
        await process_transcribe_only(query, url, platform, chat_id)
    elif action == 'both':
        await process_both(query, url, platform, chat_id)

async def process_download_only(query, url, platform, chat_id):
    """Procesa solo la descarga del video"""
    await query.edit_message_text(
        f"⏳ Descargando video de *{platform.upper()}*...\n"
        "Esto puede tomar unos momentos.",
        parse_mode='Markdown'
    )

    try:
        # Descargar video
        result = await downloader.download_video(url, chat_id)

        if not result['success']:
            await query.edit_message_text(
                f"❌ Error al descargar el video:\n`{result['error']}`",
                parse_mode='Markdown'
            )
            return

        # Enviar video
        await query.edit_message_text("📤 Enviando video...")

        with open(result['filename'], 'rb') as video_file:
            caption = f"✅ *{result['title']}*\n\n🌐 Plataforma: {result['platform'].upper()}"
            if result['platform'] == 'tiktok':
                caption += "\n🚫 Sin marca de agua"

            await query.message.reply_video(
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
        await query.delete_message()

    except Exception as e:
        logger.error(f"Error procesando video: {str(e)}")
        await query.edit_message_text(
            f"❌ Error al procesar el video:\n`{str(e)}`\n\n"
            "El video puede ser muy grande o tener restricciones.",
            parse_mode='Markdown'
        )

async def process_transcribe_only(query, url, platform, chat_id):
    """Procesa solo la transcripción del video"""
    await query.edit_message_text(
        f"⏳ Descargando y transcribiendo video de *{platform.upper()}*...\n"
        "🎙️ Esto puede tomar varios minutos.",
        parse_mode='Markdown'
    )

    try:
        # Descargar video
        result = await downloader.download_video(url, chat_id)

        if not result['success']:
            await query.edit_message_text(
                f"❌ Error al descargar el video:\n`{result['error']}`",
                parse_mode='Markdown'
            )
            return

        # Extraer audio
        await query.edit_message_text("🎵 Extrayendo audio del video...")
        audio_result = await downloader.extract_audio(result['filename'])

        if not audio_result['success']:
            await query.edit_message_text(
                f"❌ Error al extraer audio:\n`{audio_result['error']}`",
                parse_mode='Markdown'
            )
            # Limpiar archivo de video
            try:
                os.remove(result['filename'])
            except:
                pass
            return

        # Transcribir audio
        await query.edit_message_text(
            "📝 Transcribiendo audio...\n"
            "⏱️ Esto puede tomar varios minutos dependiendo de la duración del video."
        )
        transcription_result = await downloader.transcribe_audio(audio_result['audio_path'])

        if not transcription_result['success']:
            await query.edit_message_text(
                f"❌ Error al transcribir:\n`{transcription_result['error']}`",
                parse_mode='Markdown'
            )
            # Limpiar archivos
            try:
                os.remove(result['filename'])
                os.remove(audio_result['audio_path'])
            except:
                pass
            return

        # Enviar transcripción
        transcription_text = f"📝 *Transcripción de: {result['title']}*\n\n"
        transcription_text += f"🌐 Plataforma: {platform.upper()}\n"
        transcription_text += f"🗣️ Idioma detectado: {transcription_result['language']}\n\n"
        transcription_text += "─────────────────────\n\n"
        transcription_text += transcription_result['text']

        # Telegram tiene límite de 4096 caracteres por mensaje
        if len(transcription_text) > 4000:
            # Enviar en múltiples mensajes
            await query.message.reply_text(
                f"📝 *Transcripción de: {result['title']}*\n\n"
                f"🌐 Plataforma: {platform.upper()}\n"
                f"🗣️ Idioma: {transcription_result['language']}\n\n"
                "⚠️ La transcripción es muy larga, se enviará en varios mensajes.",
                parse_mode='Markdown'
            )

            # Dividir el texto en chunks
            text_chunks = [transcription_result['text'][i:i+4000]
                          for i in range(0, len(transcription_result['text']), 4000)]

            for i, chunk in enumerate(text_chunks, 1):
                await query.message.reply_text(
                    f"📄 Parte {i}/{len(text_chunks)}:\n\n{chunk}"
                )
        else:
            await query.message.reply_text(transcription_text, parse_mode='Markdown')

        # Limpiar archivos
        try:
            os.remove(result['filename'])
            os.remove(audio_result['audio_path'])
        except:
            pass

        await query.delete_message()

    except Exception as e:
        logger.error(f"Error en transcripción: {str(e)}")
        await query.edit_message_text(
            f"❌ Error al procesar:\n`{str(e)}`",
            parse_mode='Markdown'
        )

async def process_both(query, url, platform, chat_id):
    """Procesa descarga y transcripción del video"""
    await query.edit_message_text(
        f"⏳ Descargando video de *{platform.upper()}*...\n"
        "📥 Descargando y 📝 Transcribiendo",
        parse_mode='Markdown'
    )

    video_path = None
    audio_path = None

    try:
        # Descargar video
        result = await downloader.download_video(url, chat_id)

        if not result['success']:
            await query.edit_message_text(
                f"❌ Error al descargar el video:\n`{result['error']}`",
                parse_mode='Markdown'
            )
            return

        video_path = result['filename']

        # Enviar video primero
        await query.edit_message_text("📤 Enviando video...")

        with open(result['filename'], 'rb') as video_file:
            caption = f"✅ *{result['title']}*\n\n🌐 Plataforma: {result['platform'].upper()}"
            if result['platform'] == 'tiktok':
                caption += "\n🚫 Sin marca de agua"

            await query.message.reply_video(
                video=video_file,
                caption=caption,
                parse_mode='Markdown',
                supports_streaming=True
            )

        # Extraer audio
        await query.edit_message_text("🎵 Extrayendo audio para transcripción...")
        audio_result = await downloader.extract_audio(result['filename'])

        if not audio_result['success']:
            await query.edit_message_text(
                "✅ Video enviado correctamente.\n\n"
                f"❌ Error al extraer audio para transcripción:\n`{audio_result['error']}`",
                parse_mode='Markdown'
            )
            try:
                os.remove(result['filename'])
            except:
                pass
            return

        audio_path = audio_result['audio_path']

        # Transcribir audio
        await query.edit_message_text(
            "📝 Transcribiendo audio...\n"
            "⏱️ Esto puede tomar varios minutos."
        )
        transcription_result = await downloader.transcribe_audio(audio_result['audio_path'])

        if not transcription_result['success']:
            await query.edit_message_text(
                "✅ Video enviado correctamente.\n\n"
                f"❌ Error al transcribir:\n`{transcription_result['error']}`",
                parse_mode='Markdown'
            )
            try:
                os.remove(result['filename'])
                os.remove(audio_result['audio_path'])
            except:
                pass
            return

        # Enviar transcripción
        transcription_text = f"📝 *Transcripción de: {result['title']}*\n\n"
        transcription_text += f"🌐 Plataforma: {platform.upper()}\n"
        transcription_text += f"🗣️ Idioma detectado: {transcription_result['language']}\n\n"
        transcription_text += "─────────────────────\n\n"
        transcription_text += transcription_result['text']

        if len(transcription_text) > 4000:
            await query.message.reply_text(
                f"📝 *Transcripción de: {result['title']}*\n\n"
                f"🌐 Plataforma: {platform.upper()}\n"
                f"🗣️ Idioma: {transcription_result['language']}\n\n"
                "⚠️ La transcripción es muy larga, se enviará en varios mensajes.",
                parse_mode='Markdown'
            )

            text_chunks = [transcription_result['text'][i:i+4000]
                          for i in range(0, len(transcription_result['text']), 4000)]

            for i, chunk in enumerate(text_chunks, 1):
                await query.message.reply_text(
                    f"📄 Parte {i}/{len(text_chunks)}:\n\n{chunk}"
                )
        else:
            await query.message.reply_text(transcription_text, parse_mode='Markdown')

        await query.delete_message()

    except Exception as e:
        logger.error(f"Error procesando video completo: {str(e)}")
        await query.edit_message_text(
            f"❌ Error al procesar:\n`{str(e)}`",
            parse_mode='Markdown'
        )
    finally:
        # Limpiar archivos
        try:
            if video_path:
                os.remove(video_path)
            if audio_path:
                os.remove(audio_path)
        except:
            pass

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
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_error_handler(error_handler)
    
    # Iniciar bot
    logger.info("Bot iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
