# 🚀 Implementación en Docker - 5 Minutos

## ✅ Lo que necesitas

1. Un servidor con Docker (VPS, PC, Raspberry Pi, etc.)
2. 5 minutos de tu tiempo
3. Un token de Telegram Bot

---

## 📱 PASO 1: Obtén tu Token (2 minutos)

1. Abre **Telegram**
2. Busca: **@BotFather**
3. Envía: `/newbot`
4. Dale un nombre: "Mi Descargador"
5. Dale un usuario: "mi_descargador_bot"
6. **COPIA EL TOKEN** que te da (algo como: `123456:ABC-DEF1234`)

---

## 🐳 PASO 2: Instala Docker (1 minuto)

### Si ya tienes Docker: ✅ Salta al paso 3

### Si no tienes Docker:

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Luego cierra sesión y vuelve a entrar**

---

## 📦 PASO 3: Descarga y Extrae (30 segundos)

```bash
# Subir el archivo al servidor (si lo descargaste en tu PC)
scp telegram_downloader_bot.tar.gz usuario@tu-servidor:~/ 

# O descargarlo directamente en el servidor
# wget URL_DEL_ARCHIVO

# Extraer
tar -xzf telegram_downloader_bot.tar.gz
cd telegram_downloader_bot
```

---

## ⚙️ PASO 4: Configurar Token (30 segundos)

```bash
# Crear archivo de configuración
cp .env.example .env

# Editar y pegar tu token
nano .env
```

Dentro del archivo, cambia esto:
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
```

Por tu token real:
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghijklmnop
```

**Guardar:** Presiona `Ctrl+O`, luego `Enter`, luego `Ctrl+X`

---

## 🚀 PASO 5: Iniciar el Bot (1 minuto)

### Opción A: Instalación Automática (MUY FÁCIL)
```bash
chmod +x setup.sh
./setup.sh
```

El script hará todo automáticamente ✨

### Opción B: Manual (3 comandos)
```bash
# Construir
docker compose build

# Iniciar
docker compose up -d

# Ver logs
docker compose logs -f
```

---

## ✅ Verificar que Funciona

1. Abre **Telegram**
2. Busca tu bot (el usuario que le pusiste)
3. Envía: `/start`
4. Deberías ver el mensaje de bienvenida ✅

### Probar descarga:
Envía cualquier enlace de TikTok, YouTube, Twitter o Instagram:
```
https://www.tiktok.com/@usuario/video/1234567890
```

¡Y listo! Deberías recibir el video 🎉

---

## 🎯 Comandos Útiles

```bash
# Ver si está corriendo
docker compose ps

# Ver logs
docker compose logs -f

# Reiniciar
docker compose restart

# Detener
docker compose stop

# Iniciar
docker compose start
```

---

## ❌ Si algo sale mal

### El bot no responde:
```bash
# Ver qué pasó
docker compose logs -f

# Reintentar
docker compose restart
```

### Token inválido:
```bash
# Verificar token
cat .env

# Corregir
nano .env

# Reiniciar
docker compose down
docker compose up -d
```

### No tengo espacio:
```bash
# Limpiar Docker
docker system prune -a

# Limpiar descargas
rm -rf downloads/*
```

---

## 🎊 ¡Eso es todo!

Tu bot ya está corriendo en Docker y funcionando 24/7.

**Lo que puedes hacer ahora:**
- Enviar enlaces de videos al bot
- Recibir videos sin marca de agua
- Compartir el bot con amigos

**Siguiente paso (opcional):**
- Lee `ADVANCED.md` para personalizar
- Lee `FAQ.md` si tienes preguntas
- Modifica `bot.py` para agregar funciones

---

## 📊 Resumen Visual

```
Tu PC/Servidor
    │
    ├─ Docker instalado ✅
    │
    ├─ Proyecto extraído
    │   ├─ .env con tu token ✅
    │   └─ docker-compose.yml
    │
    ├─ Contenedor corriendo
    │   └─ Bot de Telegram 🤖
    │       └─ yt-dlp + ffmpeg
    │
    └─ Telegram App
        └─ Tu bot respondiendo 24/7 🎉
```

---

## 🆘 Ayuda Rápida

**¿El bot no descarga?**
- Verifica que el enlace sea de una plataforma soportada
- Revisa los logs: `docker compose logs -f`

**¿Quiero cambiar algo?**
- Edita `bot.py`
- Reconstruye: `docker compose up -d --build`

**¿Necesito actualizar?**
- `docker compose exec telegram-downloader-bot pip install --upgrade yt-dlp`

**¿Más ayuda?**
- `README.md` - Documentación completa
- `FAQ.md` - Preguntas frecuentes
- `INSTALACION_DOCKER.md` - Guía detallada

---

## 💰 Costo Estimado

**Si usas VPS:**
- DigitalOcean: $6/mes
- Linode: $5/mes
- Vultr: $5/mes

**Si usas servidor casero:**
- Raspberry Pi 4: ~$50 una vez
- PC viejo: Gratis ✅
- Costo eléctrico: ~$2-5/mes

---

¡Disfruta tu bot de descarga de videos! 🎥🎉

**Tiempo total de instalación:** 5 minutos ⏱️
