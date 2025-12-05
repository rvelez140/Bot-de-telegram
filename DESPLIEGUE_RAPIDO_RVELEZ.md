# 🚀 Despliegue Rápido - Tu Bot Ya en GitHub

## 📍 Tu Repositorio
https://github.com/rvelez140/Bot-de-telegram.git

## ✅ Lo que ya tienes:
- ✅ Código en GitHub
- ✅ Docker instalado en VPS
- ✅ aaPanel en VPS

---

## 🎯 DESPLIEGUE EN 5 PASOS (10 minutos)

### PASO 1: Conectar al VPS

```bash
# Desde tu terminal o Putty
ssh root@TU_IP_DEL_VPS

# O desde aaPanel:
# Panel → Terminal → Click en "Terminal"
```

---

### PASO 2: Clonar el Repositorio

```bash
# Ir al directorio de aaPanel
cd /www/wwwroot

# Clonar tu repositorio
git clone https://github.com/rvelez140/Bot-de-telegram.git

# Entrar al directorio
cd Bot-de-telegram

# Ver los archivos
ls -la
```

**Deberías ver:**
- bot.py
- Dockerfile
- docker-compose.yml
- requirements.txt
- etc.

---

### PASO 3: Configurar el Token de Telegram

#### 3.1 Obtener Token (si no lo tienes)

1. Abre **Telegram**
2. Busca **@BotFather**
3. Envía: `/newbot`
4. Sigue las instrucciones
5. **Copia el token** (ejemplo: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 3.2 Crear archivo .env

```bash
# Crear archivo .env desde el ejemplo
cp .env.example .env

# Editar con nano
nano .env
```

**Dentro del archivo, pega tu token:**
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Guardar:**
- Presiona `Ctrl + O`
- Presiona `Enter`
- Presiona `Ctrl + X`

#### 3.3 Proteger el archivo

```bash
chmod 600 .env
```

---

### PASO 4: Construir e Iniciar el Bot

```bash
# Asegúrate de estar en el directorio correcto
pwd
# Debería mostrar: /www/wwwroot/Bot-de-telegram

# Construir la imagen Docker
docker compose build

# Iniciar el bot
docker compose up -d

# Ver si está corriendo
docker compose ps
```

**Deberías ver algo como:**
```
NAME                          STATUS
telegram-video-downloader     Up 3 seconds
```

---

### PASO 5: Verificar que Funciona

```bash
# Ver logs en tiempo real
docker compose logs -f
```

**Logs exitosos se ven así:**
```
2024-11-30 - Bot iniciado...
2024-11-30 - Application started
```

**Si ves errores de token:**
```
ERROR - Unauthorized (invalid token)
```
→ Verifica el token en `.env`

#### Probar en Telegram:

1. Abre **Telegram**
2. Busca tu bot (el username que le diste)
3. Envía: `/start`
4. Deberías recibir el mensaje de bienvenida ✅
5. Prueba con un enlace de TikTok/YouTube/Instagram

---

## 🎉 ¡LISTO! Tu bot está corriendo

**Ubicación:** `/www/wwwroot/Bot-de-telegram`  
**Contenedor:** `telegram-video-downloader`  
**Estado:** Corriendo 24/7

---

## 📊 Comandos Útiles

### Ver estado del bot:
```bash
cd /www/wwwroot/Bot-de-telegram
docker compose ps
```

### Ver logs:
```bash
cd /www/wwwroot/Bot-de-telegram
docker compose logs -f
# Presiona Ctrl+C para salir
```

### Reiniciar bot:
```bash
cd /www/wwwroot/Bot-de-telegram
docker compose restart
```

### Detener bot:
```bash
cd /www/wwwroot/Bot-de-telegram
docker compose stop
```

### Iniciar bot:
```bash
cd /www/wwwroot/Bot-de-telegram
docker compose start
```

### Ver uso de recursos:
```bash
docker stats telegram-video-downloader
```

---

## 🔄 Actualizar el Bot (cuando hagas cambios)

### Cuando edites código en tu PC:

```bash
# En tu PC
cd Bot-de-telegram
git add .
git commit -m "Descripción de cambios"
git push
```

### En el VPS:

```bash
# SSH al VPS
ssh root@TU_IP

# Ir al directorio
cd /www/wwwroot/Bot-de-telegram

# Descargar cambios
git pull

# Reconstruir e iniciar
docker compose up -d --build

# Ver logs
docker compose logs -f
```

---

## 🛠️ Script de Actualización Rápida

Crea este script para actualizar más fácil:

```bash
# Crear script
nano /www/wwwroot/Bot-de-telegram/update.sh
```

**Contenido:**
```bash
#!/bin/bash
cd /www/wwwroot/Bot-de-telegram
echo "🔄 Descargando cambios desde Git..."
git pull
echo "🏗️ Reconstruyendo imagen..."
docker compose build
echo "🚀 Reiniciando bot..."
docker compose up -d
echo "✅ Bot actualizado!"
docker compose ps
```

**Hacer ejecutable:**
```bash
chmod +x /www/wwwroot/Bot-de-telegram/update.sh
```

**Usar:**
```bash
/www/wwwroot/Bot-de-telegram/update.sh
```

---

## 🔒 Seguridad

### Verificar que .env NO está en Git:

```bash
cd /www/wwwroot/Bot-de-telegram

# Ver archivos en Git
git ls-files | grep .env

# NO debería mostrar .env
# Si lo muestra, ver solución abajo
```

### Si .env está en Git (¡PELIGRO!):

```bash
# 1. Eliminarlo del tracking
git rm --cached .env

# 2. Asegurar que está en .gitignore
echo ".env" >> .gitignore

# 3. Commit
git add .gitignore
git commit -m "Remover .env del repositorio"
git push

# 4. IMPORTANTE: Cambiar el token en @BotFather
# El token viejo ya está expuesto en GitHub
```

---

## 🔍 Verificación Completa

Ejecuta estos comandos para verificar que todo está bien:

```bash
echo "=== VERIFICACIÓN DEL BOT ==="
echo ""
echo "📍 Ubicación:"
pwd

echo ""
echo "📁 Archivos:"
ls -la

echo ""
echo "🔑 Token configurado:"
cat .env | grep TELEGRAM_BOT_TOKEN | sed 's/=.*/=***OCULTO***/'

echo ""
echo "🐳 Estado Docker:"
docker compose ps

echo ""
echo "📊 Últimos logs:"
docker compose logs --tail=10

echo ""
echo "💾 Espacio en disco:"
df -h | grep -E '^/dev/'

echo ""
echo "=== FIN VERIFICACIÓN ==="
```

---

## 🐛 Solución de Problemas

### Problema: "permission denied"

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión
logout
# Volver a conectar
```

### Problema: "No such file or directory"

```bash
# Verificar que estás en el directorio correcto
cd /www/wwwroot/Bot-de-telegram
pwd
```

### Problema: Bot no responde en Telegram

```bash
# Ver logs completos
docker compose logs

# Verificar token
cat .env

# Reiniciar
docker compose restart
```

### Problema: "Port already in use"

Los bots de Telegram NO usan puertos, pero si hay conflicto:

```bash
# Ver qué usa el puerto
docker ps

# Detener contenedor anterior
docker compose down

# Iniciar de nuevo
docker compose up -d
```

### Problema: Sin espacio en disco

```bash
# Limpiar Docker
docker system prune -a

# Limpiar descargas viejas
rm -rf /www/wwwroot/Bot-de-telegram/downloads/*
```

---

## 🌟 Configuración de Auto-inicio

Para que el bot se inicie automáticamente cuando el VPS se reinicie:

```bash
# Editar crontab
crontab -e

# Agregar al final (selecciona nano si pregunta):
@reboot cd /www/wwwroot/Bot-de-telegram && docker compose up -d
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 📱 Monitoreo desde aaPanel

### Crear script de monitoreo:

```bash
# Crear archivo
nano /www/wwwroot/Bot-de-telegram/monitor.sh
```

**Contenido:**
```bash
#!/bin/bash
cd /www/wwwroot/Bot-de-telegram

echo "╔════════════════════════════════════╗"
echo "║   ESTADO DEL BOT DE TELEGRAM       ║"
echo "╚════════════════════════════════════╝"
echo ""

echo "🐳 Contenedor:"
docker compose ps

echo ""
echo "📊 Recursos:"
docker stats --no-stream telegram-video-downloader

echo ""
echo "📋 Últimos 20 logs:"
docker compose logs --tail=20
```

**Ejecutar:**
```bash
chmod +x /www/wwwroot/Bot-de-telegram/monitor.sh
/www/wwwroot/Bot-de-telegram/monitor.sh
```

---

## ✅ Checklist Final

- [ ] Repositorio clonado en `/www/wwwroot/Bot-de-telegram`
- [ ] Archivo `.env` creado con tu token
- [ ] Bot construido: `docker compose build`
- [ ] Bot iniciado: `docker compose up -d`
- [ ] Estado verificado: `docker compose ps` (muestra "Up")
- [ ] Logs sin errores: `docker compose logs`
- [ ] Bot probado en Telegram (responde a `/start`)
- [ ] Video descargado correctamente
- [ ] Auto-inicio configurado (opcional)

---

## 🎯 Resumen de Tu Setup

```
VPS con aaPanel
    │
    ├─ Docker ✅
    │
    ├─ /www/wwwroot/Bot-de-telegram/
    │   ├─ Código desde GitHub ✅
    │   ├─ .env con token ✅
    │   └─ Bot corriendo en Docker ✅
    │
    └─ Telegram Bot
        └─ Descargando videos 24/7 🎉
```

---

## 🚀 Comandos de Una Línea

```bash
# Despliegue completo
cd /www/wwwroot && git clone https://github.com/rvelez140/Bot-de-telegram.git && cd Bot-de-telegram && cp .env.example .env && nano .env && docker compose up -d

# Reinicio completo
cd /www/wwwroot/Bot-de-telegram && docker compose down && docker compose up -d --build

# Ver todo
cd /www/wwwroot/Bot-de-telegram && docker compose ps && docker compose logs --tail=20

# Actualizar desde Git
cd /www/wwwroot/Bot-de-telegram && git pull && docker compose up -d --build
```

---

## 📞 Siguiente Paso

**Ejecuta estos comandos en orden:**

```bash
# 1. Conectar al VPS
ssh root@TU_IP

# 2. Clonar
cd /www/wwwroot
git clone https://github.com/rvelez140/Bot-de-telegram.git
cd Bot-de-telegram

# 3. Configurar token
cp .env.example .env
nano .env
# Pegar tu token, guardar (Ctrl+O, Enter, Ctrl+X)

# 4. Iniciar
docker compose build
docker compose up -d

# 5. Verificar
docker compose logs -f
```

¡Y listo! Tu bot estará corriendo. 🎉

---

¿En qué paso estás? ¿Necesitas ayuda con algo específico?
