# 🚀 CI/CD Completo con GitHub Actions

## 🎯 **Lo Que Vamos a Lograr:**

```
Tu PC → GitHub → Docker Hub → VPS
  ↓         ↓          ↓         ↓
Código   Build      Imagen    Deploy
         Auto       Auto      Auto
```

**Workflow:**
1. Haces cambios en tu PC
2. `git push` a GitHub
3. GitHub construye imagen Docker automáticamente
4. GitHub sube imagen a Docker Hub
5. GitHub actualiza el bot en tu VPS automáticamente

**¡TODO AUTOMÁTICO!** 🎉

---

## 📋 **Requisitos Previos:**

- ✅ Repositorio en GitHub: `rvelez140/Bot-de-telegram`
- ✅ Cuenta de Docker Hub: `rvelez140`
- ✅ VPS con SSH configurado
- ✅ Bot ya funcionando en VPS

---

## 🔧 **PASO 1: Configurar Secrets en GitHub**

Los "secrets" son variables privadas que GitHub usa para conectarse a tus servicios.

### **1.1 Ir a tu Repositorio en GitHub**

https://github.com/rvelez140/Bot-de-telegram

### **1.2 Configurar Secrets**

1. Click en **"Settings"** (del repositorio)
2. En el menú lateral: **"Secrets and variables"** → **"Actions"**
3. Click en **"New repository secret"**

---

### **1.3 Crear los Siguientes Secrets:**

#### **Secret 1: DOCKER_USERNAME**
```
Name: DOCKER_USERNAME
Value: rvelez140
```

#### **Secret 2: DOCKER_PASSWORD**
```
Name: DOCKER_PASSWORD
Value: [Tu contraseña de Docker Hub]
```

⚠️ **Mejor usar un Access Token:**
1. Ve a https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Nombre: "GitHub Actions"
4. Permisos: Read, Write, Delete
5. Copia el token
6. Usa el token en vez de la contraseña

#### **Secret 3: VPS_HOST**
```
Name: VPS_HOST
Value: [IP de tu VPS]
Ejemplo: 123.45.67.89
```

#### **Secret 4: VPS_USERNAME**
```
Name: VPS_USERNAME
Value: root
```

#### **Secret 5: VPS_SSH_KEY**
```
Name: VPS_SSH_KEY
Value: [Tu clave SSH privada]
```

**¿Cómo obtener la clave SSH?**

**En tu PC (Windows PowerShell):**

```powershell
# Si NO tienes clave SSH, crear una:
ssh-keygen -t ed25519 -C "github-actions"
# Presiona Enter 3 veces (sin contraseña)

# Ver tu clave PRIVADA (la que va en el secret)
Get-Content ~/.ssh/id_ed25519
```

**Copiar TODO el contenido** (desde `-----BEGIN` hasta `-----END`)

**En tu VPS, agregar clave PÚBLICA:**

```bash
# Conectar al VPS
ssh root@TU_IP

# Agregar tu clave pública
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Desde tu PC, copiar la clave pública:
# En PowerShell:
Get-Content ~/.ssh/id_ed25519.pub

# En el VPS:
nano ~/.ssh/authorized_keys
# Pegar la clave pública
# Guardar: Ctrl+O, Enter, Ctrl+X

chmod 600 ~/.ssh/authorized_keys
```

#### **Secret 6: VPS_PORT**
```
Name: VPS_PORT
Value: 22
```

(O el puerto SSH que uses si es diferente)

---

## 📁 **PASO 2: Crear Estructura de GitHub Actions**

### **2.1 Crear directorios**

En tu proyecto local:

```powershell
# En tu PC
cd Bot-de-telegram

# Crear estructura
mkdir -p .github\workflows
```

### **2.2 Crear archivo de workflow**

```powershell
# Crear archivo deploy.yml
notepad .github\workflows\deploy.yml
```

**Pegar este contenido:**

```yaml
name: Build and Deploy Telegram Bot

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

env:
  DOCKER_USERNAME: rvelez140
  DOCKER_IMAGE: botdetelegram
  DOCKER_TAG: latest

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 🐳 Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: 🔐 Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        
    - name: 📝 Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}
        tags: |
          type=raw,value=latest
          type=sha,prefix={{branch}}-
          
    - name: 🏗️ Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile
        push: true
        tags: |
          ${{ env.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:latest
          ${{ env.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ github.sha }}
        cache-from: type=registry,ref=${{ env.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:buildcache
        cache-to: type=registry,ref=${{ env.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:buildcache,mode=max
        
    - name: ✅ Image digest
      run: echo "Image pushed successfully!"

  deploy-to-vps:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    
    steps:
    - name: 🚀 Deploy to VPS via SSH
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USERNAME }}
        key: ${{ secrets.VPS_SSH_KEY }}
        port: ${{ secrets.VPS_PORT }}
        script: |
          cd /www/wwwroot/Bot-de-telegram
          
          echo "📥 Pulling latest code from Git..."
          git pull origin main || git pull origin master
          
          echo "🐳 Pulling latest Docker image..."
          docker compose pull
          
          echo "🔄 Restarting bot..."
          docker compose up -d
          
          echo "📊 Checking status..."
          docker compose ps
          
          echo "✅ Deployment completed!"
          
    - name: 📊 Deployment status
      run: echo "Bot deployed successfully to VPS!"
```

**Guardar y cerrar**

---

## 📤 **PASO 3: Subir a GitHub**

```powershell
# Agregar archivos
git add .github/workflows/deploy.yml
git add .

# Commit
git commit -m "Agregar CI/CD con GitHub Actions"

# Push
git push
```

---

## ✅ **PASO 4: Verificar que Funciona**

### **4.1 Ver el Workflow en GitHub**

1. Ve a tu repositorio: https://github.com/rvelez140/Bot-de-telegram
2. Click en la pestaña **"Actions"**
3. Deberías ver el workflow **"Build and Deploy Telegram Bot"** corriendo

### **4.2 Monitorear el Progreso**

Verás 2 jobs:
- ✅ **build-and-push**: Construye y sube a Docker Hub (~3-5 min)
- ✅ **deploy-to-vps**: Despliega en tu VPS (~1 min)

### **4.3 Verificar en Docker Hub**

https://hub.docker.com/r/rvelez140/botdetelegram/tags

Deberías ver:
- `latest` (actualizado hace unos minutos)
- Tag con el SHA del commit

### **4.4 Verificar en tu VPS**

```bash
ssh root@TU_IP
cd /www/wwwroot/Bot-de-telegram
docker compose ps
docker compose logs --tail=20
```

---

## 🎯 **Workflow Futuro (Automático)**

Ahora cada vez que hagas cambios:

```powershell
# 1. Editar código
notepad bot.py

# 2. Commit y push
git add .
git commit -m "Mejorar funcionalidad X"
git push

# 3. ¡LISTO! 
# GitHub automáticamente:
# - Construye imagen
# - Sube a Docker Hub
# - Despliega en VPS
```

**Tiempo total:** 5-8 minutos automáticos

---

## 🔧 **Personalizar el Workflow**

### **Cambiar cuando se ejecuta:**

```yaml
on:
  push:
    branches: [ main ]  # Solo rama main
  # O comentar esto para que NO se ejecute automáticamente
  
  workflow_dispatch:  # Mantener para ejecutar manualmente
```

### **Ejecutar manualmente:**

1. GitHub → Actions
2. Seleccionar "Build and Deploy Telegram Bot"
3. Click "Run workflow"
4. Seleccionar rama
5. Click "Run workflow"

---

## 📊 **Monitoreo y Notificaciones**

### **Ver logs del workflow:**

GitHub → Actions → Click en el workflow → Click en cada job

### **Recibir notificaciones:**

GitHub te enviará email si el workflow falla.

### **Badge en README:**

Agregar al README.md:

```markdown
![Deploy Status](https://github.com/rvelez140/Bot-de-telegram/actions/workflows/deploy.yml/badge.svg)
```

---

## 🔐 **Seguridad**

### **Secrets configurados:**

```
✅ DOCKER_USERNAME (público - está en código)
✅ DOCKER_PASSWORD (privado - secret)
✅ VPS_HOST (privado - secret)
✅ VPS_USERNAME (privado - secret)
✅ VPS_SSH_KEY (privado - secret)
✅ VPS_PORT (privado - secret)
```

### **Nunca en código:**

❌ Contraseñas
❌ Tokens de Telegram
❌ Claves SSH
❌ IPs

---

## 🎨 **Workflows Adicionales**

### **Workflow para Tests (Opcional):**

Crear `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m py_compile bot.py
```

---

## 🚨 **Troubleshooting**

### **Error: "Permission denied (publickey)"**

La clave SSH no está configurada correctamente.

**Solución:**
1. Verificar que `VPS_SSH_KEY` tiene la clave PRIVADA completa
2. Verificar que la clave PÚBLICA está en `~/.ssh/authorized_keys` del VPS

### **Error: "docker: command not found"**

Docker no está instalado en el VPS.

**Solución:**
```bash
ssh root@TU_IP
curl -fsSL https://get.docker.com | sh
```

### **Error: "Failed to login to Docker Hub"**

Credenciales incorrectas.

**Solución:**
1. Verificar `DOCKER_USERNAME` y `DOCKER_PASSWORD`
2. Usar Access Token en vez de contraseña

### **Workflow no se ejecuta**

**Solución:**
1. Verificar que el archivo está en `.github/workflows/`
2. Verificar sintaxis YAML (espacios, no tabs)
3. GitHub → Settings → Actions → Verificar que Actions está habilitado

---

## 📈 **Ventajas del CI/CD**

| Antes | Después |
|-------|---------|
| ⏱️ 15-20 min manual | ⚡ 5-8 min automático |
| 🖐️ 8 comandos manuales | ✅ 1 git push |
| ❌ Errores humanos | ✅ Proceso consistente |
| 📝 Documentación manual | ✅ Historial automático |
| 🔄 Build en tu PC o VPS | ☁️ Build en GitHub |

---

## ✅ **Checklist de Configuración**

- [ ] Secrets configurados en GitHub
- [ ] Clave SSH creada y agregada
- [ ] Archivo `.github/workflows/deploy.yml` creado
- [ ] Workflow subido a GitHub
- [ ] Workflow ejecutado exitosamente
- [ ] Imagen en Docker Hub actualizada
- [ ] Bot desplegado en VPS
- [ ] Bot funcionando correctamente

---

## 🎉 **Resultado Final**

Ahora tienes un pipeline completo:

```
Desarrollador → GitHub → Docker Hub → VPS → Bot Funcionando
     ↓             ↓          ↓         ↓          ↓
  git push     Build Auto  Push Auto  Deploy   24/7 Online
  (1 cmd)      (3-5 min)   (1 min)   (1 min)
```

**Total: ~8 minutos completamente automático** 🚀

---

¿Listo para configurar? ¡Empieza por el PASO 1! 🎯
