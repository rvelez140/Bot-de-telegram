#!/bin/bash

# Script de Instalación Interactivo - Bot de Telegram
# Este script te guía paso a paso en la instalación

set -e

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Función para imprimir mensajes
print_step() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
clear
echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🎥  BOT DE TELEGRAM - DESCARGADOR DE VIDEOS  🎥         ║
║                                                            ║
║   Instalación Interactiva Paso a Paso                     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

sleep 2

# PASO 1: Verificar Docker
print_step "PASO 1/6: Verificando Docker"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker está instalado: $DOCKER_VERSION"
else
    print_error "Docker no está instalado"
    echo ""
    print_info "¿Deseas instalar Docker ahora? (s/n)"
    read -p "> " install_docker
    
    if [[ $install_docker == "s" || $install_docker == "S" ]]; then
        print_info "Instalando Docker..."
        
        # Detectar sistema operativo
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        fi
        
        case $OS in
            ubuntu|debian)
                sudo apt update
                sudo apt install -y ca-certificates curl gnupg
                sudo mkdir -p /etc/apt/keyrings
                curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                sudo apt update
                sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                ;;
            centos|rhel|fedora)
                sudo yum install -y yum-utils
                sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                sudo systemctl start docker
                sudo systemctl enable docker
                ;;
            *)
                print_error "Sistema operativo no soportado automáticamente"
                print_info "Por favor, instala Docker manualmente desde: https://docs.docker.com/get-docker/"
                exit 1
                ;;
        esac
        
        print_success "Docker instalado correctamente"
    else
        print_error "Docker es necesario para continuar"
        print_info "Instala Docker desde: https://docs.docker.com/get-docker/"
        exit 1
    fi
fi

# Verificar Docker Compose
if command -v docker compose &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    print_success "Docker Compose está disponible: $COMPOSE_VERSION"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose está disponible: $COMPOSE_VERSION"
    # Crear alias para docker compose
    alias docker-compose='docker compose'
else
    print_error "Docker Compose no está disponible"
    exit 1
fi

sleep 2

# PASO 2: Agregar usuario a grupo docker (opcional)
print_step "PASO 2/6: Configuración de Permisos"

if groups $USER | grep -q '\bdocker\b'; then
    print_success "Tu usuario ya está en el grupo docker"
else
    print_info "¿Deseas agregar tu usuario al grupo docker? (recomendado)"
    print_info "Esto permite usar Docker sin sudo"
    read -p "Agregar usuario al grupo docker? (s/n): " add_to_group
    
    if [[ $add_to_group == "s" || $add_to_group == "S" ]]; then
        sudo usermod -aG docker $USER
        print_success "Usuario agregado al grupo docker"
        print_warning "Necesitas cerrar sesión y volver a entrar para aplicar cambios"
        print_info "O ejecuta: newgrp docker"
    fi
fi

sleep 2

# PASO 3: Token de Telegram
print_step "PASO 3/6: Configuración del Token de Telegram"

echo ""
print_info "Para crear tu bot necesitas:"
echo "  1. Abre Telegram"
echo "  2. Busca @BotFather"
echo "  3. Envía: /newbot"
echo "  4. Sigue las instrucciones"
echo "  5. Copia el token que te proporciona"
echo ""
print_warning "El token se ve así: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
echo ""

# Verificar si ya existe .env
if [ -f .env ]; then
    print_warning "Ya existe un archivo .env"
    current_token=$(grep TELEGRAM_BOT_TOKEN .env | cut -d'=' -f2)
    if [ -n "$current_token" ]; then
        masked_token="${current_token:0:10}...${current_token: -5}"
        print_info "Token actual: $masked_token"
        read -p "¿Deseas usar el token existente? (s/n): " use_existing
        
        if [[ $use_existing == "n" || $use_existing == "N" ]]; then
            read -p "Ingresa tu nuevo TELEGRAM_BOT_TOKEN: " bot_token
            echo "TELEGRAM_BOT_TOKEN=$bot_token" > .env
            chmod 600 .env
            print_success "Nuevo token configurado"
        else
            print_success "Usando token existente"
        fi
    else
        read -p "Ingresa tu TELEGRAM_BOT_TOKEN: " bot_token
        echo "TELEGRAM_BOT_TOKEN=$bot_token" > .env
        chmod 600 .env
        print_success "Token configurado"
    fi
else
    read -p "Ingresa tu TELEGRAM_BOT_TOKEN: " bot_token
    
    if [ -z "$bot_token" ]; then
        print_error "El token no puede estar vacío"
        exit 1
    fi
    
    echo "TELEGRAM_BOT_TOKEN=$bot_token" > .env
    chmod 600 .env
    print_success "Archivo .env creado y configurado"
fi

sleep 2

# PASO 4: Crear directorio de descargas
print_step "PASO 4/6: Preparando Directorios"

if [ ! -d "downloads" ]; then
    mkdir -p downloads
    print_success "Directorio de descargas creado"
else
    print_success "Directorio de descargas ya existe"
fi

sleep 1

# PASO 5: Construir imagen
print_step "PASO 5/6: Construyendo Imagen Docker"

print_info "Esto puede tomar unos minutos la primera vez..."
echo ""

if docker compose build; then
    print_success "Imagen construida exitosamente"
else
    print_error "Error al construir la imagen"
    exit 1
fi

sleep 2

# PASO 6: Iniciar bot
print_step "PASO 6/6: Iniciando el Bot"

print_info "Iniciando el contenedor..."
echo ""

if docker compose up -d; then
    print_success "Bot iniciado correctamente"
else
    print_error "Error al iniciar el bot"
    exit 1
fi

sleep 2

# Verificar estado
print_step "Verificando Estado del Bot"

sleep 3

if docker compose ps | grep -q "Up"; then
    print_success "El bot está corriendo correctamente"
else
    print_error "El bot no está corriendo"
    print_info "Ver logs con: docker compose logs -f"
    exit 1
fi

# Mostrar información final
clear
echo -e "${GREEN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              ✅  INSTALACIÓN COMPLETADA  ✅                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

print_success "Tu bot de Telegram está listo para usar"
echo ""
print_info "🤖 Comandos útiles:"
echo "  • Ver logs:        docker compose logs -f"
echo "  • Detener bot:     docker compose stop"
echo "  • Iniciar bot:     docker compose start"
echo "  • Reiniciar bot:   docker compose restart"
echo "  • Ver estado:      docker compose ps"
echo "  • Actualizar bot:  docker compose up -d --build"
echo ""
print_info "📱 Probar el bot en Telegram:"
echo "  1. Abre Telegram"
echo "  2. Busca tu bot por el username que le diste"
echo "  3. Envía /start"
echo "  4. Envía un enlace de video para probar"
echo ""
print_info "📚 Documentación:"
echo "  • README.md - Documentación completa"
echo "  • FAQ.md - Preguntas frecuentes"
echo "  • ADVANCED.md - Configuración avanzada"
echo "  • INSTALACION_DOCKER.md - Guía detallada de Docker"
echo ""

read -p "¿Deseas ver los logs del bot ahora? (s/n): " show_logs

if [[ $show_logs == "s" || $show_logs == "S" ]]; then
    echo ""
    print_info "Mostrando logs (presiona Ctrl+C para salir)..."
    sleep 2
    docker compose logs -f
fi

echo ""
print_success "¡Disfruta tu bot! 🎉"
