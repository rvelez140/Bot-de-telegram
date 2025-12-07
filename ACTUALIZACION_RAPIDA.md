# 🚀 Actualización Rápida - Soporte Completo + Cuentas Privadas

## ✨ **Nuevas Funcionalidades Agregadas:**

1. 🔐 **Soporte para cuentas privadas** (con cookies)
2. 🌐 **Mejora en soporte de Twitter/X**
3. 📱 **Mejores headers HTTP** (evita bloqueos)
4. 🔄 **Última versión de yt-dlp**

---

## ⚡ **Actualización Rápida en el VPS**

### **PASO 1: Actualizar código desde GitHub**

```bash
# Conectar al VPS
ssh root@TU_IP

# Ir al directorio
cd /www/wwwroot/Bot-de-telegram

# Descargar cambios
git pull
```

---

### **PASO 2: Reconstruir imagen**

```bash
# Detener bot
docker compose down

# Reconstruir con nuevas mejoras
docker compose build --no-cache

# Iniciar bot
docker compose up -d

# Ver logs
docker compose logs -f
```

---

## 🔐 **OPCIONAL: Configurar Cookies para Cuentas Privadas**

Si quieres descargar de cuentas privadas:

### **1. Exportar cookies del navegador**

**Chrome:**
- Instala extensión: "Get cookies.txt LOCALLY"
- Ve a Instagram/Twitter y inicia sesión
- Click en la extensión → Export → `cookies.txt`

**Firefox:**
- Instala addon: "cookies.txt"
- Mismo proceso

---

### **2. Subir cookies al VPS**

**Opción A - SCP (desde tu PC):**
```powershell
scp cookies.txt root@TU_IP:/www/wwwroot/Bot-de-telegram/
```

**Opción B - Manual:**
```bash
# En el VPS
cd /www/wwwroot/Bot-de-telegram
nano cookies.txt
# Pegar contenido, guardar (Ctrl+O, Enter, Ctrl+X)
```

---

### **3. Proteger archivo**

```bash
chmod 600 /www/wwwroot/Bot-de-telegram/cookies.txt
```

---

### **4. Reconstruir bot**

```bash
cd /www/wwwroot/Bot-de-telegram
docker compose down
docker compose build
docker compose up -d
```

---

## ✅ **Verificar que Funciona**

### **Probar con contenido público:**

```
https://www.tiktok.com/@zachking/video/7308444126198557998
https://www.youtube.com/watch?v=jNQXAC9IVRw
https://www.instagram.com/reel/DDx7HKgSBLi/
```

### **Probar con cuenta privada (si configuraste cookies):**

Envía enlace de Instagram privado que sigues.

---

## 🎯 **Lo Que Ahora Puede Hacer Tu Bot:**

| Contenido | Sin Cookies | Con Cookies |
|-----------|-------------|-------------|
| **TikTok público** | ✅ | ✅ |
| **TikTok privado** | ❌ | ✅ |
| **YouTube público** | ✅ | ✅ |
| **YouTube sin listar** | ❌ | ✅ |
| **Instagram público** | ✅ | ✅ |
| **Instagram privado** | ❌ | ✅ |
| **Instagram stories** | ❌ | ✅ |
| **Twitter público** | ✅ | ✅ |
| **Twitter protegido** | ❌ | ✅ |

---

## 🔄 **Comandos Útiles**

```bash
# Ver logs
docker compose logs -f

# Reiniciar
docker compose restart

# Ver estado
docker compose ps

# Actualizar desde Git
git pull && docker compose up -d --build

# Ver versión de yt-dlp
docker compose exec telegram-downloader-bot yt-dlp --version
```

---

## 📚 **Documentación Completa**

Para guía detallada de cookies:
- Lee: `CONFIGURAR_COOKIES.md`

Para todas las funcionalidades:
- Lee: `NUEVAS_FUNCIONALIDADES.md`

---

## 🚨 **Importante**

- ⚠️ Las cookies expiran cada 30-60 días
- 🔒 Nunca compartas `cookies.txt` (contiene tu sesión)
- 📝 `cookies.txt` está en `.gitignore` (no se sube a Git)
- 🔐 Solo usa cookies de TU cuenta

---

¿Listo para actualizar? Ejecuta los comandos del PASO 1 y 2. 🚀
