# 🌐 Aplicación Web - Video Downloader

Interfaz web para gestionar cuentas y descargar videos de redes sociales.

## 📋 Características

### ✅ Funcionalidades Implementadas

1. **Sistema de Autenticación**
   - Registro de usuarios con validación
   - Login seguro con hash de contraseñas
   - Sesiones persistentes (7 días)

2. **Gestión de Cuentas de Redes Sociales**
   - Configuración de cuentas de Twitter/X
   - Login automatizado con Playwright
   - Almacenamiento seguro de cookies
   - Eliminación de cuentas

3. **Descarga de Videos**
   - Soporte para TikTok, YouTube, Twitter/X, Instagram
   - Descarga directa desde el navegador
   - Uso automático de cuentas configuradas para contenido privado
   - Historial de descargas

4. **Interfaz Moderna**
   - Diseño responsive
   - Dashboard intuitivo
   - Feedback visual en tiempo real

## 🚀 Inicio Rápido

### Opción 1: Con Docker Compose (Recomendado)

```bash
# 1. Configurar variables de entorno
cp .env.example .env
nano .env  # Configurar TELEGRAM_BOT_TOKEN y FLASK_SECRET_KEY

# 2. Generar clave secreta para Flask
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))" >> .env

# 3. Crear directorio de datos
mkdir -p data

# 4. Iniciar servicios
docker-compose up -d

# 5. Verificar logs
docker-compose logs -f web-interface
```

La aplicación web estará disponible en: **http://localhost:5000**

### Opción 2: Ejecutar Localmente (Sin Docker)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar navegadores de Playwright
playwright install chromium

# 3. Configurar variables de entorno
export FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export DOWNLOAD_DIR=./downloads
export DATABASE_PATH=./web_users.db

# 4. Crear directorios
mkdir -p downloads

# 5. Ejecutar aplicación
python web_app.py
```

La aplicación web estará disponible en: **http://localhost:5000**

## 📖 Guía de Uso

### 1. Registro e Inicio de Sesión

1. Accede a **http://localhost:5000**
2. Haz clic en "Regístrate aquí"
3. Crea una cuenta con:
   - Usuario (mínimo 3 caracteres)
   - Contraseña (mínimo 6 caracteres)
4. Inicia sesión con tus credenciales

### 2. Configurar Cuenta de Twitter/X

Para descargar videos de cuentas privadas de Twitter/X:

1. Ve a la sección **"Cuentas"** en el menú
2. Selecciona **"Twitter/X"** en el formulario
3. Ingresa tus credenciales de Twitter/X:
   - Usuario o email de Twitter
   - Contraseña
4. Haz clic en **"Agregar Cuenta"**
5. Espera mientras el sistema inicia sesión automáticamente
6. ¡Listo! Ahora puedes descargar contenido privado

**Nota:** Tu contraseña NO se guarda. Solo se utilizan cookies de sesión.

### 3. Descargar Videos

1. Ve al **Dashboard**
2. Pega la URL del video en el campo de descarga
3. Haz clic en **"Descargar"**
4. Espera mientras se procesa el video
5. El video se descargará automáticamente

**Plataformas soportadas:**
- 🎵 TikTok
- ▶️ YouTube
- 🐦 Twitter/X
- 📷 Instagram

### 4. Ver Historial

En el Dashboard puedes ver tus últimas 10 descargas con:
- URL del video
- Plataforma
- Fecha y hora de descarga

## 🔐 Seguridad

### Prácticas de Seguridad Implementadas

✅ **Contraseñas hasheadas** con Werkzeug (bcrypt)
✅ **Cookies de sesión seguras** con clave secreta
✅ **No se almacenan contraseñas** de redes sociales
✅ **Cookies encriptadas** en base de datos SQLite
✅ **Sesiones con expiración** (7 días)
✅ **Archivos temporales eliminados** después de descargar
✅ **Protección CSRF** integrada en Flask

### Recomendaciones

1. **Cambia la clave secreta** en producción:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Usa HTTPS** en producción con un proxy inverso (nginx, Caddy)

3. **Configura firewall** para proteger el puerto 5000

4. **Actualiza regularmente** las dependencias:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 🗄️ Base de Datos

La aplicación utiliza SQLite con las siguientes tablas:

### `web_users`
- `id`: ID único del usuario
- `username`: Nombre de usuario (único)
- `password_hash`: Contraseña hasheada
- `created_at`: Fecha de creación

### `social_accounts`
- `id`: ID único de la cuenta
- `user_id`: ID del usuario propietario
- `platform`: Plataforma (twitter, instagram, etc.)
- `platform_username`: Usuario en la plataforma
- `cookies`: Cookies de sesión (encriptadas)
- `created_at`: Fecha de creación
- `updated_at`: Fecha de actualización

### `download_history`
- `id`: ID único de la descarga
- `user_id`: ID del usuario
- `url`: URL del video descargado
- `platform`: Plataforma
- `filename`: Nombre del archivo
- `downloaded_at`: Fecha de descarga

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Por Defecto |
|----------|-------------|-------------|
| `FLASK_SECRET_KEY` | Clave secreta para sesiones | `(generada aleatoriamente)` |
| `WEB_PORT` | Puerto del servidor web | `5000` |
| `DOWNLOAD_DIR` | Directorio de descargas | `/downloads` |
| `DATABASE_PATH` | Ruta de la base de datos | `web_users.db` |

### Personalización de Puertos

Para cambiar el puerto de la aplicación web:

```yaml
# docker-compose.yml
services:
  web-interface:
    ports:
      - "8080:5000"  # Cambiar 8080 por el puerto deseado
```

O en ejecución local:

```bash
export WEB_PORT=8080
python web_app.py
```

### Proxy Inverso con Nginx

Ejemplo de configuración para usar con nginx:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🐛 Solución de Problemas

### Error: "No se puede conectar a la base de datos"

```bash
# Verificar permisos del directorio
chmod 755 data/
chmod 644 data/web_users.db
```

### Error: "Login de Twitter/X falla"

- Verifica que tus credenciales sean correctas
- Asegúrate de que Playwright esté instalado:
  ```bash
  playwright install chromium
  ```
- Revisa los logs para más detalles:
  ```bash
  docker-compose logs -f web-interface
  ```

### Error: "No se puede descargar el video"

- Verifica que la URL sea válida
- Para contenido privado, asegúrate de tener una cuenta configurada
- Revisa que yt-dlp esté actualizado:
  ```bash
  pip install --upgrade yt-dlp
  ```

## 📊 Monitoreo

### Ver Logs en Docker

```bash
# Todos los servicios
docker-compose logs -f

# Solo la aplicación web
docker-compose logs -f web-interface

# Últimas 100 líneas
docker-compose logs --tail=100 web-interface
```

### Healthcheck

La aplicación tiene un healthcheck que verifica su estado cada 30 segundos:

```bash
# Ver estado del servicio
docker-compose ps

# Debería mostrar "healthy" en el estado
```

## 🔄 Actualización

Para actualizar la aplicación web:

```bash
# 1. Detener servicios
docker-compose down

# 2. Obtener últimos cambios
git pull

# 3. Reconstruir imágenes
docker-compose build web-interface

# 4. Iniciar servicios
docker-compose up -d

# 5. Verificar logs
docker-compose logs -f web-interface
```

## 📝 Notas Adicionales

- La base de datos se guarda en `./data/web_users.db` para persistencia
- Los archivos descargados se eliminan automáticamente después de 1 minuto
- Las sesiones de usuario duran 7 días por defecto
- Las cookies de redes sociales se actualizan automáticamente al reconfigurar una cuenta

## 🤝 Integración con el Bot de Telegram

La aplicación web y el bot de Telegram funcionan de manera independiente:

- **Bot de Telegram**: Para uso mediante chat de Telegram
- **Aplicación Web**: Para uso mediante navegador web

Ambos comparten:
- Directorio de descargas (`/downloads`)
- Mismas capacidades de descarga
- Soporte para las mismas plataformas

## 📞 Soporte

Para reportar problemas o sugerir mejoras, abre un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo la misma licencia que el bot de Telegram principal.
