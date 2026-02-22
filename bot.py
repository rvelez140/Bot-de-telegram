import os
import logging
import asyncio
import math
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
import yt_dlp
import re
import whisper
import subprocess
import json
import tempfile
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

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
DATABASE_PATH = os.getenv('BOT_DATABASE_PATH', os.path.join(DOWNLOAD_DIR, 'bot_sessions.db'))
TWITTER_COOKIE_TTL_HOURS = int(os.getenv('TWITTER_COOKIE_TTL_HOURS', '48'))

# Límites de Telegram
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB en bytes
CHUNK_SIZE = 1900 * 1024 * 1024     # 1.9GB por parte (margen de seguridad)

# Asegurar que el directorio de descargas existe
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Almacenar datos temporales de usuario (URL y tiempo de expiración)
user_data_store = {}

# Almacenar cookies de X/Twitter por usuario
user_twitter_cookies = {}

# Estados para el ConversationHandler de login
WAITING_USERNAME, WAITING_PASSWORD = range(2)


def log_event(event, **kwargs):
    """Logging estructurado para facilitar observabilidad."""
    payload = {'event': event, **kwargs}
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))


def init_bot_db():
    """Inicializa la base de datos local para persistencia de sesiones."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS twitter_sessions (
            user_id INTEGER PRIMARY KEY,
            cookies TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_twitter_session(user_id, cookies):
    expires_at = datetime.utcnow() + timedelta(hours=TWITTER_COOKIE_TTL_HOURS)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO twitter_sessions (user_id, cookies, expires_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            cookies=excluded.cookies,
            created_at=CURRENT_TIMESTAMP,
            expires_at=excluded.expires_at
        ''',
        (user_id, cookies, expires_at.isoformat())
    )
    conn.commit()
    conn.close()


def load_twitter_session(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT cookies, expires_at FROM twitter_sessions WHERE user_id = ?',
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    cookies, expires_at = row
    if datetime.utcnow() >= datetime.fromisoformat(expires_at):
        delete_twitter_session(user_id)
        return None

    return cookies


def delete_twitter_session(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM twitter_sessions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


def purge_expired_sessions():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM twitter_sessions WHERE expires_at <= ?', (datetime.utcnow().isoformat(),))
    conn.commit()
    conn.close()


def safe_remove(path):
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.warning(f"No se pudo eliminar archivo temporal {path}: {e}")

async def generate_twitter_cookies(username, password):
    """Genera cookies de X/Twitter usando Playwright"""
    try:
        async with async_playwright() as p:
            # Usar chromium con headless
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            # Ir a la página de login de X/Twitter
            await page.goto('https://twitter.com/i/flow/login', wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)

            # Esperar e ingresar username/email
            try:
                username_input = await page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
                await username_input.fill(username)
                await asyncio.sleep(1)

                # Click en "Next"
                next_button = await page.wait_for_selector('button:has-text("Next"), button:has-text("Siguiente")', timeout=5000)
                await next_button.click()
                await asyncio.sleep(2)

                # Esperar e ingresar password
                password_input = await page.wait_for_selector('input[name="password"], input[type="password"]', timeout=10000)
                await password_input.fill(password)
                await asyncio.sleep(1)

                # Click en "Log in"
                login_button = await page.wait_for_selector('button[data-testid="LoginForm_Login_Button"]', timeout=5000)
                await login_button.click()
                await asyncio.sleep(3)

                # Esperar a que cargue la página principal (verificar que el login fue exitoso)
                try:
                    await page.wait_for_selector('[data-testid="primaryColumn"]', timeout=15000)
                except Exception:
                    # Si no aparece el elemento esperado, puede que requiera verificación adicional
                    pass

                # Obtener cookies
                cookies = await context.cookies()

                await browser.close()

                # Convertir cookies a formato Netscape
                cookies_txt = "# Netscape HTTP Cookie File\n"
                cookies_txt += "# This file was generated by the bot for user authentication\n\n"

                for cookie in cookies:
                    domain = cookie.get('domain', '')
                    flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                    path = cookie.get('path', '/')
                    secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                    expiration = str(int(cookie.get('expires', -1)))
                    name = cookie.get('name', '')
                    value = cookie.get('value', '')

                    cookies_txt += f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n"

                return {
                    'success': True,
                    'cookies': cookies_txt,
                    'cookies_dict': cookies
                }

            except Exception as e:
                await browser.close()
                logger.error(f"Error durante el login: {str(e)}")
                return {
                    'success': False,
                    'error': f'Error durante el proceso de login: {str(e)}'
                }

    except Exception as e:
        logger.error(f"Error generando cookies: {str(e)}")
        return {
            'success': False,
            'error': f'Error al conectar con X/Twitter: {str(e)}'
        }

class VideoDownloader:
    def __init__(self):
        self.supported_platforms = {
            'tiktok': ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com'],
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
        except Exception:
            return 3600  # Default 1 hora si no se puede obtener
    
    async def download_image(self, url, chat_id):
        """Descarga imágenes"""
        output_path = os.path.join(DOWNLOAD_DIR, f'{chat_id}_%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'quiet': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
        }
        
        # Soporte para cuentas privadas (solo si cookies.txt existe)
        cookies_file = '/app/cookies.txt'
        if os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 10:
            ydl_opts['cookiefile'] = cookies_file
        
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
    
    async def download_video(self, url, chat_id, user_id=None):
        """Descarga el video usando yt-dlp con reintentos para errores transitorios."""
        output_path = os.path.join(DOWNLOAD_DIR, f'{chat_id}_%(title)s.%(ext)s')
        cookies_file = None

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            'max_filesize': 50 * 1024 * 1024,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
        }

        platform = self.get_platform(url)

        if platform == 'tiktok':
            ydl_opts['format'] = 'best[ext=mp4]/best'
            ydl_opts['extractor_args'] = {'tiktok': {'api_hostname': 'api22-normal-c-useast2a.tiktokv.com'}}
        elif platform == 'instagram':
            ydl_opts['format'] = 'best[ext=mp4]/best'
        elif platform == 'youtube':
            ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            ydl_opts['extractor_args'] = {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']
                }
            }
            default_cookies_file = '/app/cookies.txt'
            if os.path.exists(default_cookies_file) and os.path.getsize(default_cookies_file) > 10:
                ydl_opts['cookiefile'] = default_cookies_file
        elif platform == 'twitter':
            ydl_opts['format'] = 'best[ext=mp4]/best'
            ydl_opts['extractor_args'] = {
                'twitter': {
                    'api': ['syndication', 'graphql']
                }
            }

            user_cookies = user_twitter_cookies.get(user_id)
            if user_id and not user_cookies:
                user_cookies = load_twitter_session(user_id)
                if user_cookies:
                    user_twitter_cookies[user_id] = user_cookies

            if user_id and user_cookies:
                cookies_file = os.path.join(DOWNLOAD_DIR, f'cookies_{user_id}.txt')
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    f.write(user_cookies)
                ydl_opts['cookiefile'] = cookies_file
                log_event('twitter_cookie_used', user_id=user_id)
            else:
                ydl_opts['cookiesfrombrowser'] = None

            ydl_opts['source_address'] = '0.0.0.0'

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                    if not os.path.exists(filename):
                        base = os.path.splitext(filename)[0]
                        for ext in ['.mp4', '.mkv', '.webm', '.mov']:
                            alt_filename = base + ext
                            if os.path.exists(alt_filename):
                                filename = alt_filename
                                break

                    file_size = os.path.getsize(filename)
                    if file_size > MAX_FILE_SIZE:
                        logger.info(f"Archivo muy grande ({file_size / (1024*1024):.2f}MB), dividiendo...")
                        parts = self.split_video(filename)
                    else:
                        parts = [filename]

                    log_event('download_success', platform=platform, user_id=user_id, attempt=attempt)
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
                log_event('download_error', platform=platform, user_id=user_id, attempt=attempt, error=str(e))
                if attempt < max_attempts:
                    await asyncio.sleep(1.5 * attempt)
                    continue
                return {
                    'success': False,
                    'error': str(e)
                }
            finally:
                safe_remove(cookies_file)
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

Envíame un enlace (o varios) de cualquiera de estas plataformas:
✅ TikTok (sin marca de agua)
✅ YouTube (hasta 1080p)
✅ X (Twitter) - 🔐 *¡Ahora con soporte para cuentas privadas!*
✅ Instagram (posts, reels e imágenes)

*¿Qué puedo hacer?*
📥 Descargar videos
📝 Transcribir el audio a texto
📥+📝 Ambas cosas
🔐 Descargar de cuentas privadas de X/Twitter

Simplemente envía el enlace y tendrás *30 segundos* para elegir qué hacer.

*Comandos disponibles:*
/start - Mostrar este mensaje
/help - Ayuda
/platforms - Ver plataformas soportadas
/login_twitter - Iniciar sesión en X/Twitter
/logout_twitter - Cerrar sesión de X/Twitter
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = """
📖 *Ayuda*

*Cómo usar:*
1. Copia el enlace del video o imagen que quieres descargar
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
✅ 🔐 *¡Nuevo!* Descarga de cuentas privadas de X/Twitter

*Cuentas Privadas de X/Twitter:*
Para descargar videos de cuentas privadas de X/Twitter:
1. Usa /login_twitter para iniciar sesión
2. Ingresa tu usuario y contraseña de X/Twitter
3. El bot guardará tus cookies de sesión
4. Ahora puedes descargar videos de cuentas privadas
5. Usa /logout_twitter cuando quieras cerrar sesión

*Limitaciones:*
- Videos >2GB se dividen en partes de ~1.9GB
- Algunos videos pueden tener restricciones de copyright
- La transcripción puede tomar varios minutos
- Las sesiones de X/Twitter expiran después de un tiempo

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
   - 🔐 *¡Nuevo!* Soporta cuentas privadas con /login_twitter

✅ *Instagram*
   - instagram.com
   - Posts, Reels e Imágenes
   - Stories (si están disponibles públicamente)

*Funciones especiales:*
📹 División automática de videos grandes
🖼️ Descarga de imágenes en máxima calidad
📎 Procesamiento múltiple de enlaces
🔐 Login para cuentas privadas de X/Twitter
    """
    await update.message.reply_text(platforms_text, parse_mode='Markdown')

async def login_twitter_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de login para X/Twitter"""
    user_id = update.effective_user.id

    # Verificar si ya tiene sesión activa
    session_cookies = user_twitter_cookies.get(user_id) or load_twitter_session(user_id)

    if session_cookies:
        keyboard = [
            [
                InlineKeyboardButton("✅ Sí, reemplazar", callback_data=f"replace_login_{user_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_login_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "⚠️ Ya tienes una sesión activa de X/Twitter.\n\n"
            "¿Deseas reemplazarla con una nueva sesión?",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🔐 *Login de X/Twitter*\n\n"
        "Para descargar videos de cuentas privadas, necesito tus credenciales de X/Twitter.\n\n"
        "⚠️ *Importante:*\n"
        "• Tus credenciales solo se usan para obtener cookies de sesión\n"
        "• No se guardan las contraseñas, solo las cookies de sesión\n"
        "• Las cookies expiran después de un tiempo\n"
        "• Usa /logout_twitter para eliminar tu sesión\n\n"
        "📝 Por favor, envía tu *nombre de usuario o email* de X/Twitter:\n\n"
        "_Envía /cancel para cancelar_",
        parse_mode='Markdown'
    )
    return WAITING_USERNAME

async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el username y pide la contraseña"""
    username = update.message.text.strip()

    # Guardar username en context
    context.user_data['twitter_username'] = username

    await update.message.reply_text(
        f"✅ Usuario recibido: `{username}`\n\n"
        "🔑 Ahora envía tu *contraseña* de X/Twitter:\n\n"
        "_La contraseña no se guardará, solo se usará para obtener las cookies de sesión_\n\n"
        "_Envía /cancel para cancelar_",
        parse_mode='Markdown'
    )
    return WAITING_PASSWORD

async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la contraseña y realiza el login"""
    password = update.message.text.strip()
    username = context.user_data.get('twitter_username')
    user_id = update.effective_user.id

    # Eliminar el mensaje con la contraseña inmediatamente
    try:
        await update.message.delete()
    except Exception:
        pass

    status_message = await update.effective_chat.send_message(
        "⏳ *Iniciando sesión en X/Twitter...*\n\n"
        "Esto puede tomar 30-60 segundos.\n"
        "Por favor espera...",
        parse_mode='Markdown'
    )

    # Generar cookies
    result = await generate_twitter_cookies(username, password)

    if result['success']:
        # Guardar cookies del usuario en memoria y persistencia local
        user_twitter_cookies[user_id] = result['cookies']
        save_twitter_session(user_id, result['cookies'])
        log_event('twitter_login_success', user_id=user_id)

        await status_message.edit_text(
            "✅ *¡Login exitoso!*\n\n"
            "Ahora puedes descargar videos de cuentas privadas de X/Twitter.\n\n"
            "🔐 Tu sesión está activa.\n"
            "🚪 Usa /logout_twitter para cerrar sesión.",
            parse_mode='Markdown'
        )
    else:
        await status_message.edit_text(
            "❌ *Error al iniciar sesión*\n\n"
            f"Error: {result['error']}\n\n"
            "Por favor verifica tus credenciales e intenta de nuevo con /login_twitter",
            parse_mode='Markdown'
        )

    # Limpiar datos del contexto
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el proceso de login"""
    await update.message.reply_text(
        "❌ Proceso de login cancelado.\n\n"
        "Puedes intentar de nuevo en cualquier momento con /login_twitter"
    )
    context.user_data.clear()
    return ConversationHandler.END

async def logout_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cierra la sesión de X/Twitter"""
    user_id = update.effective_user.id

    session_cookies = user_twitter_cookies.get(user_id) or load_twitter_session(user_id)

    if session_cookies:
        # Eliminar cookies del usuario
        user_twitter_cookies.pop(user_id, None)
        delete_twitter_session(user_id)
        log_event('twitter_logout', user_id=user_id)

        # Eliminar archivo de cookies temporal si existe
        cookies_file = os.path.join(DOWNLOAD_DIR, f'cookies_{user_id}.txt')
        if os.path.exists(cookies_file):
            safe_remove(cookies_file)

        await update.message.reply_text(
            "✅ *Sesión cerrada correctamente*\n\n"
            "Tu sesión de X/Twitter ha sido eliminada.\n\n"
            "Usa /login_twitter si necesitas volver a iniciar sesión.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "ℹ️ No tienes ninguna sesión activa de X/Twitter.\n\n"
            "Usa /login_twitter para iniciar sesión.",
            parse_mode='Markdown'
        )

async def handle_login_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los callbacks de los botones de login"""
    query = update.callback_query
    await query.answer()

    action, user_id_str = query.data.split('_', 2)[0:2]
    user_id = int(user_id_str.split('_')[-1])

    # Verificar que el usuario que presionó el botón es el correcto
    if query.from_user.id != user_id:
        await query.answer("⚠️ Este botón no es para ti", show_alert=True)
        return

    if action == "replace":
        await query.edit_message_text(
            "🔐 *Login de X/Twitter*\n\n"
            "📝 Por favor, envía tu *nombre de usuario o email* de X/Twitter:\n\n"
            "_Envía /cancel para cancelar_",
            parse_mode='Markdown'
        )
        return WAITING_USERNAME
    elif action == "cancel":
        await query.edit_message_text(
            "❌ Proceso cancelado.\n\n"
            "Tu sesión anterior sigue activa."
        )
        return ConversationHandler.END

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja URLs enviados por el usuario"""
    url = update.message.text.strip()

    # Validar que sea un URL
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    if not url_pattern.match(url):
        await update.message.reply_text(
            "❌ No se encontraron enlaces válidos.\n"
            "Envía uno o más enlaces de video/imagen."
        )
        return

    # Detectar plataforma
    platform = downloader.get_platform(url)
    if not platform:
        await update.message.reply_text(
            "❌ Ninguno de los enlaces es de una plataforma soportada.\n"
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
    user_id = query.from_user.id

    await query.edit_message_text(
        f"⏳ Descargando video de *{platform.upper()}*...\n"
        "Esto puede tomar unos momentos.",
        parse_mode='Markdown'
    )

    try:
        # Descargar video
        result = await downloader.download_video(url, chat_id, user_id=user_id)

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
        safe_remove(result['filename'])

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
    user_id = query.from_user.id

    await query.edit_message_text(
        f"⏳ Descargando y transcribiendo video de *{platform.upper()}*...\n"
        "🎙️ Esto puede tomar varios minutos.",
        parse_mode='Markdown'
    )

    try:
        # Descargar video
        result = await downloader.download_video(url, chat_id, user_id=user_id)

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
            safe_remove(result['filename'])
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
            safe_remove(result['filename'])
            safe_remove(audio_result['audio_path'])
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
        safe_remove(result['filename'])
        safe_remove(audio_result['audio_path'])

        await query.delete_message()

    except Exception as e:
        logger.error(f"Error en transcripción: {str(e)}")
        await query.edit_message_text(
            f"❌ Error al procesar:\n`{str(e)}`",
            parse_mode='Markdown'
        )

async def process_both(query, url, platform, chat_id):
    """Procesa descarga y transcripción del video"""
    user_id = query.from_user.id

    await query.edit_message_text(
        f"⏳ Descargando video de *{platform.upper()}*...\n"
        "📥 Descargando y 📝 Transcribiendo",
        parse_mode='Markdown'
    )

    video_path = None
    audio_path = None

    try:
        # Descargar video
        result = await downloader.download_video(url, chat_id, user_id=user_id)

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
            safe_remove(result['filename'])
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
            safe_remove(result['filename'])
            safe_remove(audio_result['audio_path'])
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
        safe_remove(video_path)
        safe_remove(audio_path)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja errores"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Función principal"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado")
        return

    init_bot_db()
    purge_expired_sessions()

    # Crear aplicación
    application = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler para login de Twitter
    login_conversation = ConversationHandler(
        entry_points=[CommandHandler('login_twitter', login_twitter_start)],
        states={
            WAITING_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)
            ],
            WAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_login)],
        allow_reentry=True
    )

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("platforms", platforms))
    application.add_handler(CommandHandler("logout_twitter", logout_twitter))
    application.add_handler(login_conversation)
    application.add_handler(CallbackQueryHandler(button_callback, pattern=r'^(download|transcribe|both)_\d+$'))
    application.add_handler(CallbackQueryHandler(handle_login_callback, pattern=r'^(replace|cancel)_login_\d+$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_error_handler(error_handler)

    # Iniciar bot
    logger.info("Bot iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
