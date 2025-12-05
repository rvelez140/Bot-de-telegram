# 🔄 Guía de Actualización - Nuevas Funcionalidades

## 🎉 ¿Qué hay de nuevo?

Tu bot ahora tiene 3 nuevas funcionalidades importantes:

1. 🖼️ **Descarga de imágenes** - Soporta imágenes de Instagram, Twitter, TikTok
2. 📦 **División automática de videos grandes** - Videos >2GB se dividen en partes
3. 📎 **Múltiples enlaces simultáneos** - Envía varios enlaces a la vez

---

## 🚀 Actualización Rápida (5 minutos)

### Para tu repositorio: https://github.com/rvelez140/Bot-de-telegram.git

**PASO 1: Actualizar el código en GitHub**

En tu PC local:

```bash
cd Bot-de-telegram

# Descargar cambios (si hiciste fork o clon del proyecto actualizado)
git pull origin main

# O si tienes el código nuevo, sobrescribir bot.py
# Copia el archivo bot.py nuevo al directorio
```

Subir a GitHub:

```bash
git add bot.py README.md
git commit -m "Agregar soporte para imágenes, división de videos grandes y múltiples enlaces"
git push
```

**PASO 2: Actualizar en el VPS**

Conectar al VPS:

```bash
ssh root@TU_IP
```

Actualizar bot:

```bash
# Ir al directorio
cd /www/wwwroot/Bot-de-telegram

# Descargar cambios
git pull

# Reconstruir contenedor
docker compose down
docker compose build
docker compose up -d

# Verificar logs
docker compose logs -f
```

¡Listo! Tu bot ya tiene las nuevas funcionalidades.

---

## 🧪 Probar las Nuevas Funcionalidades

### Probar descarga de imagen:

```
1. Abre tu bot en Telegram
2. Envía: https://www.instagram.com/p/[algún_post_con_imagen]/
3. Deberías recibir la imagen en máxima calidad
```

### Probar video grande (si tienes uno >2GB):

```
1. Envía un enlace de YouTube de video largo
2. El bot dividirá automáticamente
3. Recibirás múltiples partes numeradas
```

### Probar múltiples enlaces:

```
1. Envía varios enlaces en un mensaje:

https://www.tiktok.com/@usuario/video/123
https://www.youtube.com/watch?v=abc
https://www.instagram.com/p/xyz/

2. El bot procesará todos automáticamente
3. Recibirás todos los archivos
```

---

## 📋 Checklist de Actualización

- [ ] Código actualizado localmente
- [ ] Cambios subidos a GitHub
- [ ] VPS conectado via SSH
- [ ] Código descargado con `git pull`
- [ ] Contenedor reconstruido
- [ ] Bot reiniciado
- [ ] Logs verificados (sin errores)
- [ ] Funcionalidad de imágenes probada
- [ ] Funcionalidad de múltiples enlaces probada
- [ ] Funcionalidad de división de videos probada (opcional)

---

## 🔧 Si algo sale mal

### El bot no inicia después de actualizar

```bash
# Ver logs para identificar error
cd /www/wwwroot/Bot-de-telegram
docker compose logs

# Errores comunes:
# - Sintaxis en bot.py → Verificar código
# - Permisos → chmod 755 bot.py
# - Token inválido → Verificar .env
```

### Función no disponible

```bash
# Verificar que el código se actualizó
cd /www/wwwroot/Bot-de-telegram
git log -1

# Debería mostrar tu último commit

# Si no, hacer pull nuevamente
git pull
docker compose up -d --build
```

### División de videos no funciona

**Causa:** ffmpeg ya está instalado en el Dockerfile, pero verifica:

```bash
# Entrar al contenedor
docker compose exec telegram-video-downloader bash

# Verificar ffmpeg
ffmpeg -version

# Si no está, el Dockerfile ya lo instala
```

---

## 📚 Documentación Adicional

Para más detalles sobre las nuevas funcionalidades:

- **NUEVAS_FUNCIONALIDADES.md** - Guía completa de cada función
- **README.md** - Documentación actualizada
- **FAQ.md** - Preguntas frecuentes (actualizar si es necesario)

---

## 💡 Comandos Útiles Post-Actualización

```bash
# Ver estado del bot
cd /www/wwwroot/Bot-de-telegram && docker compose ps

# Ver logs en tiempo real
cd /www/wwwroot/Bot-de-telegram && docker compose logs -f

# Reiniciar bot
cd /www/wwwroot/Bot-de-telegram && docker compose restart

# Ver última actualización de Git
cd /www/wwwroot/Bot-de-telegram && git log -1 --oneline
```

---

## 🎯 Resumen de Cambios en el Código

### Archivo: bot.py

**Cambios principales:**

1. **Clase renombrada:** `VideoDownloader` → `MediaDownloader`

2. **Nuevas funciones:**
   - `split_video()` - Divide videos grandes
   - `get_duration()` - Obtiene duración del video
   - `download_image()` - Descarga imágenes

3. **Función mejorada:**
   - `handle_url()` - Ahora procesa múltiples URLs
   - Detecta y extrae todos los enlaces del mensaje
   - Procesa cada uno secuencialmente
   - Muestra progreso en tiempo real

4. **Comandos actualizados:**
   - `/start` - Menciona nuevas funcionalidades
   - `/help` - Incluye ejemplos de múltiples enlaces
   - `/platforms` - Actualizado con imágenes

5. **Constantes nuevas:**
   - `MAX_FILE_SIZE` - 2GB
   - `CHUNK_SIZE` - 1.9GB por parte

---

## 🔄 Actualizaciones Futuras

Para mantener tu bot actualizado:

```bash
# Crear alias (opcional)
echo 'alias update-bot="cd /www/wwwroot/Bot-de-telegram && git pull && docker compose up -d --build"' >> ~/.bashrc
source ~/.bashrc

# Ahora puedes actualizar con:
update-bot
```

---

## 🆘 Soporte

Si tienes problemas con la actualización:

1. **Revisa los logs:**
   ```bash
   docker compose logs -f
   ```

2. **Verifica la versión:**
   ```bash
   git log -1
   ```

3. **Reinstala si es necesario:**
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

---

¡Disfruta las nuevas funcionalidades! 🎉

**Tiempo estimado de actualización:** 5-10 minutos
**Downtime del bot:** ~2 minutos durante la reconstrucción
