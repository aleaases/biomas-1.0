#!/bin/bash
# Script para verificar que el proyecto está listo para Hugging Face Spaces

echo "🔍 Verificando estructura del proyecto..."

# Verificar archivos críticos
FILES=(
    "Dockerfile"
    ".dockerignore"
    "docker-compose.yml"
    "app.py"
    "requirements.txt"
    "yolov8n.pt"
    "templates/index.html"
    ".hfignore"
)

MISSING=0

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ FALTA: $file"
        MISSING=$((MISSING+1))
    fi
done

echo ""
echo "📁 Verificando directorios..."

DIRS=(
    "templates"
    "outputs"
    "uploads"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "⚠️  Créando: $dir/"
        mkdir -p "$dir"
    fi
done

echo ""
echo "📦 Verificando dependencias en requirements.txt..."

if grep -q "Flask" requirements.txt && \
   grep -q "ultralytics" requirements.txt && \
   grep -q "torch" requirements.txt && \
   grep -q "pandas" requirements.txt; then
    echo "✅ Todas las dependencias críticas están presentes"
else
    echo "❌ Faltan dependencias importantes"
    MISSING=$((MISSING+1))
fi

echo ""
echo "📋 Verificando tamaño del modelo..."

if [ -f "yolov8n.pt" ]; then
    SIZE=$(ls -lh yolov8n.pt | awk '{print $5}')
    echo "✅ yolov8n.pt ($SIZE)"
else
    echo "❌ Modelo yolov8n.pt no encontrado"
    MISSING=$((MISSING+1))
fi

echo ""
if [ $MISSING -eq 0 ]; then
    echo "🎉 ¡El proyecto está LISTO para Hugging Face Spaces!"
    echo ""
    echo "Próximos pasos:"
    echo "1. Instala Docker (https://www.docker.com/products/docker-desktop)"
    echo "2. Lee HUGGING_FACE_DEPLOYMENT.md para instrucciones de deployment"
    echo "3. Ejecuta: docker build -t biomas-analyzer:latest ."
    echo "4. Prueba localmente: docker run -p 5000:5000 biomas-analyzer:latest"
    echo "5. Sube a Hugging Face Spaces"
    exit 0
else
    echo "⚠️  Hay $MISSING archivo(s)/validación(es) pendiente(s)"
    exit 1
fi
