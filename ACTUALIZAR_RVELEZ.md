# 🚀 Actualización para rvelez140 - Comandos Exactos

## 📦 Archivos Actualizados

### Archivos Modificados:
- `bot.py` - Código principal (261 → 497 líneas)
- `README.md` - Documentación actualizada

### Archivos Nuevos:
- `NUEVAS_FUNCIONALIDADES.md` - Guía completa de nuevas funciones
- `GUIA_ACTUALIZACION.md` - Cómo actualizar
- `DESPLIEGUE_RAPIDO_RVELEZ.md` - Guía específica para ti

---

## ✨ Nuevas Funcionalidades

1. 🖼️ **Descarga de imágenes** (Instagram, Twitter, TikTok)
2. 📦 **División automática** de videos >2GB en partes iguales
3. 📎 **Múltiples enlaces** simultáneos (envía varios a la vez)

---

## 🎯 PASO A PASO - Actualizar Tu Bot

### Opción A: Archivo Completo Actualizado (Recomendado)

Ya tienes el archivo `telegram_downloader_bot.tar.gz` descargado con TODO el código actualizado.

**En tu PC:**

```bash
# 1. Extraer el proyecto actualizado
tar -xzf telegram_downloader_bot.tar.gz
cd telegram_downloader_bot

# 2. Copiar el bot.py actualizado a tu repositorio
cp bot.py /ruta/a/tu/Bot-de-telegram/

# 3. También puedes copiar la documentación nueva
cp NUEVAS_FUNCIONALIDADES.md /ruta/a/tu/Bot-de-telegram/
cp GUIA_ACTUALIZACION.md /ruta/a/tu/Bot-de-telegram/

# 4. Ir a tu repositorio
cd /ruta/a/tu/Bot-de-telegram/

# 5. Subir cambios a GitHub
git add bot.py README.md NUEVAS_FUNCIONALIDADES.md GUIA_ACTUALIZACION.md
git commit -m "Agregar soporte para imágenes, división de videos grandes y múltiples enlaces"
git push
```

---

**En tu VPS:**

```bash
# 1. Conectar
ssh root@TU_IP

# 2. Ir al directorio del bot
cd /www/wwwroot/Bot-de-telegram

# 3. Descargar cambios
git pull

# 4. Reconstruir contenedor
docker compose down
docker compose build
docker compose up -d

# 5. Ver logs
docker compose logs -f
```

---

### Opción B: Solo Actualizar bot.py

Si solo quieres el código nuevo:

**Archivo a actualizar:** Solo `bot.py`

**En tu PC:**

1. Abre el archivo `bot.py` del proyecto descargado
2. Copia TODO el contenido
3. Reemplaza el contenido de tu `bot.py` en `Bot-de-telegram/`
4. Sube a GitHub:

```bash
cd Bot-de-telegram
git add bot.py
git commit -m "Actualizar bot: imágenes, videos grandes, múltiples enlaces"
git push
```

**En tu VPS:**

```bash
ssh root@TU_IP
cd /www/wwwroot/Bot-de-telegram
git pull
docker compose down
docker compose up -d --build
docker compose logs -f
```

---

## 🧪 Probar Nuevas Funcionalidades

### 1. Probar imagen:

Envía a tu bot:
```
https://www.instagram.com/p/C1yf_W5v4p2/
```

Deberías recibir la imagen.

### 2. Probar múltiples enlaces:

Envía a tu bot:
```
https://www.tiktok.com/@gordonramsayofficial/video/7011450298411109637
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.instagram.com/p/C1yf_W5v4p2/
```

El bot procesará los 3 y los enviará uno por uno.

### 3. Probar video grande (opcional):

Busca un video de YouTube largo (>2GB) y envía el enlace.
El bot lo dividirá automáticamente en partes.

---

## 📋 Checklist Completo

### En tu PC:
- [ ] Proyecto actualizado extraído
- [ ] `bot.py` copiado a tu repositorio
- [ ] Cambios confirmados: `git status`
- [ ] Commit hecho: `git commit`
- [ ] Subido a GitHub: `git push`

### En tu VPS:
- [ ] Conectado via SSH
- [ ] En directorio: `/www/wwwroot/Bot-de-telegram`
- [ ] Código descargado: `git pull`
- [ ] Contenedor detenido: `docker compose down`
- [ ] Imagen reconstruida: `docker compose build`
- [ ] Bot iniciado: `docker compose up -d`
- [ ] Logs verificados: `docker compose logs -f`

### Pruebas:
- [ ] Bot responde a `/start`
- [ ] Descarga imagen (Instagram/Twitter)
- [ ] Procesa múltiples enlaces
- [ ] Divide video grande (opcional)

---

## 💻 Comandos de Una Línea

### Actualización completa en VPS:

```bash
cd /www/wwwroot/Bot-de-telegram && git pull && docker compose down && docker compose build && docker compose up -d && docker compose logs --tail=20
```

### Ver estado después de actualizar:

```bash
cd /www/wwwroot/Bot-de-telegram && echo "=== GIT STATUS ===" && git log -1 --oneline && echo "" && echo "=== DOCKER STATUS ===" && docker compose ps && echo "" && echo "=== ÚLTIMOS LOGS ===" && docker compose logs --tail=10
```

---

## 🔍 Verificación de Código Actualizado

Para verificar que tienes el código nuevo:

```bash
# En tu VPS
cd /www/wwwroot/Bot-de-telegram

# Ver número de líneas en bot.py
wc -l bot.py

# Debería mostrar algo como:
# 497 bot.py
# (antes era ~261 líneas)

# Ver funciones nuevas
grep -n "split_video\|download_image\|MAX_FILE_SIZE" bot.py

# Debería encontrar esas funciones
```

---

## 🐛 Solución Rápida de Problemas

### Bot no inicia:

```bash
docker compose logs
# Busca errores de sintaxis en Python
```

### Código no actualizado:

```bash
git status
git log -1
# Verifica último commit

# Forzar actualización
git fetch --all
git reset --hard origin/main
docker compose up -d --build
```

### Función no funciona:

```bash
# Verificar que bot.py tiene el código nuevo
grep "def split_video" bot.py
grep "def download_image" bot.py

# Si no aparece, el código no se actualizó
git pull
docker compose up -d --build
```

---

## 📊 Comparación Antes/Después

### ANTES:
```
✅ Videos de TikTok, YouTube, Twitter, Instagram
✅ Sin marca de agua (TikTok)
❌ Límite 50MB
❌ Solo un enlace a la vez
❌ No soporta imágenes
```

### DESPUÉS:
```
✅ Videos de TikTok, YouTube, Twitter, Instagram
✅ Imágenes de todas las plataformas 🆕
✅ Sin marca de agua (TikTok)
✅ Videos hasta 2GB por parte 🆕
✅ División automática de videos grandes 🆕
✅ Múltiples enlaces simultáneos 🆕
```

---

## 📞 Siguiente Paso

**Ejecuta estos comandos en orden:**

```bash
# EN TU PC:
# 1. Extrae el proyecto
tar -xzf telegram_downloader_bot.tar.gz

# 2. Copia bot.py a tu repo
cp telegram_downloader_bot/bot.py ~/Bot-de-telegram/

# 3. Sube a GitHub
cd ~/Bot-de-telegram
git add bot.py
git commit -m "Actualizar bot con nuevas funcionalidades"
git push

# EN TU VPS:
# 1. Conectar
ssh root@TU_IP

# 2. Actualizar
cd /www/wwwroot/Bot-de-telegram
git pull
docker compose down
docker compose build
docker compose up -d

# 3. Verificar
docker compose logs -f
```

---

## 🎉 ¡Listo!

Tu bot ahora tiene:
- 🖼️ Soporte para imágenes
- 📦 División automática de videos grandes
- 📎 Procesamiento múltiple de enlaces

**Tiempo estimado:** 10 minutos
**Downtime:** ~2 minutos

---

¿Necesitas ayuda? Revisa:
- `NUEVAS_FUNCIONALIDADES.md` - Detalles de cada función
- `GUIA_ACTUALIZACION.md` - Guía completa
- `FAQ.md` - Preguntas frecuentes
