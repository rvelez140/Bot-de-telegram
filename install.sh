#!/bin/bash

# Script de instalación rápida para el Bot de Telegram
# Descargador de Videos

set -e

echo "🎥 Bot de Telegram - Descargador de Videos"
echo "=========================================="
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado."
    echo "Por favor, instala Docker primero: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado."
    echo "Por favor, instala Docker Compose primero: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker y Docker Compose están instalados"
echo ""

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "📝 Configurando el bot..."
    echo ""
    echo "Necesitas el token de tu bot de Telegram."
    echo "Si no lo tienes, obtén uno de @BotFather en Telegram:"
    echo "  1. Abre Telegram y busca @BotFather"
    echo "  2. Envía /newbot"
    echo "  3. Sigue las instrucciones"
    echo "  4. Copia el token que te proporciona"
    echo ""
    read -p "Ingresa tu TELEGRAM_BOT_TOKEN: " bot_token
    
    if [ -z "$bot_token" ]; then
        echo "❌ Token no puede estar vacío"
        exit 1
    fi
    
    echo "TELEGRAM_BOT_TOKEN=$bot_token" > .env
    echo "✅ Archivo .env creado"
else
    echo "✅ Archivo .env ya existe"
fi

echo ""
echo "🏗️  Construyendo la imagen Docker..."
docker-compose build

echo ""
echo "🚀 Iniciando el bot..."
docker-compose up -d

echo ""
echo "✅ ¡Bot iniciado con éxito!"
echo ""
echo "📊 Comandos útiles:"
echo "  - Ver logs:        docker-compose logs -f"
echo "  - Detener bot:     docker-compose stop"
echo "  - Reiniciar bot:   docker-compose restart"
echo "  - Eliminar bot:    docker-compose down"
echo ""
echo "🤖 Tu bot está listo para usar en Telegram"
echo ""

# Mostrar logs iniciales
echo "📋 Mostrando logs (presiona Ctrl+C para salir)..."
sleep 2
docker-compose logs -f
