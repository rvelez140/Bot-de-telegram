# Arquitectura de Despliegue con Ansible

## Resumen

Este directorio integra un sistema de automatizacion basado en Ansible,
inspirado en [clawdbot-ansible](https://github.com/moltbot/clawdbot-ansible),
adaptado para el despliegue seguro del Telegram Video Bot.

## Estructura de directorios

```
ansible/
├── playbook.yml                    # Playbook principal
├── inventory.yml.example           # Inventario de ejemplo
├── requirements.yml                # Dependencias de Ansible Galaxy
├── install.sh                      # Instalador de un comando
├── run-playbook.sh                 # Runner del playbook
├── .ansible-lint                   # Configuracion de linting
├── .yamllint                       # Configuracion YAML lint
│
├── roles/
│   └── telegram-bot/
│       ├── defaults/main.yml       # Variables por defecto
│       ├── files/
│       │   └── health-check.sh     # Script de verificacion
│       ├── handlers/main.yml       # Handlers (restart, reload)
│       ├── tasks/
│       │   ├── main.yml            # Orquestador de tareas
│       │   ├── system-tools.yml    # Dispatcher OS
│       │   ├── system-tools-linux.yml
│       │   ├── system-tools-redhat.yml
│       │   ├── system-tools-macos.yml
│       │   ├── user.yml            # Creacion de usuario
│       │   ├── docker.yml          # Dispatcher Docker
│       │   ├── docker-linux.yml    # Docker CE Linux
│       │   ├── docker-macos.yml    # Docker Desktop macOS
│       │   ├── firewall.yml        # Dispatcher firewall
│       │   ├── firewall-linux.yml  # UFW + DOCKER-USER chain
│       │   ├── firewall-macos.yml  # App Firewall
│       │   ├── tailscale.yml       # Dispatcher Tailscale
│       │   ├── tailscale-linux.yml
│       │   ├── tailscale-macos.yml
│       │   └── deploy.yml          # Despliegue del bot
│       └── templates/
│           ├── daemon.json.j2              # Docker daemon config
│           ├── docker-compose.override.yml.j2  # Override hardened
│           ├── env.j2                      # Archivo .env
│           └── telegram-bot.service.j2     # Servicio systemd
│
└── docs/
    ├── architecture.md             # Este archivo
    └── security.md                 # Modelo de seguridad
```

## Fases de Ejecucion

El playbook ejecuta las tareas en orden critico:

```
Fase 1: System Tools
  └── Instala git, curl, ffmpeg, etc. (apt/yum/brew)

Fase 2: Tailscale VPN (opcional)
  └── Mesh VPN para acceso remoto seguro

Fase 3: User Management
  └── Crea usuario 'telegrambot' dedicado

Fase 4: Docker
  └── Docker CE + Compose v2 + daemon.json hardened

Fase 5: Firewall (CRITICO: despues de Docker)
  └── UFW + DOCKER-USER iptables chain

Fase 6: Deploy
  └── Clona repo, configura .env, docker compose up
```

El orden es critico: Docker debe instalarse ANTES del firewall
porque `/etc/docker/daemon.json` debe existir cuando se configura
la chain DOCKER-USER.

## Capas de Seguridad

Implementa el modelo de 4 capas adaptado de clawdbot-ansible:

1. **Red (UFW)**: deny incoming, allow outgoing, deny routed
2. **Contenedor (DOCKER-USER)**: iptables chain que bloquea acceso externo
3. **Binding**: Docker ports solo en 127.0.0.1
4. **Proceso**: usuario non-root + systemd hardening
