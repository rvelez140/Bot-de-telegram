#!/bin/bash

# Script de Despliegue Automático para VPS con aaPanel
# Uso: ./deploy.sh

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        BOT DE TELEGRAM - DESPLIEGUE EN VPS/AAPANEL        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Variables
INSTALL_DIR="/www/wwwroot/telegram-video-bot"
REPO_URL=""

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar si estamos ejecutando como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    print_warning "Este script debe ejecutarse como root o con sudo"
    print_info "Intentando con sudo..."
    sudo "$0" "$@"
    exit $?
fi

# PASO 1: Verificar Docker
echo ""
print_info "PASO 1/7: Verificando Docker..."

if command -v docker &> /dev/null; then
    print_success "Docker está instalado"
else
    print_warning "Docker no está instalado. Instalando..."
    
    # Instalar Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    print_success "Docker instalado"
fi

# Verificar Docker Compose
if command -v docker compose &> /dev/null || command -v docker-compose &> /dev/null; then
    print_success "Docker Compose está disponible"
else
    print_info "Instalando Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose instalado"
fi

# PASO 2: Verificar Git
echo ""
print_info "PASO 2/7: Verificando Git..."

if command -v git &> /dev/null; then
    print_success "Git está instalado"
else
    print_info "Instalando Git..."
    
    if [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y git
    elif [ -f /etc/redhat-release ]; then
        yum install -y git
    fi
    
    print_success "Git instalado"
fi

# PASO 3: Solicitar información del repositorio
echo ""
print_info "PASO 3/7: Configuración del Repositorio"

# Verificar si ya existe el directorio
if [ -d "$INSTALL_DIR" ]; then
    print_warning "El directorio $INSTALL_DIR ya existe"
    read -p "¿Deseas eliminarlo y volver a clonar? (s/n): " remove_dir
    
    if [[ $remove_dir == "s" || $remove_dir == "S" ]]; then
        # Detener contenedor si está corriendo
        if [ -f "$INSTALL_DIR/docker-compose.yml" ]; then
            cd "$INSTALL_DIR"
            docker compose down 2>/dev/null || true
        fi
        
        rm -rf "$INSTALL_DIR"
        print_success "Directorio eliminado"
    else
        print_info "Usando directorio existente"
        cd "$INSTALL_DIR"
        
        # Actualizar desde Git
        print_info "Actualizando desde Git..."
        git pull
        
        # Saltar al paso de configuración
        SKIP_CLONE=true
    fi
fi

# Clonar repositorio si es necesario
if [ "$SKIP_CLONE" != "true" ]; then
    echo ""
    print_info "Opciones de origen del código:"
    echo "  1. Clonar desde GitHub/GitLab"
    echo "  2. Usar código local (ya extraído)"
    read -p "Selecciona opción (1 o 2): " code_option
    
    if [ "$code_option" == "1" ]; then
        read -p "URL del repositorio Git: " REPO_URL
        
        if [ -z "$REPO_URL" ]; then
            print_error "URL no puede estar vacía"
            exit 1
        fi
        
        # Crear directorio base si no existe
        mkdir -p /www/wwwroot
        
        # Clonar repositorio
        print_info "Clonando repositorio..."
        cd /www/wwwroot
        git clone "$REPO_URL" telegram-video-bot
        
        print_success "Repositorio clonado"
        
    elif [ "$code_option" == "2" ]; then
        # Copiar código local
        print_info "Copiando código desde directorio actual..."
        
        # Verificar que estamos en el directorio correcto
        if [ ! -f "bot.py" ]; then
            print_error "No se encuentra bot.py en el directorio actual"
            print_info "Asegúrate de ejecutar este script desde el directorio del proyecto"
            exit 1
        fi
        
        mkdir -p "$INSTALL_DIR"
        cp -r . "$INSTALL_DIR/"
        print_success "Código copiado a $INSTALL_DIR"
    else
        print_error "Opción inválida"
        exit 1
    fi
fi

# PASO 4: Configurar Token
cd "$INSTALL_DIR"

echo ""
print_info "PASO 4/7: Configuración del Token"

if [ -f ".env" ]; then
    print_warning "Ya existe un archivo .env"
    current_token=$(grep TELEGRAM_BOT_TOKEN .env | cut -d'=' -f2)
    
    if [ -n "$current_token" ]; then
        masked_token="${current_token:0:10}...${current_token: -5}"
        print_info "Token actual: $masked_token"
        read -p "¿Deseas mantener este token? (s/n): " keep_token
        
        if [[ $keep_token == "n" || $keep_token == "N" ]]; then
            read -p "Ingresa tu nuevo TELEGRAM_BOT_TOKEN: " new_token
            echo "TELEGRAM_BOT_TOKEN=$new_token" > .env
            print_success "Token actualizado"
        else
            print_success "Usando token existente"
        fi
    else
        read -p "Ingresa tu TELEGRAM_BOT_TOKEN: " new_token
        echo "TELEGRAM_BOT_TOKEN=$new_token" > .env
        print_success "Token configurado"
    fi
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
    fi
    
    read -p "Ingresa tu TELEGRAM_BOT_TOKEN: " new_token
    echo "TELEGRAM_BOT_TOKEN=$new_token" > .env
    print_success "Archivo .env creado"
fi

# Proteger archivo .env
chmod 600 .env
chown www:www .env 2>/dev/null || chown $(whoami):$(whoami) .env

# PASO 5: Crear directorios necesarios
echo ""
print_info "PASO 5/7: Creando directorios..."

mkdir -p downloads
chmod 755 downloads

print_success "Directorios creados"

# PASO 6: Construir imagen Docker
echo ""
print_info "PASO 6/7: Construyendo imagen Docker..."
print_warning "Esto puede tomar varios minutos..."

if docker compose build; then
    print_success "Imagen construida correctamente"
else
    print_error "Error al construir la imagen"
    exit 1
fi

# PASO 7: Iniciar contenedor
echo ""
print_info "PASO 7/7: Iniciando el bot..."

# Detener contenedor anterior si existe
docker compose down 2>/dev/null || true

# Iniciar nuevo contenedor
if docker compose up -d; then
    print_success "Bot iniciado correctamente"
else
    print_error "Error al iniciar el bot"
    exit 1
fi

# Esperar un poco
sleep 3

# Verificar estado
echo ""
print_info "Verificando estado del bot..."

if docker compose ps | grep -q "Up"; then
    print_success "¡El bot está corriendo!"
else
    print_error "El bot no está corriendo"
    print_info "Revisar logs con: docker compose logs"
    exit 1
fi

# Resumen final
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              ✅  DESPLIEGUE COMPLETADO  ✅                 ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

print_success "Tu bot está corriendo en el VPS"
echo ""
print_info "📍 Ubicación: $INSTALL_DIR"
print_info "🐳 Contenedor: telegram-video-downloader"
echo ""
print_info "📊 Comandos útiles:"
echo "  cd $INSTALL_DIR"
echo "  docker compose logs -f       # Ver logs"
echo "  docker compose restart       # Reiniciar"
echo "  docker compose stop          # Detener"
echo "  docker compose ps            # Ver estado"
echo ""
print_info "🔄 Para actualizar desde Git:"
echo "  cd $INSTALL_DIR"
echo "  git pull"
echo "  docker compose up -d --build"
echo ""
print_info "📱 Prueba tu bot en Telegram:"
echo "  1. Busca tu bot"
echo "  2. Envía /start"
echo "  3. Envía un enlace de video"
echo ""

# Ofrecer ver logs
read -p "¿Deseas ver los logs ahora? (s/n): " show_logs

if [[ $show_logs == "s" || $show_logs == "S" ]]; then
    echo ""
    print_info "Mostrando logs (presiona Ctrl+C para salir)..."
    sleep 2
    docker compose logs -f
fi

print_success "¡Listo! 🎉"
