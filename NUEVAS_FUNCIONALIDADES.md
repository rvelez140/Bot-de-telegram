# 🆕 Nuevas Funcionalidades - Bot de Telegram

## ✨ Actualizaciones Implementadas

### 1. 🖼️ **Descarga de Imágenes**

Ahora el bot puede descargar imágenes además de videos.

**Plataformas soportadas para imágenes:**
- Instagram (posts e imágenes)
- Twitter/X (imágenes de tweets)
- TikTok (imágenes de posts)

**Ejemplo de uso:**
```
https://www.instagram.com/p/ABC123xyz/
```

El bot detectará automáticamente si es una imagen o video y lo descargará en la máxima calidad disponible.

---

### 2. 📦 **División Automática de Videos Grandes**

Videos que superan los 2GB se dividen automáticamente en partes iguales.

**Características:**
- ✅ División automática sin intervención del usuario
- ✅ Cada parte es de ~1.9GB (máximo permitido por Telegram)
- ✅ Partes numeradas claramente (Parte 1/3, Parte 2/3, etc.)
- ✅ Mantiene la calidad original del video
- ✅ Cada parte es independiente y reproducible

**Ejemplo:**
```
Video de 5GB:
└─> Parte 1/3 (1.9GB)
└─> Parte 2/3 (1.9GB)
└─> Parte 3/3 (1.2GB)
```

**El bot muestra:**
```
✅ Video 1/1 - Parte 1/3

📝 Título del video
🌐 YOUTUBE
💾 Tamaño: 1900.0MB
```

---

### 3. 📎 **Procesamiento Múltiple de Enlaces**

Envía varios enlaces a la vez y el bot los procesará todos automáticamente.

**Características:**
- ✅ Procesa múltiples enlaces en una sola solicitud
- ✅ Soporta mezcla de plataformas
- ✅ Progreso en tiempo real
- ✅ Ignora enlaces no soportados
- ✅ Continúa aunque uno falle

**Ejemplo de uso:**

Envía varios enlaces en un solo mensaje:
```
https://www.tiktok.com/@usuario/video/123
https://www.youtube.com/watch?v=abc123
https://www.instagram.com/p/xyz789/
https://twitter.com/user/status/456
```

**El bot procesará:**
```
📥 Procesando 4 enlace(s)...

⏳ Procesando 1/4 - TIKTOK...
✅ Video enviado

⏳ Procesando 2/4 - YOUTUBE...
✅ Video enviado

⏳ Procesando 3/4 - INSTAGRAM...
✅ Imagen enviada

⏳ Procesando 4/4 - TWITTER...
✅ Video enviado

✅ Procesamiento completado
📊 Total: 4 archivo(s)
```

---

## 📝 Comandos Actualizados

### `/start` - Mensaje de Bienvenida
Ahora menciona:
- Soporte para imágenes
- División automática de videos grandes
- Capacidad de procesar múltiples enlaces

### `/help` - Ayuda
Incluye ejemplos de:
- Un solo enlace
- Múltiples enlaces
- Información sobre división de videos

### `/platforms` - Plataformas Soportadas
Actualizado con:
- Mención de imágenes por plataforma
- División automática de videos
- Funciones especiales

---

## 🎯 Casos de Uso

### Caso 1: Descargar un Video Normal
```
Usuario envía: https://www.tiktok.com/@user/video/123
Bot descarga: Video sin marca de agua
Bot envía: 1 archivo de video
```

### Caso 2: Descargar un Video Grande (>2GB)
```
Usuario envía: https://www.youtube.com/watch?v=video_largo
Bot descarga: Video de 4GB
Bot divide: En 3 partes
Bot envía: 
  - Parte 1/3 (1.9GB)
  - Parte 2/3 (1.9GB)
  - Parte 3/3 (0.2GB)
```

### Caso 3: Descargar una Imagen
```
Usuario envía: https://www.instagram.com/p/imagen123/
Bot descarga: Imagen en máxima calidad
Bot envía: 1 archivo de imagen
```

### Caso 4: Descargar Múltiples Archivos
```
Usuario envía:
  https://tiktok.com/video1
  https://youtube.com/video2
  https://instagram.com/imagen1
  
Bot procesa: Los 3 enlaces
Bot envía: 
  - Video de TikTok
  - Video de YouTube (dividido si es grande)
  - Imagen de Instagram
```

### Caso 5: Mezcla con Enlaces No Soportados
```
Usuario envía:
  https://tiktok.com/video1
  https://unsupported-site.com/video
  https://youtube.com/video2
  
Bot informa: "1 enlace no soportado será ignorado"
Bot procesa: Solo TikTok y YouTube
Bot envía: 2 videos
```

---

## 🔧 Detalles Técnicos

### División de Videos

**Método utilizado:** FFmpeg con codec copy
- No recodifica el video (mantiene calidad)
- División rápida
- Sin pérdida de calidad

**Tamaños:**
- Límite Telegram: 2GB (2000MB)
- Tamaño por parte: 1.9GB (1900MB) - margen de seguridad
- Si video = 5GB → 3 partes (1.9GB, 1.9GB, 1.2GB)

**Formato de nombres:**
```
{título}_parte1de3.mp4
{título}_parte2de3.mp4
{título}_parte3de3.mp4
```

### Detección Automática Imagen/Video

El bot intenta primero descargar como video:
1. Si es video → Descarga exitosa
2. Si falla → Intenta como imagen
3. Si falla → Muestra error

Esto permite manejar URLs que pueden contener ambos tipos de contenido.

### Procesamiento Asíncrono

**Ventajas:**
- Descarga múltiples archivos sin bloquear
- Actualiza progreso en tiempo real
- No bloquea otras solicitudes del bot

**Limitaciones:**
- Procesa enlaces en orden
- Pausa de 1 segundo entre descargas (evitar saturación)
- Si un enlace falla, continúa con los siguientes

---

## 📊 Límites y Consideraciones

### Límites de Telegram:
- **Tamaño máximo por archivo:** 2GB
- **Solución:** División automática en partes
- **Tipo de archivos:** Videos, imágenes, documentos

### Límites del Bot:
- **Videos grandes:** Se dividen automáticamente
- **Múltiples enlaces:** Sin límite específico, pero recomendado <10 por mensaje
- **Tiempo de procesamiento:** Depende del tamaño y cantidad

### Recomendaciones:
- Para videos >10GB, considera enviarlos en mensajes separados
- Para >5 enlaces, envía en grupos pequeños
- Videos muy largos (>2 horas) pueden tardar varios minutos

---

## 🎓 Ejemplos Prácticos

### Ejemplo 1: Clase de YouTube Completa
```
Usuario necesita: Video de clase de 3 horas (4GB)

Envía: https://youtube.com/watch?v=clase_completa

Bot procesa:
⏳ Descargando video...
📦 Video muy grande (4000MB), dividiendo...
📤 Enviando parte 1/3...
📤 Enviando parte 2/3...
📤 Enviando parte 3/3...

Usuario recibe:
✅ Video 1/1 - Parte 1/3 (1.9GB)
✅ Video 1/1 - Parte 2/3 (1.9GB)
✅ Video 1/1 - Parte 3/3 (0.2GB)
```

### Ejemplo 2: Galería de Instagram
```
Usuario necesita: 5 imágenes de diferentes posts

Envía:
https://instagram.com/p/post1/
https://instagram.com/p/post2/
https://instagram.com/p/post3/
https://instagram.com/p/post4/
https://instagram.com/p/post5/

Bot procesa:
📥 Procesando 5 enlace(s)...
⏳ Procesando 1/5 - INSTAGRAM...
⏳ Procesando 2/5 - INSTAGRAM...
⏳ Procesando 3/5 - INSTAGRAM...
⏳ Procesando 4/5 - INSTAGRAM...
⏳ Procesando 5/5 - INSTAGRAM...

Usuario recibe:
✅ Imagen 1/5
✅ Imagen 2/5
✅ Imagen 3/5
✅ Imagen 4/5
✅ Imagen 5/5
✅ Procesamiento completado: 5 archivos
```

### Ejemplo 3: Mezcla de Contenido
```
Usuario necesita: Videos de diferentes plataformas

Envía:
https://tiktok.com/@user/video/123
https://youtube.com/watch?v=abc (5GB)
https://instagram.com/p/imagen/
https://twitter.com/user/status/456

Bot procesa:
📥 Procesando 4 enlace(s)...

Usuario recibe:
✅ Video 1/4 (TikTok sin marca de agua)
✅ Video 2/4 - Parte 1/3 (YouTube)
✅ Video 2/4 - Parte 2/3 (YouTube)
✅ Video 2/4 - Parte 3/3 (YouTube)
✅ Imagen 3/4 (Instagram)
✅ Video 4/4 (Twitter)

✅ Procesamiento completado
📊 Total: 4 archivo(s)
```

---

## 🔄 Actualización del Bot

Para actualizar tu bot con estas nuevas funcionalidades:

### En tu VPS:

```bash
# Conectar al VPS
ssh root@TU_IP

# Ir al directorio
cd /www/wwwroot/Bot-de-telegram

# Descargar cambios desde Git
git pull

# Reconstruir imagen Docker
docker compose down
docker compose build
docker compose up -d

# Verificar logs
docker compose logs -f
```

### Si ya actualizaste el código en GitHub:

El nuevo código ya incluye todas estas funcionalidades. Solo necesitas hacer `git pull` en tu VPS y reconstruir el contenedor.

---

## ✅ Verificación de Funcionalidades

Prueba cada funcionalidad nueva:

**1. Probar imagen:**
```
/start
https://www.instagram.com/p/[algún_post_con_imagen]/
```

**2. Probar video grande:**
```
https://www.youtube.com/watch?v=[video_largo_>2GB]
```

**3. Probar múltiples enlaces:**
```
https://tiktok.com/@user/video/123
https://youtube.com/watch?v=abc
https://instagram.com/p/xyz/
```

---

## 🐛 Troubleshooting

### Error: "Failed to split video"
**Causa:** ffmpeg no disponible o problema al dividir  
**Solución:** El bot enviará el video completo si la división falla

### Error: "Cannot process multiple URLs"
**Causa:** Regex no detecta URLs correctamente  
**Solución:** Verifica que cada URL esté en una línea nueva

### Error: "Image download failed"
**Causa:** El contenido no es una imagen o está protegido  
**Solución:** Verifica que el enlace sea público

### Videos divididos no se reproducen bien
**Causa:** División incorrecta  
**Solución:** Usa un player que soporte partes divididas o únelas con:
```bash
cat parte1.mp4 parte2.mp4 parte3.mp4 > completo.mp4
```

---

## 📈 Mejoras Futuras (Opcional)

Ideas para implementar después:

- [ ] Descarga de playlists completas
- [ ] Conversión de formato automática
- [ ] Compresión de videos muy grandes
- [ ] Subtítulos automáticos
- [ ] Historial de descargas por usuario
- [ ] Sistema de cola para muchos enlaces
- [ ] Unión automática de partes antes de enviar
- [ ] Preview/thumbnail antes de descargar

---

¡Disfruta las nuevas funcionalidades! 🎉
