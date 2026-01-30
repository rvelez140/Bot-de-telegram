# Modelo de Seguridad

## Defensa en Profundidad (4 capas)

Basado en el modelo de seguridad de
[clawdbot-ansible](https://github.com/moltbot/clawdbot-ansible),
adaptado para el Telegram Video Bot.

### Capa 1: Firewall de Red (UFW)

- **Politica por defecto**: deny incoming, allow outgoing, deny routed
- **Puertos abiertos**: Solo SSH (22/tcp) y Tailscale (41641/udp)
- **Puerto web (5000)**: NO expuesto publicamente por defecto

```
$ sudo ufw status
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
41641/udp                  ALLOW       Anywhere    # Solo si Tailscale habilitado
```

### Capa 2: DOCKER-USER iptables Chain

Incluso si un contenedor mapea un puerto (ej: `-p 80:80`), la chain
DOCKER-USER impide que sea accesible desde la interfaz externa.

Reglas aplicadas en `/etc/ufw/after.rules`:
- Permite conexiones establecidas (ESTABLISHED, RELATED)
- Permite trafico localhost (127.0.0.0/8)
- Permite redes Docker internas (172.16.0.0/12)
- Permite Tailscale (100.64.0.0/10)
- **DROP todo lo demas** desde la interfaz externa

### Capa 3: Localhost Binding

El docker-compose.override.yml configura el puerto web como:

```yaml
ports:
  - "127.0.0.1:5000:5000"  # Solo accesible localmente
```

Para acceso externo, usa un reverse proxy (nginx/caddy) o Tailscale.

### Capa 4: Proceso Non-Root + systemd Hardening

El servicio systemd aplica:
- `NoNewPrivileges=true`: previene escalacion de privilegios
- `PrivateTmp=true`: namespace tmp aislado
- `ProtectSystem=strict`: filesystem read-only (excepto paths permitidos)
- `ProtectHome=read-only`: home directory solo lectura
- `ReadWritePaths`: solo el directorio del bot es escribible

### Docker Daemon Hardened

`/etc/docker/daemon.json`:
```json
{
  "iptables": true,
  "ip-forward": true,
  "userland-proxy": false,
  "live-restore": true,
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

**Nota**: `iptables: true` se mantiene intencionalmente activo.
Desactivarlo romperia la red de contenedores.

## Acceso a la Interfaz Web

Por defecto, la web solo es accesible via:

1. **Localhost**: `http://127.0.0.1:5000` (SSH tunnel)
2. **Tailscale**: `http://100.x.y.z:5000` (si habilitado)
3. **Reverse Proxy**: nginx/caddy con HTTPS

Para SSH tunnel:
```bash
ssh -L 5000:127.0.0.1:5000 user@tu-servidor
# Luego abrir: http://localhost:5000
```
