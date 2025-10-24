#!/bin/bash
# Alternative model download approach for memory-constrained environments
# This downloads models locally then copies to Docker volume

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔧 MEMORY-EFFICIENT MODEL CACHE BUILDER"
echo "═══════════════════════════════════════════════════════════════════════"
echo "⚡ Downloads models locally, then copies to Docker volume"
echo "⚡ Avoids memory issues in Docker container builds"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check Python environment
log "🔍 Checking Python environment..."

# Check if we're in project directory with .venv
if [ -d ".venv" ]; then
    log "📁 Found project virtual environment (.venv)"
    source .venv/bin/activate
    log "✅ Activated project virtual environment"
elif [ -d "venv" ]; then
    log "📁 Found project virtual environment (venv)"
    source venv/bin/activate
    log "✅ Activated project virtual environment"
elif [ ! -z "${VIRTUAL_ENV:-}" ]; then
    log "✅ Already in virtual environment: $VIRTUAL_ENV"
else
    warn "No virtual environment found, using system Python"
fi

PYTHON_VERSION=$(python --version 2>&1)
log "🐍 Python: $PYTHON_VERSION"

if ! command -v python &> /dev/null; then
    error "Python not found. Please install Python 3.8+"
    exit 1
fi

# Check required packages
log "🔍 Checking required Python packages..."
MISSING_PACKAGES=()

for package in transformers torch huggingface_hub einops pillow; do
    if ! python -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    warn "Missing packages: ${MISSING_PACKAGES[*]}"
    log "📦 Installing missing packages..."
    python -m pip install "${MISSING_PACKAGES[@]}"
fi

# Create local models directory
MODELS_DIR="./models"
mkdir -p "$MODELS_DIR"

# Download models locally
log "📥 Downloading Nomic Text v2 model..."
if python scripts/download_model.py --output "$MODELS_DIR/nomic-embed-v2"; then
    log "✅ Text model downloaded successfully"
else
    error "Failed to download text model"
    exit 1
fi

log "📥 Downloading Nomic Vision v1.5 model..."
if python scripts/download_vision_model.py --output "$MODELS_DIR/nomic-embed-vision-v1.5"; then
    log "✅ Vision model downloaded successfully"
else
    error "Failed to download vision model"
    exit 1
fi

# Check models size
log "📊 Checking downloaded models..."
TEXT_SIZE=$(du -sh "$MODELS_DIR/nomic-embed-v2" | cut -f1)
VISION_SIZE=$(du -sh "$MODELS_DIR/nomic-embed-vision-v1.5" | cut -f1)
TOTAL_SIZE=$(du -sh "$MODELS_DIR" | cut -f1)

log "   Text model:   $TEXT_SIZE"
log "   Vision model: $VISION_SIZE"
log "   Total size:   $TOTAL_SIZE"

# Create or update Docker volume
log "🐳 Creating Docker volume for model cache..."
docker volume create sutra-markdown_model_cache 2>/dev/null || true

# Copy models to Docker volume
log "📤 Copying models to Docker volume..."
docker run --rm \
    -v "$(pwd)/models:/host-models:ro" \
    -v "sutra-markdown_model_cache:/cache" \
    alpine:latest \
    sh -c "
        echo 'Copying models to cache volume...'
        cp -r /host-models/* /cache/
        echo 'Setting permissions...'
        chmod -R 755 /cache
        echo 'Verifying copy...'
        ls -la /cache/
        echo 'Cache size:'
        du -sh /cache
    "

# Verify cache
log "✅ Verifying model cache..."
CACHE_SIZE=$(docker run --rm -v sutra-markdown_model_cache:/cache alpine du -sh /cache | cut -f1)
log "   Cache size: $CACHE_SIZE"

if [[ "$CACHE_SIZE" > "1G" ]]; then
    log "✅ Model cache created successfully!"
else
    error "Model cache appears incomplete (size: $CACHE_SIZE)"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "🎉 MODEL CACHE READY"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Summary:"
echo "   • Text model:     $TEXT_SIZE"
echo "   • Vision model:   $VISION_SIZE" 
echo "   • Total cached:   $CACHE_SIZE"
echo "   • Volume:         sutra-markdown_model_cache"
echo ""
echo "🚀 Next steps:"
echo "   • Run: ./deploy_production.sh no-cache"
echo "   • Or:  docker compose up -d sutra-api"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"