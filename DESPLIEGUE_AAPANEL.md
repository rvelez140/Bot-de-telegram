# 🚀 Despliegue con aaPanel y Git

## 📋 Requisitos Previos

- ✅ VPS con aaPanel instalado
- ✅ Acceso SSH al VPS
- ✅ Cuenta de GitHub/GitLab/Gitea
- ✅ Token de Telegram Bot

---

## PARTE 1: Subir Proyecto a Git

### Opción A: GitHub (Recomendado)

#### 1.1 Crear Repositorio en GitHub

1. Ve a https://github.com
2. Click en "New repository" (botón verde)
3. Nombre: `telegram-video-bot` (o el que prefieras)
4. **IMPORTANTE:** Marca como **Private** (para proteger tu token)
5. NO inicialices con README (ya tenemos uno)
6. Click "Create repository"

#### 1.2 Subir el Código

En tu computadora local (donde tienes el proyecto):

```bash
# Extraer el proyecto si aún no lo has hecho
tar -xzf telegram_downloader_bot.tar.gz
cd telegram_downloader_bot

# Inicializar repositorio Git
git init

# Agregar todos los archivos
git add .

# Hacer commit inicial
git commit -m "Initial commit: Telegram video downloader bot"

# Conectar con GitHub
git remote add origin https://github.com/TU_USUARIO/telegram-video-bot.git

# Subir código
git branch -M main
git push -u origin main
```

**Credenciales:**
- Usuario: Tu usuario de GitHub
- Contraseña: Usa un "Personal Access Token" (no tu contraseña)

**Crear Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → Nombre: "VPS Bot Deploy"
3. Permisos: Marca "repo"
4. Generar y copiar el token (guárdalo, no lo verás de nuevo)

---

### Opción B: GitLab

```bash
# Similar a GitHub pero con GitLab
git remote add origin https://gitlab.com/TU_USUARIO/telegram-video-bot.git
git push -u origin main
```

---

### Opción C: Repositorio Privado en tu VPS (Gitea/Gogs)

Si tienes Gitea en aaPanel:

```bash
git remote add origin https://tu-dominio.com/gitea/tu-usuario/telegram-video-bot.git
git push -u origin main
```

---

## PARTE 2: Configurar aaPanel

### 2.1 Acceder a aaPanel

1. Abre tu navegador
2. Ve a: `http://TU_IP:7800` (o el puerto que uses)
3. Inicia sesión con tus credenciales

### 2.2 Instalar Docker en aaPanel

#### Opción 1: Desde la interfaz de aaPanel

1. En aaPanel, ve a **"App Store"** o **"Docker Manager"**
2. Busca **"Docker"** o **"Docker Manager"**
3. Click en **"Install"**
4. Espera a que termine la instalación

#### Opción 2: Via SSH (Recomendado)

```bash
# Conectar a tu VPS via SSH
ssh root@TU_IP

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker compose version
```

### 2.3 Configurar Permisos

```bash
# Agregar usuario www a grupo docker (para que aaPanel pueda usar Docker)
sudo usermod -aG docker www
sudo systemctl restart docker
```

---

## PARTE 3: Desplegar el Bot en el VPS

### 3.1 Conectar via SSH

```bash
ssh root@TU_IP
# O desde aaPanel: Terminal → SSH Terminal
```

### 3.2 Clonar el Repositorio

```bash
# Ir al directorio de aplicaciones
cd /www/wwwroot

# Clonar tu repositorio
git clone https://github.com/TU_USUARIO/telegram-video-bot.git

# O si es privado con token:
git clone https://TU_TOKEN@github.com/TU_USUARIO/telegram-video-bot.git

# Entrar al directorio
cd telegram-video-bot
```

### 3.3 Configurar el Token de Telegram

```bash
# Crear archivo .env
cp .env.example .env

# Editar con nano
nano .env

# O con vi
vi .env
```

**Contenido del .env:**
```env
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
```

**Guardar:**
- Nano: `Ctrl+O`, `Enter`, `Ctrl+X`
- Vi: `Esc`, `:wq`, `Enter`

**Proteger el archivo:**
```bash
chmod 600 .env
```

### 3.4 Construir e Iniciar el Bot

```bash
# Construir imagen
docker compose build

# Iniciar bot en segundo plano
docker compose up -d

# Ver logs
docker compose logs -f
```

---

## PARTE 4: Configurar en aaPanel (Opcional)

### 4.1 Crear Script de Gestión en aaPanel

1. En aaPanel, ve a **"Cron"** o **"Scheduled Tasks"**
2. Crea un nuevo script bash

**Script de inicio:**
```bash
#!/bin/bash
cd /www/wwwroot/telegram-video-bot
docker compose up -d
```

**Script de reinicio:**
```bash
#!/bin/bash
cd /www/wwwroot/telegram-video-bot
docker compose restart
```

**Script de actualización:**
```bash
#!/bin/bash
cd /www/wwwroot/telegram-video-bot
git pull
docker compose up -d --build
```

### 4.2 Configurar Auto-inicio (Opcional)

Para que el bot se inicie automáticamente cuando el VPS se reinicie:

```bash
# Editar crontab
crontab -e

# Agregar esta línea al final:
@reboot cd /www/wwwroot/telegram-video-bot && docker compose up -d
```

---

## PARTE 5: Monitoreo desde aaPanel

### 5.1 Ver Logs

```bash
# SSH al servidor
ssh root@TU_IP

# Ver logs en tiempo real
cd /www/wwwroot/telegram-video-bot
docker compose logs -f

# Ver últimas 100 líneas
docker compose logs --tail=100
```

### 5.2 Ver Estado del Contenedor

```bash
# Ver contenedores corriendo
docker ps

# Ver estado del bot
docker compose ps

# Ver uso de recursos
docker stats telegram-video-downloader
```

### 5.3 Crear Script de Monitoreo

Crear archivo `monitor.sh`:
```bash
#!/bin/bash
cd /www/wwwroot/telegram-video-bot

echo "=== Estado del Bot ==="
docker compose ps

echo ""
echo "=== Uso de Recursos ==="
docker stats --no-stream telegram-video-downloader

echo ""
echo "=== Últimos Logs ==="
docker compose logs --tail=20
```

Hacer ejecutable:
```bash
chmod +x monitor.sh
```

Ejecutar:
```bash
./monitor.sh
```

---

## PARTE 6: Actualización del Bot

### Cuando hagas cambios en el código:

#### En tu computadora local:
```bash
cd telegram_downloader_bot

# Hacer cambios en bot.py o lo que necesites
nano bot.py

# Guardar cambios en Git
git add .
git commit -m "Descripción de los cambios"
git push
```

#### En el VPS:
```bash
# SSH al servidor
ssh root@TU_IP

cd /www/wwwroot/telegram-video-bot

# Descargar cambios
git pull

# Reconstruir y reiniciar
docker compose up -d --build

# Verificar logs
docker compose logs -f
```

---

## PARTE 7: Gestión del Bot

### Comandos Útiles

```bash
# Ir al directorio
cd /www/wwwroot/telegram-video-bot

# Iniciar bot
docker compose up -d

# Detener bot
docker compose stop

# Reiniciar bot
docker compose restart

# Ver logs
docker compose logs -f

# Ver estado
docker compose ps

# Actualizar desde Git
git pull
docker compose up -d --build

# Limpiar recursos
docker system prune -a
```

---

## PARTE 8: Seguridad en aaPanel

### 8.1 Proteger el archivo .env

```bash
# Asegurar que .env no esté en Git
echo ".env" >> .gitignore

# Cambiar permisos
chmod 600 .env
chown www:www .env
```

### 8.2 Firewall en aaPanel

1. Ve a **"Security"** en aaPanel
2. El bot NO necesita puertos abiertos (solo usa la API de Telegram)
3. Asegura que solo SSH (22) y aaPanel estén abiertos

### 8.3 Backup Automático

En aaPanel, configura backup automático:

1. **"Backup"** → **"Backup Settings"**
2. Agregar directorio: `/www/wwwroot/telegram-video-bot`
3. Frecuencia: Diaria
4. Retención: 7 días

O crear script manual:
```bash
#!/bin/bash
BACKUP_DIR="/www/backup/telegram-bot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

cd /www/wwwroot/telegram-video-bot
tar -czf $BACKUP_DIR/bot-backup-$DATE.tar.gz \
    bot.py \
    docker-compose.yml \
    Dockerfile \
    requirements.txt \
    .env

# Mantener solo últimos 7 backups
ls -t $BACKUP_DIR/bot-backup-*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completado: bot-backup-$DATE.tar.gz"
```

---

## PARTE 9: Troubleshooting

### Problema: "Permission denied" al usar Docker

```bash
# Agregar usuario actual a grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión
logout
# Volver a conectar via SSH
```

### Problema: Puerto 7800 (aaPanel) usado por Docker

aaPanel y Docker no tienen conflicto de puertos porque:
- aaPanel usa puerto 7800 para su interfaz web
- El bot de Telegram NO usa puertos (solo API)
- No hay problema ✅

### Problema: Bot no inicia

```bash
# Ver logs completos
cd /www/wwwroot/telegram-video-bot
docker compose logs

# Verificar token
cat .env

# Reiniciar todo
docker compose down
docker compose up -d
```

### Problema: Git pide credenciales constantemente

```bash
# Usar SSH en vez de HTTPS
git remote set-url origin git@github.com:TU_USUARIO/telegram-video-bot.git

# O guardar credenciales
git config credential.helper store
```

---

## PARTE 10: Estructura Final en el VPS

```
/www/wwwroot/telegram-video-bot/
├── .git/                       # Repositorio Git
├── .env                        # Tu token (NO en Git)
├── .gitignore                  # Archivos ignorados
├── bot.py                      # Código principal
├── Dockerfile                  # Config Docker
├── docker-compose.yml          # Orquestación
├── requirements.txt            # Dependencias
├── downloads/                  # Temporales (creado auto)
├── README.md                   # Documentación
└── *.md                        # Otras guías

Docker Containers:
└── telegram-video-downloader   # Corriendo 24/7
```

---

## 🎯 Resumen del Flujo Completo

### Primera vez:
```bash
# 1. LOCAL: Subir a Git
git init
git add .
git commit -m "Initial commit"
git push

# 2. VPS: Clonar
ssh root@TU_IP
cd /www/wwwroot
git clone URL_DE_TU_REPO
cd telegram-video-bot

# 3. VPS: Configurar
cp .env.example .env
nano .env  # Agregar token

# 4. VPS: Iniciar
docker compose up -d
```

### Actualizaciones futuras:
```bash
# LOCAL: Hacer cambios y subir
git add .
git commit -m "Cambios"
git push

# VPS: Descargar y actualizar
cd /www/wwwroot/telegram-video-bot
git pull
docker compose up -d --build
```

---

## ✅ Checklist Final

- [ ] Proyecto subido a Git (privado)
- [ ] Docker instalado en VPS
- [ ] Repositorio clonado en `/www/wwwroot/`
- [ ] Archivo `.env` creado con token
- [ ] Bot iniciado con `docker compose up -d`
- [ ] Logs verificados (sin errores)
- [ ] Bot probado en Telegram
- [ ] Backup configurado
- [ ] Scripts de gestión creados

---

## 💡 Tips Adicionales

### Usar dominio con aaPanel

Si tienes un dominio configurado en aaPanel, puedes:

1. Crear sitio web en aaPanel
2. Agregar dominio: `bot.tudominio.com`
3. NO necesitas configurar proxy (el bot no tiene interfaz web)
4. Solo úsalo para organizarte mejor

### Monitoreo con aaPanel

1. **"Monitor"** en aaPanel muestra:
   - Uso de CPU
   - Uso de RAM
   - Uso de Disco

2. El contenedor Docker aparecerá en el uso de recursos

### Logs en aaPanel

Puedes ver logs de Docker desde aaPanel:
1. **"Docker Manager"** (si lo instalaste desde aaPanel)
2. O usa SSH y `docker compose logs`

---

## 🚨 IMPORTANTE: Seguridad

**NUNCA subas el archivo `.env` a Git**

El `.gitignore` ya está configurado para evitarlo, pero verifica:

```bash
# Verificar que .env está en .gitignore
cat .gitignore | grep .env

# Debería mostrar:
# .env
```

Si accidentalmente subiste el `.env`:
1. Revoca el token en @BotFather
2. Crea nuevo token
3. Actualiza `.env`
4. Elimina el archivo de Git history

---

¿Necesitas ayuda con algún paso específico? ¡Pregúntame! 🚀
