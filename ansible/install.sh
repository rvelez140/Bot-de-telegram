#!/usr/bin/env bash
# ============================================================================
# Telegram Video Bot - Instalador de un solo comando
# ============================================================================
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/rvelez140/Bot-de-telegram/main/ansible/install.sh | bash
#
# O localmente:
#   bash ansible/install.sh
# ============================================================================

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    cat << 'BANNER'

  _____ _____ _     _____ ____ ____      _    __  __
 |_   _| ____| |   | ____/ ___|  _ \   / \  |  \/  |
   | | |  _| | |   |  _|| |  _| |_) | / _ \ | |\/| |
   | | | |___| |___| |__| |_| |  _ < / ___ \| |  | |
   |_| |_____|_____|_____\____|_| \_/_/   \_|_|  |_|

  VIDEO BOT - ANSIBLE INSTALLER

BANNER
    echo -e "${NC}"
}

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Este script debe ejecutarse como root o con sudo"
        echo "  sudo bash $0"
        exit 1
    fi
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME="$NAME"
        OS_VERSION="$VERSION_ID"
        OS_FAMILY="debian"
        if [[ "$ID" == "centos" || "$ID" == "rhel" || "$ID" == "fedora" ]]; then
            OS_FAMILY="redhat"
        fi
    elif [[ "$(uname)" == "Darwin" ]]; then
        OS_NAME="macOS"
        OS_VERSION="$(sw_vers -productVersion)"
        OS_FAMILY="darwin"
    else
        log_error "Sistema operativo no soportado"
        exit 1
    fi
    log_info "Sistema detectado: $OS_NAME $OS_VERSION ($OS_FAMILY)"
}

install_ansible() {
    log_info "Verificando Ansible..."

    if command -v ansible-playbook &> /dev/null; then
        local version
        version=$(ansible --version | head -1)
        log_success "Ansible ya instalado: $version"
        return 0
    fi

    log_info "Instalando Ansible..."

    case "$OS_FAMILY" in
        debian)
            apt-get update -qq
            apt-get install -y -qq software-properties-common
            apt-get install -y -qq ansible python3-pip
            ;;
        redhat)
            yum install -y epel-release
            yum install -y ansible python3-pip
            ;;
        darwin)
            if command -v brew &> /dev/null; then
                brew install ansible
            else
                pip3 install ansible
            fi
            ;;
    esac

    log_success "Ansible instalado: $(ansible --version | head -1)"
}

install_galaxy_deps() {
    log_info "Instalando dependencias de Ansible Galaxy..."

    local req_file="ansible/requirements.yml"
    if [ -f "$req_file" ]; then
        ansible-galaxy collection install -r "$req_file" --force
        log_success "Dependencias de Galaxy instaladas"
    else
        log_warn "No se encontro requirements.yml, saltando"
    fi
}

configure_bot() {
    echo ""
    echo -e "${CYAN}=== Configuracion del Bot ===${NC}"
    echo ""

    # Token del bot
    if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
        read -rp "Ingresa tu TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN
        if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
            log_error "El token del bot es obligatorio"
            exit 1
        fi
    fi

    # Flask secret key
    if [ -z "${FLASK_SECRET_KEY:-}" ]; then
        FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
        log_info "Clave Flask generada automaticamente"
    fi

    # Tailscale
    read -rp "Habilitar Tailscale VPN? (s/n) [n]: " enable_tailscale
    TAILSCALE_ENABLED="false"
    TAILSCALE_AUTHKEY=""
    if [[ "${enable_tailscale,,}" == "s" ]]; then
        TAILSCALE_ENABLED="true"
        read -rp "Tailscale auth key (opcional): " TAILSCALE_AUTHKEY
    fi

    log_success "Configuracion completada"
}

run_playbook() {
    log_info "Ejecutando playbook de Ansible..."
    echo ""

    local extra_vars=(
        -e "telegram_bot_token=${TELEGRAM_BOT_TOKEN}"
        -e "flask_secret_key=${FLASK_SECRET_KEY}"
        -e "tailscale_enabled=${TAILSCALE_ENABLED}"
    )

    if [ -n "$TAILSCALE_AUTHKEY" ]; then
        extra_vars+=(-e "tailscale_authkey=${TAILSCALE_AUTHKEY}")
    fi

    ansible-playbook ansible/playbook.yml \
        -i "localhost," \
        --connection=local \
        "${extra_vars[@]}" \
        -v

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}"
        cat << 'DONE'
  ============================================
      DESPLIEGUE COMPLETADO EXITOSAMENTE
  ============================================
DONE
        echo -e "${NC}"
        echo ""
        log_success "Bot desplegado y corriendo"
        echo ""
        log_info "Comandos utiles:"
        echo "  sudo systemctl status telegram-video-bot   # Estado del servicio"
        echo "  sudo journalctl -u telegram-video-bot -f   # Ver logs"
        echo "  sudo systemctl restart telegram-video-bot  # Reiniciar"
        echo ""
        log_info "Prueba tu bot:"
        echo "  1. Busca tu bot en Telegram"
        echo "  2. Envia /start"
        echo "  3. Envia un enlace de video"
        echo ""
    else
        log_error "El playbook fallo con codigo: $exit_code"
        log_info "Revisa los logs arriba para mas detalles"
        exit $exit_code
    fi
}

# --- Main ---
main() {
    print_banner
    check_root
    detect_os
    install_ansible
    install_galaxy_deps
    configure_bot
    run_playbook
}

main "$@"
