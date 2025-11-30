# 🔧 Guía Rápida de Git

## 🚀 Setup Inicial (Primera Vez)

### 1. Configurar Git (si nunca lo has usado)

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

### 2. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre: `telegram-video-bot`
3. **IMPORTANTE:** Marca como **Private** 🔒
4. NO marques "Add README"
5. Click "Create repository"

### 3. Subir el Código

```bash
# En tu computadora local, extrae el proyecto
tar -xzf telegram_downloader_bot.tar.gz
cd telegram_downloader_bot

# Inicializar Git
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "Initial commit: Telegram Video Downloader Bot"

# Conectar con GitHub (reemplaza TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/telegram-video-bot.git

# Subir código
git branch -M main
git push -u origin main
```

### 4. Autenticación GitHub

**Opción A: Personal Access Token (Recomendado)**

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Nombre: "VPS Bot Deploy"
4. Permisos: Marca "repo"
5. Generate token
6. **COPIA EL TOKEN** (no lo verás de nuevo)

Cuando Git pida contraseña, usa el token en vez de tu contraseña.

**Opción B: SSH (Más seguro)**

```bash
# Generar clave SSH (si no tienes)
ssh-keygen -t ed25519 -C "tu@email.com"

# Copiar clave pública
cat ~/.ssh/id_ed25519.pub

# Agregar en GitHub:
# Settings → SSH and GPG keys → New SSH key
# Pega la clave pública

# Cambiar URL a SSH
git remote set-url origin git@github.com:TU_USUARIO/telegram-video-bot.git
```

---

## 📥 Clonar en el VPS

### Primera vez:

```bash
# Conectar al VPS
ssh root@TU_IP

# Ir a directorio de aaPanel
cd /www/wwwroot

# Clonar (opción HTTPS)
git clone https://github.com/TU_USUARIO/telegram-video-bot.git

# O clonar (opción HTTPS con token)
git clone https://TU_TOKEN@github.com/TU_USUARIO/telegram-video-bot.git

# O clonar (opción SSH)
git clone git@github.com:TU_USUARIO/telegram-video-bot.git

# Entrar al directorio
cd telegram-video-bot
```

---

## 🔄 Workflow: Hacer Cambios

### En tu computadora local:

```bash
cd telegram_downloader_bot

# 1. Ver estado actual
git status

# 2. Hacer cambios en los archivos
nano bot.py  # O cualquier editor

# 3. Ver qué cambió
git diff

# 4. Agregar archivos modificados
git add bot.py
# O agregar todos los cambios:
git add .

# 5. Hacer commit
git commit -m "Descripción clara de los cambios"

# 6. Subir a GitHub
git push
```

### En el VPS (actualizar):

```bash
# Conectar al VPS
ssh root@TU_IP

# Ir al directorio
cd /www/wwwroot/telegram-video-bot

# Descargar cambios
git pull

# Reconstruir y reiniciar bot
docker compose up -d --build

# Ver logs
docker compose logs -f
```

---

## 🛠️ Comandos Git Útiles

### Ver información

```bash
# Ver estado
git status

# Ver historial de commits
git log

# Ver historial compacto
git log --oneline

# Ver qué cambió
git diff

# Ver ramas
git branch
```

### Trabajar con cambios

```bash
# Descartar cambios no guardados
git checkout -- archivo.py

# Descartar todos los cambios
git reset --hard

# Ver archivos modificados
git status

# Agregar archivo específico
git add bot.py

# Agregar todos los archivos
git add .

# Commit con mensaje
git commit -m "Mensaje descriptivo"

# Commit y push en un comando
git commit -am "Mensaje" && git push
```

### Actualizar desde GitHub

```bash
# Descargar cambios
git pull

# Ver qué hay nuevo sin descargar
git fetch
git log HEAD..origin/main
```

### Deshacer cosas

```bash
# Deshacer último commit (mantener cambios)
git reset --soft HEAD^

# Deshacer último commit (eliminar cambios)
git reset --hard HEAD^

# Revertir un commit específico
git revert COMMIT_HASH
```

---

## 🌿 Trabajar con Ramas (Opcional)

```bash
# Crear rama para desarrollo
git checkout -b desarrollo

# Hacer cambios y commit
git add .
git commit -m "Nuevas funciones"

# Cambiar a rama main
git checkout main

# Fusionar desarrollo en main
git merge desarrollo

# Eliminar rama
git branch -d desarrollo

# Subir rama a GitHub
git push -u origin desarrollo
```

---

## 🚨 Solución de Problemas

### "Permission denied (publickey)"

```bash
# Verificar SSH
ssh -T git@github.com

# O cambiar a HTTPS
git remote set-url origin https://github.com/TU_USUARIO/telegram-video-bot.git
```

### "Failed to push some refs"

```bash
# Descargar cambios primero
git pull --rebase
git push
```

### Conflictos al hacer pull

```bash
# Ver archivos en conflicto
git status

# Editar archivo y resolver conflicto
nano archivo_en_conflicto.py

# Buscar marcas de conflicto:
# <<<<<<< HEAD
# Tu código
# =======
# Código del servidor
# >>>>>>> origin/main

# Después de resolver:
git add archivo_resuelto.py
git commit -m "Resolver conflicto"
git push
```

### Olvidé agregar archivo al .gitignore

```bash
# Si ya subiste .env por error (¡PELIGRO!)

# 1. Agregarlo a .gitignore
echo ".env" >> .gitignore

# 2. Eliminar del tracking
git rm --cached .env

# 3. Commit
git add .gitignore
git commit -m "Remover .env del repositorio"
git push

# 4. IMPORTANTE: Cambiar el token en @BotFather
# porque el viejo ya está expuesto en GitHub
```

### Guardar credenciales

```bash
# Guardar credenciales (HTTP)
git config credential.helper store

# O por 1 hora
git config credential.helper 'cache --timeout=3600'
```

---

## 📋 Checklist Pre-Push

Antes de hacer `git push`, verifica:

- [ ] `.env` NO está en el commit
- [ ] Archivos `downloads/` NO están incluidos
- [ ] No hay contraseñas o tokens en el código
- [ ] El commit tiene mensaje descriptivo
- [ ] Los cambios funcionan localmente

```bash
# Ver qué vas a subir
git status
git diff --cached

# Verificar que .env no esté
git ls-files | grep .env
# No debería mostrar nada
```

---

## 🔒 Seguridad

### NUNCA subas estos archivos:

- ❌ `.env` (contiene token)
- ❌ `*.pem` / `*.key` (claves SSH)
- ❌ Contraseñas o tokens en código
- ❌ Datos personales

### Verificar que .gitignore funciona:

```bash
# Ver archivos ignorados
git status --ignored

# Debería listar:
# - .env
# - downloads/
# - __pycache__/
# etc.
```

---

## 📝 Buenas Prácticas

### Mensajes de Commit

✅ Buenos ejemplos:
```bash
git commit -m "Agregar soporte para Facebook videos"
git commit -m "Corregir error al descargar videos largos"
git commit -m "Actualizar dependencias de seguridad"
git commit -m "Mejorar manejo de errores en descarga"
```

❌ Malos ejemplos:
```bash
git commit -m "cambios"
git commit -m "fix"
git commit -m "asdf"
git commit -m "update"
```

### Frecuencia de Commits

- Haz commit cuando completes una funcionalidad
- No acumules muchos cambios en un solo commit
- Commits pequeños y frecuentes > commits grandes y raros

### Tags para Versiones

```bash
# Crear tag
git tag -a v1.0.0 -m "Primera versión estable"

# Subir tag
git push origin v1.0.0

# Ver tags
git tag

# Ver código de un tag específico
git checkout v1.0.0
```

---

## 🔄 Automatizar Updates en VPS

Crear script `auto-update.sh` en el VPS:

```bash
#!/bin/bash
cd /www/wwwroot/telegram-video-bot

# Guardar cambios locales si hay
git stash

# Descargar cambios
git pull

# Aplicar cambios guardados si había
git stash pop

# Reconstruir y reiniciar
docker compose up -d --build

echo "Bot actualizado $(date)"
```

Agregar a crontab para actualizar automáticamente:

```bash
# Editar crontab
crontab -e

# Agregar (actualizar cada día a las 3 AM):
0 3 * * * /www/wwwroot/telegram-video-bot/auto-update.sh >> /var/log/bot-update.log 2>&1
```

---

## 📚 Recursos

- **Git Básico:** https://git-scm.com/book/es/v2
- **GitHub Docs:** https://docs.github.com/es
- **Git Cheatsheet:** https://training.github.com/downloads/es_ES/github-git-cheat-sheet/

---

## ⚡ Comandos Rápidos para Copy-Paste

### Setup inicial:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/telegram-video-bot.git
git push -u origin main
```

### Workflow diario:
```bash
# Local: hacer cambios y subir
git add .
git commit -m "Descripción de cambios"
git push

# VPS: actualizar bot
cd /www/wwwroot/telegram-video-bot
git pull
docker compose up -d --build
```

### Verificar seguridad:
```bash
# Verificar que .env no esté en Git
git ls-files | grep .env
# (debe estar vacío)

# Ver qué vas a subir
git status
git diff --cached
```

---

¿Listo para subir tu bot a Git? 🚀
