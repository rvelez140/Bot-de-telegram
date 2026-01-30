#!/usr/bin/env bash
# ============================================================================
# Health Check - Verifica el estado del bot y sus servicios
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
check_fail() { echo -e "${RED}[FAIL]${NC} $1"; ERRORS=$((ERRORS + 1)); }
check_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

ERRORS=0

echo "=== Telegram Video Bot - Health Check ==="
echo ""

# Docker
if command -v docker &> /dev/null; then
    check_ok "Docker instalado: $(docker --version | head -c 50)"
else
    check_fail "Docker no instalado"
fi

# Docker Compose
if docker compose version &> /dev/null; then
    check_ok "Docker Compose: $(docker compose version | head -c 50)"
else
    check_fail "Docker Compose no disponible"
fi

# Contenedores
if docker ps --format '{{.Names}}' | grep -q "telegram-video-downloader"; then
    check_ok "Contenedor del bot: corriendo"
else
    check_fail "Contenedor del bot: no esta corriendo"
fi

if docker ps --format '{{.Names}}' | grep -q "video-downloader-web"; then
    check_ok "Contenedor web: corriendo"
else
    check_warn "Contenedor web: no esta corriendo (puede ser opcional)"
fi

# Servicio systemd
if systemctl is-active telegram-video-bot &> /dev/null; then
    check_ok "Servicio systemd: activo"
else
    check_warn "Servicio systemd: no activo"
fi

# Firewall
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "active"; then
        check_ok "UFW Firewall: activo"
    else
        check_warn "UFW Firewall: inactivo"
    fi
fi

# Tailscale
if command -v tailscale &> /dev/null; then
    if tailscale status &> /dev/null; then
        check_ok "Tailscale: conectado"
    else
        check_warn "Tailscale: instalado pero no conectado"
    fi
fi

# Disco
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_ok "Espacio en disco: ${DISK_USAGE}% usado"
elif [ "$DISK_USAGE" -lt 90 ]; then
    check_warn "Espacio en disco: ${DISK_USAGE}% usado"
else
    check_fail "Espacio en disco: ${DISK_USAGE}% usado (critico)"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Todos los checks pasaron.${NC}"
else
    echo -e "${RED}$ERRORS check(s) fallaron.${NC}"
    exit 1
fi
