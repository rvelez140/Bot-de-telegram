# 🐳 Guía Completa de Implementación en Docker

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

1. ✅ Un servidor con acceso SSH (puede ser VPS, servidor local, Raspberry Pi, etc.)
2. ✅ Sistema operativo: Linux (Ubuntu, Debian, CentOS, etc.)
3. ✅ Acceso root o sudo
4. ✅ Conexión a internet

## 🔧 PASO 1: Instalar Docker

### En Ubuntu/Debian:

```bash
# Actualizar paquetes
sudo apt update
sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configurar repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalación
sudo docker --version
sudo docker compose version
```

### En CentOS/RHEL:

```bash
# Instalar dependencias
sudo yum install -y yum-utils

# Agregar repositorio
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Instalar Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verificar
sudo docker --version
sudo docker compose version
```

### Agregar tu usuario al grupo docker (opcional, para no usar sudo):

```bash
# Agregar usuario
sudo usermod -aG docker $USER

# Aplicar cambios (necesitas cerrar sesión y volver a entrar)
newgrp docker

# Verificar
docker ps
```

## 🤖 PASO 2: Obtener Token de Telegram

1. **Abre Telegram** en tu móvil o desktop

2. **Busca @BotFather**
   - Es el bot oficial de Telegram para crear bots
   - Usuario: `@BotFather`

3. **Crea tu bot:**
   ```
   /newbot
   ```

4. **Sigue las instrucciones:**
   - Nombre del bot: "Mi Descargador de Videos"
   - Username: "mi_descargador_bot" (debe terminar en "bot")

5. **Copia el token:**
   ```
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
   ```
   
   ⚠️ **¡IMPORTANTE!** Guarda este token en un lugar seguro. Lo necesitarás en el siguiente paso.

6. **Configura tu bot (opcional):**
   ```
   /setdescription - Descripción del bot
   /setabouttext - Texto "Acerca de"
   /setuserpic - Foto de perfil
   ```

## 📦 PASO 3: Descargar e Instalar el Bot

### Opción A: Descarga directa del archivo

```bash
# Crear directorio para el bot
mkdir -p ~/telegram-bot
cd ~/telegram-bot

# Descargar el archivo (ajusta la ruta según donde esté tu archivo)
# Si lo tienes en tu computadora local, súbelo con scp:
# scp telegram_downloader_bot.tar.gz usuario@servidor:~/telegram-bot/

# Extraer archivos
tar -xzf telegram_downloader_bot.tar.gz
cd telegram_downloader_bot

# Ver archivos
ls -la
```

### Opción B: Copiar archivos manualmente

Si prefieres copiar los archivos uno por uno:

```bash
# Crear directorio
mkdir -p ~/telegram-bot && cd ~/telegram-bot

# Crear cada archivo con nano o vim
# Copia el contenido de cada archivo del proyecto
```

## ⚙️ PASO 4: Configurar el Bot

### Configurar variables de entorno:

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con nano
nano .env

# O con vim
vim .env
```

**Contenido del archivo `.env`:**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
```

Reemplaza `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456` con tu token real.

💾 **Guardar:** En nano presiona `Ctrl+O`, `Enter`, luego `Ctrl+X`

### Verificar que el archivo existe:

```bash
cat .env
```

Deberías ver tu token (pero no lo compartas con nadie).

## 🚀 PASO 5: Construir y Ejecutar el Bot

### Método 1: Con Docker Compose (Recomendado)

```bash
# Construir la imagen
docker compose build

# Iniciar el bot
docker compose up -d

# Ver logs
docker compose logs -f
```

**Explicación de comandos:**
- `build` - Construye la imagen del contenedor
- `up -d` - Inicia el contenedor en segundo plano (detached)
- `logs -f` - Muestra logs en tiempo real (Ctrl+C para salir)

### Método 2: Con Docker directamente

```bash
# Construir imagen
docker build -t telegram-bot .

# Ejecutar contenedor
docker run -d \
  --name telegram-video-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN="tu_token_aqui" \
  -v $(pwd)/downloads:/downloads \
  telegram-bot

# Ver logs
docker logs -f telegram-video-bot
```

### Método 3: Instalación automática

```bash
# Hacer ejecutable el script
chmod +x install.sh

# Ejecutar
./install.sh
```

Este script te pedirá el token y hará todo automáticamente.

## ✅ PASO 6: Verificar que Funciona

### Verificar que el contenedor está corriendo:

```bash
# Ver contenedores activos
docker ps

# Deberías ver algo como:
# CONTAINER ID   IMAGE     COMMAND           STATUS
# abc123def456   ...       "python bot.py"   Up 2 minutes
```

### Ver los logs:

```bash
# Con docker compose
docker compose logs -f

# Con docker
docker logs -f telegram-video-bot
```

**Logs exitosos se ven así:**
```
2024-11-25 10:30:15 - Bot iniciado...
2024-11-25 10:30:15 - Application started
```

**Si hay errores, verás:**
```
ERROR - TELEGRAM_BOT_TOKEN no está configurado
```
o
```
ERROR - Unauthorized (invalid token)
```

### Probar el bot en Telegram:

1. **Abre Telegram**
2. **Busca tu bot** por el username que le diste
3. **Envía:** `/start`
4. **Deberías recibir:** El mensaje de bienvenida
5. **Prueba con un video:**
   ```
   https://www.tiktok.com/@usuario/video/1234567890
   ```

## 🔧 PASO 7: Gestión del Bot

### Comandos útiles:

```bash
# Ver estado
docker compose ps

# Ver logs
docker compose logs -f

# Detener bot
docker compose stop

# Iniciar bot
docker compose start

# Reiniciar bot
docker compose restart

# Detener y eliminar
docker compose down

# Reconstruir después de cambios
docker compose up -d --build

# Ver uso de recursos
docker stats telegram-video-downloader
```

### Actualizar el bot:

```bash
# 1. Detener el bot
docker compose down

# 2. Hacer cambios en bot.py o lo que necesites

# 3. Reconstruir
docker compose build

# 4. Iniciar
docker compose up -d

# 5. Verificar logs
docker compose logs -f
```

## 🐛 Solución de Problemas Comunes

### Problema 1: "Cannot connect to Docker daemon"

```bash
# Iniciar Docker
sudo systemctl start docker

# Habilitar en inicio
sudo systemctl enable docker

# Verificar estado
sudo systemctl status docker
```

### Problema 2: "Permission denied"

```bash
# Agregar usuario a grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar
newgrp docker
```

### Problema 3: "Port already in use"

Los bots de Telegram no usan puertos, pero si tienes otro servicio:

```bash
# Ver qué está usando el puerto
sudo lsof -i :PUERTO

# Detener servicio conflictivo
docker compose down
```

### Problema 4: "Invalid token"

```bash
# Verificar el token en .env
cat .env

# Verificar que no tiene espacios o caracteres extra
# Debe ser exactamente como lo dio @BotFather

# Reconstruir con nuevo token
docker compose down
nano .env  # Corregir token
docker compose up -d
```

### Problema 5: Bot se reinicia constantemente

```bash
# Ver logs para identificar error
docker compose logs -f

# Errores comunes:
# - Token inválido
# - Falta ffmpeg (ya está en el Dockerfile)
# - Permisos de archivos
```

### Problema 6: "No space left on device"

```bash
# Ver espacio en disco
df -h

# Limpiar Docker
docker system prune -a

# Limpiar descargas
rm -rf ./downloads/*
```

## 🔒 Seguridad

### Proteger el archivo .env:

```bash
# Cambiar permisos (solo tú puedes leer)
chmod 600 .env

# Verificar
ls -la .env
# Debería mostrar: -rw------- 1 tu_usuario tu_grupo
```

### Configurar firewall (opcional):

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw enable

# No necesitas abrir puertos para Telegram bot
```

### Actualizar sistema regularmente:

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

## 📊 Monitoreo

### Ver recursos del contenedor:

```bash
# Stats en tiempo real
docker stats telegram-video-downloader

# Ver logs con timestamps
docker compose logs -f --timestamps

# Ver últimas 100 líneas
docker compose logs --tail=100
```

### Configurar logs rotativos:

Ya está configurado en `docker-compose.yml`:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔄 Backup y Restauración

### Hacer backup:

```bash
# Backup completo
tar -czf telegram-bot-backup-$(date +%F).tar.gz \
  bot.py \
  requirements.txt \
  Dockerfile \
  docker-compose.yml \
  .env

# Mover a lugar seguro
mv telegram-bot-backup-*.tar.gz ~/backups/
```

### Restaurar:

```bash
# Extraer backup
tar -xzf telegram-bot-backup-2024-11-25.tar.gz

# Reconstruir
docker compose up -d --build
```

## 🌐 Configuración en VPS (Opcional)

### Para DigitalOcean, Linode, Vultr, etc.:

```bash
# 1. Conectar via SSH
ssh root@tu_ip_del_vps

# 2. Actualizar sistema
apt update && apt upgrade -y

# 3. Instalar Docker (ver PASO 1)

# 4. Crear usuario no-root (recomendado)
adduser botuser
usermod -aG sudo botuser
usermod -aG docker botuser

# 5. Cambiar a nuevo usuario
su - botuser

# 6. Subir archivos (desde tu computadora local)
scp telegram_downloader_bot.tar.gz botuser@tu_ip:/home/botuser/

# 7. Continuar con PASO 3
```

## 🚀 Puesta en Producción

### Configurar inicio automático:

Docker Compose ya incluye `restart: unless-stopped`, pero verifica:

```bash
# Ver política de reinicio
docker inspect telegram-video-downloader | grep -i restart

# Debería mostrar: "RestartPolicy": {"Name": "unless-stopped"}
```

### Habilitar Docker en el arranque:

```bash
sudo systemctl enable docker
```

### Configurar monitoreo (opcional):

```bash
# Crear script de health check
cat > health_check.sh << 'EOF'
#!/bin/bash
if ! docker ps | grep -q telegram-video-downloader; then
  echo "Bot caído, reiniciando..."
  cd ~/telegram-bot/telegram_downloader_bot
  docker compose up -d
fi
EOF

chmod +x health_check.sh

# Agregar a crontab (cada 5 minutos)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/usuario/health_check.sh") | crontab -
```

## ✨ Siguientes Pasos

Una vez que el bot esté funcionando:

1. ✅ Prueba con diferentes plataformas
2. ✅ Configura usuarios autorizados (ver ADVANCED.md)
3. ✅ Personaliza mensajes del bot
4. ✅ Agrega funcionalidades extras
5. ✅ Configura backups automáticos

## 📚 Recursos Adicionales

- **Documentación de Docker:** https://docs.docker.com/
- **python-telegram-bot:** https://docs.python-telegram-bot.org/
- **yt-dlp:** https://github.com/yt-dlp/yt-dlp
- **Telegram Bot API:** https://core.telegram.org/bots/api

---

## 🆘 ¿Necesitas Ayuda?

Si algo no funciona:

1. **Revisa los logs:** `docker compose logs -f`
2. **Verifica el token:** `cat .env`
3. **Asegúrate que Docker está corriendo:** `docker ps`
4. **Revisa el FAQ.md** para problemas comunes

**Comando de diagnóstico completo:**
```bash
#!/bin/bash
echo "=== Diagnóstico del Bot ==="
echo "Docker version:"
docker --version
echo ""
echo "Docker Compose version:"
docker compose version
echo ""
echo "Contenedores activos:"
docker ps
echo ""
echo "Token configurado:"
cat .env | grep TELEGRAM_BOT_TOKEN | sed 's/=.*/=***OCULTO***/'
echo ""
echo "Últimos logs:"
docker compose logs --tail=20
echo ""
echo "Espacio en disco:"
df -h | grep -E '^/dev/'
echo ""
echo "=== Fin del diagnóstico ==="
```

Guarda esto como `diagnostico.sh`, hazlo ejecutable (`chmod +x diagnostico.sh`) y ejecútalo cuando tengas problemas.

---

¡Listo! Tu bot debería estar funcionando perfectamente. 🎉
