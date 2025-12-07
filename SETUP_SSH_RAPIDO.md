# 🔑 Configuración Rápida de SSH para GitHub Actions

## ⚡ **Setup en 5 Minutos**

### **En tu PC (Windows):**

```powershell
# 1. Generar clave SSH (si no tienes)
ssh-keygen -t ed25519 -C "github-actions-bot" -f ~/.ssh/github_actions_bot

# Presiona Enter 3 veces (sin passphrase)

# 2. Ver clave PRIVADA (para GitHub Secret)
Get-Content ~/.ssh/github_actions_bot

# 3. Ver clave PÚBLICA (para VPS)
Get-Content ~/.ssh/github_actions_bot.pub
```

---

### **En tu VPS:**

```bash
# Conectar
ssh root@TU_IP

# Agregar clave pública
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
```

**Pegar la clave PÚBLICA (de github_actions_bot.pub)**

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Proteger archivo
chmod 600 ~/.ssh/authorized_keys

# Probar desde tu PC
exit
```

---

### **Probar Conexión:**

```powershell
# En tu PC
ssh -i ~/.ssh/github_actions_bot root@TU_IP
```

Si conecta sin pedir contraseña → **✅ Funcionó**

---

## 📋 **Secrets para GitHub**

Copia estos valores:

### **1. VPS_HOST**
```
Tu IP del VPS
```

### **2. VPS_USERNAME**
```
root
```

### **3. VPS_PORT**
```
22
```

### **4. VPS_SSH_KEY**
```
Contenido COMPLETO de: ~/.ssh/github_actions_bot
(desde -----BEGIN hasta -----END-----)
```

### **5. DOCKER_USERNAME**
```
rvelez140
```

### **6. DOCKER_PASSWORD**
```
Tu contraseña de Docker Hub
O mejor: Access Token de https://hub.docker.com/settings/security
```

---

## 🔧 **Agregar Secrets en GitHub**

1. Ve a: https://github.com/rvelez140/Bot-de-telegram/settings/secrets/actions
2. Click "New repository secret"
3. Agregar cada uno de los 6 secrets de arriba
4. ✅ Listo

---

## ✅ **Verificación Rápida**

```bash
# Verificar que SSH funciona
ssh -i ~/.ssh/github_actions_bot root@TU_IP "echo 'SSH OK'"

# Debe imprimir: SSH OK
```

---

## 🚨 **Si no Funciona**

### **Error: Permission denied**

```bash
# En el VPS, verificar permisos
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Verificar contenido
cat ~/.ssh/authorized_keys
```

### **Error: Host key verification failed**

```powershell
# En tu PC, agregar host conocido
ssh-keyscan TU_IP >> ~/.ssh/known_hosts
```

---

## 📝 **Resumen**

**En tu PC:**
1. Generar clave SSH
2. Copiar clave privada

**En tu VPS:**
1. Agregar clave pública

**En GitHub:**
1. Agregar 6 secrets

**¡Listo!** 🎉

---

## 🔐 **Seguridad**

- ✅ Clave SSH sin passphrase (para automatización)
- ✅ Clave privada solo en GitHub Secrets
- ✅ Clave pública en VPS
- ✅ Permisos correctos (600/700)
- ✅ Nunca compartas la clave privada

---

¿Problemas? Revisa: `CI_CD_GITHUB_ACTIONS.md` - Sección Troubleshooting
