# 🔐 Descargar de Cuentas Privadas - Configuración de Cookies

## 🎯 **Qué Permite Esto**

Con cookies configuradas, tu bot podrá:
- ✅ Descargar de cuentas privadas de Instagram
- ✅ Descargar stories de Instagram
- ✅ Descargar contenido protegido de Twitter/X
- ✅ Acceder a contenido que requiere login
- ✅ Evitar límites de rate limiting

---

## 📋 **Plataformas que Requieren Cookies para Contenido Privado**

| Plataforma | Público | Privado/Protegido |
|------------|---------|-------------------|
| **Instagram** | ✅ Sin cookies | ❌ Necesita cookies |
| **Twitter/X** | ✅ Sin cookies | ⚠️ Algunos necesitan cookies |
| **TikTok** | ✅ Sin cookies | ⚠️ Algunos necesitan cookies |
| **YouTube** | ✅ Sin cookies | ❌ Necesita cookies (privados) |

---

## 🛠️ **PASO 1: Obtener Cookies del Navegador**

### **Opción A: Usar Extensión de Chrome/Firefox (Recomendado)**

#### **Para Chrome:**

1. Instala la extensión: **"Get cookies.txt LOCALLY"**
   - Link: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

2. **Instagram:**
   - Ve a https://www.instagram.com
   - Inicia sesión con tu cuenta
   - Click en el ícono de la extensión
   - Click en "Export" → Guarda como `cookies.txt`

3. **Twitter/X:**
   - Ve a https://twitter.com
   - Inicia sesión
   - Click en el ícono de la extensión
   - Click en "Export" → Guarda como `cookies_twitter.txt`

4. **TikTok:**
   - Ve a https://www.tiktok.com
   - Inicia sesión
   - Click en el ícono de la extensión
   - Click en "Export" → Guarda como `cookies_tiktok.txt`

---

#### **Para Firefox:**

1. Instala: **"cookies.txt"**
   - Link: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

2. Mismo proceso que Chrome

---

### **Opción B: Usar yt-dlp para Extraer Cookies**

```bash
# En tu PC (Windows)
# Instalar yt-dlp
pip install yt-dlp

# Extraer cookies de Chrome para Instagram
yt-dlp --cookies-from-browser chrome --cookies cookies_instagram.txt https://www.instagram.com

# Extraer cookies de Firefox para Instagram
yt-dlp --cookies-from-browser firefox --cookies cookies_instagram.txt https://www.instagram.com
```

---

## 📤 **PASO 2: Subir Cookies al VPS**

### **Método 1: SCP (Recomendado)**

Desde tu PC (PowerShell o CMD):

```powershell
# Subir cookies de Instagram
scp cookies.txt root@TU_IP:/www/wwwroot/Bot-de-telegram/cookies.txt

# O si tienes múltiples:
scp cookies_instagram.txt root@TU_IP:/www/wwwroot/Bot-de-telegram/cookies.txt
```

---

### **Método 2: Manual (Copiar y Pegar)**

```bash
# En el VPS
ssh root@TU_IP

cd /www/wwwroot/Bot-de-telegram

# Crear archivo
nano cookies.txt
```

**Pegar el contenido del archivo cookies.txt de tu PC**

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### **Método 3: Desde aaPanel**

1. En aaPanel: **Files**
2. Navegar a `/www/wwwroot/Bot-de-telegram/`
3. Click en **"Upload"**
4. Seleccionar `cookies.txt`
5. Subir

---

## 🐳 **PASO 3: Actualizar Docker para Usar Cookies**

### **Actualizar Dockerfile:**

```bash
cd /www/wwwroot/Bot-de-telegram
nano Dockerfile
```

**Agregar después de `COPY bot.py .`:**

```dockerfile
# Copiar cookies si existe
COPY cookies.txt /app/cookies.txt 2>/dev/null || true
```

**Dockerfile completo:**

```dockerfile
FROM python:3.11-slim

# Instalar ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY bot.py .

# Copiar cookies (opcional, no falla si no existe)
COPY cookies.txt /app/cookies.txt 2>/dev/null || true

# Crear directorio de descargas
RUN mkdir -p /downloads

# Variables de entorno
ENV TELEGRAM_BOT_TOKEN=""

# Ejecutar bot
CMD ["python", "bot.py"]
```

**Guardar y cerrar**

---

## 🔄 **PASO 4: Reconstruir y Reiniciar Bot**

```bash
cd /www/wwwroot/Bot-de-telegram

# Detener bot
docker compose down

# Reconstruir imagen con cookies
docker compose build --no-cache

# Iniciar bot
docker compose up -d

# Ver logs
docker compose logs -f
```

---

## ✅ **PASO 5: Probar con Cuenta Privada**

### **Instagram Privado:**

1. Encuentra un post de una cuenta privada que SIGUES
2. Copia el enlace
3. Envíalo al bot
4. Debería descargarse ✅

### **Instagram Story:**

```
https://www.instagram.com/stories/usuario/story_id
```

---

## 🔐 **Seguridad de las Cookies**

### **⚠️ IMPORTANTE:**

Las cookies contienen tu sesión activa. Si alguien las obtiene, puede acceder a tu cuenta.

**Medidas de seguridad:**

```bash
# Proteger archivo cookies.txt
cd /www/wwwroot/Bot-de-telegram
chmod 600 cookies.txt

# Verificar que NO está en Git
cat .gitignore | grep cookies.txt

# Si no está, agregarlo:
echo "cookies.txt" >> .gitignore
echo "cookies_*.txt" >> .gitignore

git add .gitignore
git commit -m "Ignorar archivos de cookies"
git push
```

---

## 🔄 **Actualizar Cookies (Cada 30-60 días)**

Las cookies expiran. Para renovarlas:

1. Volver al navegador
2. Exportar cookies nuevamente
3. Subir al VPS
4. Reiniciar bot:

```bash
cd /www/wwwroot/Bot-de-telegram
docker compose restart
```

---

## 🧪 **Verificar que las Cookies Funcionan**

```bash
# Conectar al VPS
cd /www/wwwroot/Bot-de-telegram

# Entrar al contenedor
docker compose exec telegram-downloader-bot bash

# Verificar que cookies.txt existe
ls -la /app/cookies.txt

# Probar descarga con cookies
yt-dlp --cookies /app/cookies.txt "https://www.instagram.com/p/ENLACE_PRIVADO/"

# Salir
exit
```

---

## 🎯 **Usar Diferentes Cookies por Plataforma**

Si quieres cookies separadas para cada plataforma:

### **Modificar bot.py:**

```python
# En la función download_video, cambiar:

if platform == 'instagram':
    ydl_opts['cookiefile'] = '/app/cookies_instagram.txt'
elif platform == 'twitter':
    ydl_opts['cookiefile'] = '/app/cookies_twitter.txt'
elif platform == 'tiktok':
    ydl_opts['cookiefile'] = '/app/cookies_tiktok.txt'
else:
    ydl_opts['cookiefile'] = '/app/cookies.txt'
```

### **Subir múltiples archivos de cookies:**

```bash
# Subir cada archivo
scp cookies_instagram.txt root@TU_IP:/www/wwwroot/Bot-de-telegram/
scp cookies_twitter.txt root@TU_IP:/www/wwwroot/Bot-de-telegram/
scp cookies_tiktok.txt root@TU_IP:/www/wwwroot/Bot-de-telegram/
```

### **Actualizar Dockerfile:**

```dockerfile
# Copiar todas las cookies
COPY cookies*.txt /app/ 2>/dev/null || true
```

---

## 🚨 **Troubleshooting**

### **Error: "cookies.txt not found"**

```bash
# Verificar ubicación
cd /www/wwwroot/Bot-de-telegram
ls -la cookies.txt

# Si no existe, subirlo de nuevo
```

### **Error: "Login required"**

Significa que las cookies expiraron:
1. Exportar cookies nuevamente
2. Subir al VPS
3. Reiniciar bot

### **Error: "This account is private"**

Asegúrate de:
1. ✅ Estar siguiendo la cuenta privada
2. ✅ Las cookies son de una cuenta que sigue esa cuenta
3. ✅ Las cookies no han expirado

---

## 📊 **Resumen de Archivos**

```
/www/wwwroot/Bot-de-telegram/
├─ bot.py                    ← Código actualizado
├─ Dockerfile               ← Con soporte de cookies
├─ cookies.txt              ← Cookies generales (Instagram)
├─ cookies_twitter.txt      ← Cookies de Twitter (opcional)
├─ cookies_tiktok.txt       ← Cookies de TikTok (opcional)
└─ .gitignore              ← Incluye cookies*.txt
```

---

## ✅ **Checklist de Configuración**

- [ ] Cookies exportadas desde navegador
- [ ] Cookies subidas al VPS
- [ ] Dockerfile actualizado
- [ ] Bot reconstruido
- [ ] Permisos configurados (chmod 600)
- [ ] cookies.txt en .gitignore
- [ ] Bot probado con cuenta privada
- [ ] Funciona correctamente

---

## 🎉 **Resultado Final**

Con cookies configuradas, tu bot podrá:

✅ Instagram público → Sin cookies
✅ Instagram privado → Con cookies
✅ Instagram stories → Con cookies
✅ Twitter público → Sin cookies
✅ Twitter protegido → Con cookies
✅ TikTok público → Sin cookies
✅ TikTok privado → Con cookies
✅ YouTube público → Sin cookies
✅ YouTube sin listar → Con cookies

---

## 📝 **Notas Importantes**

1. **Privacidad:** Solo usa cookies de TU propia cuenta
2. **Seguridad:** Nunca compartas el archivo cookies.txt
3. **Renovación:** Actualiza cookies cada 30-60 días
4. **Backup:** Guarda copia de cookies.txt localmente
5. **Legal:** Solo descarga contenido que tengas permiso de descargar

---

¿Listo para configurar las cookies? 🚀
