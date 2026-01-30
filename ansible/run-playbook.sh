#!/usr/bin/env bash
# ============================================================================
# Playbook Runner - Ejecuta el playbook con manejo de privilegios
# ============================================================================
# Uso:
#   ./run-playbook.sh                           # Ejecucion local
#   ./run-playbook.sh -i inventory.yml          # Con inventario personalizado
#   ./run-playbook.sh -e telegram_bot_token=XXX # Con variables extra
#   ./run-playbook.sh --tags deploy             # Solo desplegar
#   ./run-playbook.sh --check                   # Dry run
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verificar que estamos en el directorio correcto
if [ ! -f "$SCRIPT_DIR/playbook.yml" ]; then
    echo "Error: No se encuentra playbook.yml en $SCRIPT_DIR"
    exit 1
fi

# Verificar Ansible
if ! command -v ansible-playbook &> /dev/null; then
    echo "Error: ansible-playbook no encontrado."
    echo "Instala Ansible primero:"
    echo "  pip3 install ansible"
    echo "  # o"
    echo "  apt-get install ansible"
    exit 1
fi

# Instalar dependencias de Galaxy si no estan instaladas
if [ -f "$SCRIPT_DIR/requirements.yml" ]; then
    echo "Verificando dependencias de Ansible Galaxy..."
    ansible-galaxy collection install -r "$SCRIPT_DIR/requirements.yml" 2>/dev/null || true
fi

# Detectar si necesitamos sudo/become
BECOME_FLAGS=""
if [ "$EUID" -ne 0 ]; then
    BECOME_FLAGS="--become --ask-become-pass"
    echo "No eres root. Se solicitara la contrasena de sudo."
fi

# Inventario por defecto
DEFAULT_INVENTORY="$SCRIPT_DIR/inventory.yml"
if [ ! -f "$DEFAULT_INVENTORY" ]; then
    DEFAULT_INVENTORY="localhost,"
fi

# Ejecutar playbook
echo ""
echo "=== Ejecutando Playbook de Telegram Video Bot ==="
echo ""

# shellcheck disable=SC2086
ansible-playbook "$SCRIPT_DIR/playbook.yml" \
    -i "$DEFAULT_INVENTORY" \
    $BECOME_FLAGS \
    "$@"
