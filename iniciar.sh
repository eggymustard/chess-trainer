#!/bin/bash

# Obtener la ruta absoluta del directorio donde está este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Colores para la terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

echo -e "${YELLOW}=== Verificando Chess Trainer ===${NC}"
ERRORS=0

# 1. Verificar Python y librerías
if ! command -v python &> /dev/null; then
    echo -e "${RED}[ERROR] Python no está instalado.${NC}"
    ERRORS=$((ERRORS+1))
else
    python -c "import pygame, chess, requests" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Faltan librerías de Python (pygame, chess, requests).${NC}"
        echo "        Ejecuta: pip install -r requirements.txt"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}[OK] Python y librerías listas.${NC}"
    fi
fi

# 2. Verificar binarios locales (bin/)
for bin in stockfish ollama piper_bin; do
    if [ ! -x "bin/$bin" ]; then
        echo -e "${RED}[ERROR] Falta el binario bin/$bin o no es ejecutable.${NC}"
        ERRORS=$((ERRORS+1))
    fi
done
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}[OK] Binarios locales (Stockfish, Ollama, Piper) listos.${NC}"
fi

# 3. Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}[ERROR] FFmpeg no está instalado. (Necesario para el audio del coach).${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}[OK] FFmpeg instalado.${NC}"
fi

# 4. Verificar modelo de voz de Piper
if [ ! -f "assets/models/piper/es_MX-claude-high.onnx" ]; then
    echo -e "${RED}[ERROR] Falta el modelo de voz de Piper en assets/models/piper/${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}[OK] Modelo de voz de Piper listo.${NC}"
fi

# 5. Verificar modelo de Ollama (Qwen)
if [ ! -d "models/manifests" ]; then
    echo -e "${RED}[ERROR] Falta el modelo de IA (Qwen) en models/.${NC}"
    echo "        Ejecuta: ollama pull qwen2.5:3b"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}[OK] Modelo de IA (Qwen) listo.${NC}"
fi

# 6. Verificar sonidos
if [ ! -f "assets/sounds/Move.wav" ]; then
    echo -e "${RED}[ERROR] Faltan los archivos de sonido en assets/sounds/${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}[OK] Sonidos del juego listos.${NC}"
fi

# Si hay errores, detener el proceso
if [ $ERRORS -gt 0 ]; then
    echo -e "\n${RED}======================================${NC}"
    echo -e "${RED}Se encontraron $ERRORS errores. Corrígelos antes de jugar.${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Todo verificado correctamente.${NC}"

# --- CREAR LANZADOR DE ESCRITORIO ---
# Detectar automáticamente el nombre de la carpeta del escritorio (Desktop o Escritorio)
DESKTOP_DIR=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")
# Si no existe, probar con la versión en español
if [ ! -d "$DESKTOP_DIR" ] && [ -d "$HOME/Escritorio" ]; then
    DESKTOP_DIR="$HOME/Escritorio"
fi

APPS_DIR="$HOME/.local/share/applications"
APPS_LANZADOR="$APPS_DIR/chess-trainer.desktop"

crear_lanzador() {
    local ruta_destino=$1
    cat > "$ruta_destino" << EOF
[Desktop Entry]
Type=Application
Name=Chess Trainer
Comment=Juego de ajedrez con entrenador IA local
Exec=$DIR/iniciar.sh
Icon=$DIR/assets/icon.png
Terminal=true
Categories=Game;BoardGame;
EOF
    chmod +x "$ruta_destino"
    # Intentar marcar como confiable en GNOME/KDE para evitar el cartel de "archivo no seguro"
    gio set "$ruta_destino" metadata::trusted true 2>/dev/null
}

# Crear en el escritorio (si la carpeta existe)
if [ -d "$DESKTOP_DIR" ]; then
    crear_lanzador "$DESKTOP_DIR/chess-trainer.desktop"
    echo -e "${GREEN}[OK] Lanzador creado en el Escritorio ($DESKTOP_DIR).${NC}"
else
    echo -e "${YELLOW}[AVISO] No se encontró la carpeta del escritorio. Se creará solo en el menú.${NC}"
fi

# Crear en el menú de aplicaciones
mkdir -p "$APPS_DIR"
crear_lanzador "$APPS_LANZADOR"
echo -e "${GREEN}[OK] Lanzador creado en el Menú de Aplicaciones.${NC}"

echo -e "\n${YELLOW}Iniciando Ollama en segundo plano...${NC}"

# Configurar Ollama para usar la carpeta local
export OLLAMA_MODELS="$DIR/models"
export OLLAMA_HOST="127.0.0.1:11434"

# Matar instancias previas de Ollama para evitar conflictos
killall ollama 2>/dev/null
sleep 1

# Iniciar Ollama
./bin/ollama serve &
OLLAMA_PID=$!

# Esperar a que Ollama esté listo
sleep 2

echo -e "${GREEN}Iniciando Chess Trainer...${NC}"

# Ejecutar el juego
python main.py

# Al cerrar el juego, apagar Ollama
echo -e "\n${YELLOW}Cerrando Ollama...${NC}"
kill $OLLAMA_PID 2>/dev/null
