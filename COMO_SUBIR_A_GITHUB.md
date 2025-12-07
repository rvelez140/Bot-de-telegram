# 📤 Guía Paso a Paso: Subir a GitHub

## 🎯 **3 Opciones para Actualizar tu Repositorio**

---

## ✅ **OPCIÓN 1: Copiar y Pegar (Más Fácil - 5 minutos)**

### **Paso 1: Descargar el archivo**

Ya tienes el archivo: `telegram_downloader_bot.tar.gz`

### **Paso 2: Extraer**

```powershell
# En PowerShell
cd Downloads
tar -xzf telegram_downloader_bot.tar.gz
```

### **Paso 3: Copiar archivos al proyecto**

```powershell
# Ir a tu proyecto
cd "C:\Users\Antuan Velez\VSCODE PROYECTO\Bot-de-telegram"

# Copiar archivos actualizados
Copy-Item "$HOME\Downloads\telegram_downloader_bot\bot.py" . -Force
Copy-Item "$HOME\Downloads\telegram_downloader_bot\requirements.txt" . -Force
Copy-Item "$HOME\Downloads\telegram_downloader_bot\Dockerfile" . -Force
Copy-Item "$HOME\Downloads\telegram_downloader_bot\.gitignore" . -Force

# Crear directorio .github\workflows si no existe
New-Item -ItemType Directory -Force -Path ".github\workflows"

# Copiar workflow
Copy-Item "$HOME\Downloads\telegram_downloader_bot\.github\workflows\deploy.yml" ".github\workflows\" -Force

# Copiar documentación nueva
Copy-Item "$HOME\Downloads\telegram_downloader_bot\CI_CD_GITHUB_ACTIONS.md" .
Copy-Item "$HOME\Downloads\telegram_downloader_bot\SETUP_SSH_RAPIDO.md" .
Copy-Item "$HOME\Downloads\telegram_downloader_bot\CONFIGURAR_COOKIES.md" .
Copy-Item "$HOME\Downloads\telegram_downloader_bot\ACTUALIZACION_RAPIDA.md" .
```

### **Paso 4: Subir a GitHub**

```powershell
# Ver qué cambió
git status

# Agregar todos los cambios
git add .

# Commit
git commit -m "✨ Agregar CI/CD automático, soporte cuentas privadas y mejoras

- Soporte para cuentas privadas con cookies
- GitHub Actions para CI/CD automático
- Mejoras en Twitter/X
- Actualización de yt-dlp
- Nuevas guías de configuración"

# Push
git push
```

### **Paso 5: Verificar**

Ve a: https://github.com/rvelez140/Bot-de-telegram

Deberías ver:
- ✅ Nuevos archivos en el repo
- ✅ Pestaña "Actions" con workflow

---

## 🔄 **OPCIÓN 2: Un Comando (Requiere que tengas el .tar.gz)**

```powershell
# Todo en uno
cd "C:\Users\Antuan Velez\VSCODE PROYECTO\Bot-de-telegram"; `
$source = "$HOME\Downloads\telegram_downloader_bot"; `
Copy-Item "$source\bot.py" . -Force; `
Copy-Item "$source\requirements.txt" . -Force; `
Copy-Item "$source\Dockerfile" . -Force; `
Copy-Item "$source\.gitignore" . -Force; `
New-Item -ItemType Directory -Force -Path ".github\workflows"; `
Copy-Item "$source\.github\workflows\deploy.yml" ".github\workflows\" -Force; `
Copy-Item "$source\*.md" . -Force; `
git add .; `
git commit -m "✨ CI/CD automático + soporte cuentas privadas"; `
git push
```

---

## 📋 **OPCIÓN 3: Archivo por Archivo (Manual)**

Si prefieres hacerlo manualmente:

### **1. Actualizar bot.py**

```powershell
cd "C:\Users\Antuan Velez\VSCODE PROYECTO\Bot-de-telegram"
code bot.py  # O notepad bot.py
```

Abre `telegram_downloader_bot/bot.py` del archivo extraído y copia todo el contenido.

### **2. Actualizar requirements.txt**

```powershell
notepad requirements.txt
```

Contenido:
```txt
python-telegram-bot==21.0.1
yt-dlp>=2024.12.23
requests==2.31.0
asyncio==3.4.3
```

### **3. Actualizar Dockerfile**

```powershell
notepad Dockerfile
```

Agregar después de `COPY bot.py .`:
```dockerfile
# Copiar cookies si existe
COPY cookies.txt /app/cookies.txt 2>/dev/null || true
```

### **4. Crear .github/workflows/deploy.yml**

```powershell
mkdir .github\workflows -Force
notepad .github\workflows\deploy.yml
```

Copiar contenido de `telegram_downloader_bot/.github/workflows/deploy.yml`

### **5. Subir**

```powershell
git add .
git commit -m "✨ CI/CD + mejoras"
git push
```

---

## 📊 **Verificar que Todo se Subió**

### **En GitHub:**

1. Ve a: https://github.com/rvelez140/Bot-de-telegram

2. **Verifica estos archivos:**
   - ✅ `bot.py` (actualizado)
   - ✅ `requirements.txt` (con yt-dlp>=2024.12.23)
   - ✅ `Dockerfile` (con cookies)
   - ✅ `.github/workflows/deploy.yml` (nuevo)
   - ✅ `CI_CD_GITHUB_ACTIONS.md` (nuevo)
   - ✅ `SETUP_SSH_RAPIDO.md` (nuevo)
   - ✅ `CONFIGURAR_COOKIES.md` (nuevo)

3. **Verifica pestaña Actions:**
   - Click en "Actions"
   - Deberías ver el workflow (puede estar corriendo)

---

## 🚨 **Troubleshooting**

### **Error: "fatal: not a git repository"**

```powershell
# Asegúrate de estar en el directorio correcto
cd "C:\Users\Antuan Velez\VSCODE PROYECTO\Bot-de-telegram"
git status
```

### **Error: "failed to push"**

```powershell
# Actualizar primero
git pull
git push
```

### **Error: "Permission denied"**

```powershell
# Configurar credenciales
git config --global user.name "rvelez140"
git config --global user.email "tu_email@example.com"

# O usar GitHub CLI
gh auth login
```

### **Archivos no se copiaron**

```powershell
# Verificar ruta del archivo extraído
ls "$HOME\Downloads\telegram_downloader_bot"

# Ajustar la ruta en los comandos si está en otro lugar
```

---

## ✅ **Checklist Final**

Antes de hacer push, verifica:

- [ ] `bot.py` actualizado (líneas ~517)
- [ ] `requirements.txt` tiene `yt-dlp>=2024.12.23`
- [ ] `Dockerfile` tiene línea de cookies
- [ ] `.gitignore` tiene `cookies*.txt`
- [ ] `.github/workflows/deploy.yml` existe
- [ ] Documentación nueva copiada

Si todo está ✅, haz push:

```powershell
git add .
git commit -m "✨ Actualización completa con CI/CD"
git push
```

---

## 🎉 **Después del Push**

1. Ve a GitHub Actions
2. Verás el workflow corriendo
3. Espera ~8 minutos
4. ¡Bot actualizado en VPS automáticamente!

---

## 📝 **Resumen de Comandos**

```powershell
# Setup inicial (solo una vez)
cd "C:\Users\Antuan Velez\VSCODE PROYECTO\Bot-de-telegram"
cd Downloads
tar -xzf telegram_downloader_bot.tar.gz

# Copiar archivos
cd "C:\Users\Antuan Velez\VSCODE PROYECTO\Bot-de-telegram"
Copy-Item "$HOME\Downloads\telegram_downloader_bot\*" . -Recurse -Force

# Subir a GitHub
git add .
git commit -m "✨ CI/CD + mejoras"
git push
```

---

¿Necesitas ayuda con algún paso específico? 🚀
