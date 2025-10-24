#!/bin/bash
# Complete Docker Cleanup & Fresh Installation Script for Sutra-Markdown
# This script performs a complete cleanup and fresh installation

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

# Configuration variables
BUILD_ENV=${BUILD_ENV:-production}
DEPLOYMENT_MODE=${DEPLOYMENT_MODE:-standard}  # standard, high-performance, development
REMOVE_DEV_DEPS=${REMOVE_DEV_DEPS:-true}

# Main header
print_header() {
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}🧹 SUTRA-MARKDOWN PRODUCTION-OPTIMIZED DEPLOYMENT${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}⚡ Mode: ${BUILD_ENV^^} | Deployment: ${DEPLOYMENT_MODE^^}${NC}"
    echo -e "${YELLOW}⚡ Production optimizations: Smaller images, no dev deps${NC}"
    echo -e "${YELLOW}⚡ High-performance embedding service for 10K+ requests${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! docker compose version &> /dev/null; then
        error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Check available disk space (need at least 10GB)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS version
        AVAILABLE_GB=$(df -g . | awk 'NR==2 {print $4}')
    else
        # Linux version
        AVAILABLE_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    fi
    
    if [ "$AVAILABLE_GB" -lt 10 ]; then
        error "Insufficient disk space. Need at least 10GB free, have ${AVAILABLE_GB}GB"
        exit 1
    fi
    
    success "Prerequisites check passed (${AVAILABLE_GB}GB available)"
}

# Complete Docker cleanup
complete_docker_cleanup() {
    log "🧹 Starting complete Docker cleanup..."
    
    # Stop all running containers
    info "Stopping all running containers..."
    if docker ps -q | xargs -r docker stop 2>/dev/null; then
        success "All containers stopped"
    else
        info "No running containers to stop"
    fi
    
    # Remove all containers
    info "Removing all containers..."
    if docker ps -a -q | xargs -r docker rm -f 2>/dev/null; then
        success "All containers removed"
    else
        info "No containers to remove"
    fi
    
    # Remove all custom images (keep base images like redis, nginx)
    info "Removing Sutra-specific Docker images..."
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}" | grep -E "(sutra|local)" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
    
    # Remove all volumes
    info "Removing all Docker volumes..."
    if docker volume ls -q | xargs -r docker volume rm -f 2>/dev/null; then
        success "All volumes removed"
    else
        info "No volumes to remove"
    fi
    
    # Remove all custom networks (keep default networks)
    info "Removing custom Docker networks..."
    docker network ls --format "{{.Name}}" | grep -v -E "(bridge|host|none)" | xargs -r docker network rm 2>/dev/null || true
    
    # Clean up system
    info "Cleaning up Docker system..."
    docker system prune -a -f --volumes >/dev/null 2>&1 || true
    
    success "Complete Docker cleanup finished"
}

# Setup environment
setup_environment() {
    log "⚙️ Setting up environment configuration..."
    
    # Create .env.docker if it doesn't exist
    if [ ! -f ".env.docker" ]; then
        info "Creating .env.docker configuration..."
        cat > .env.docker << 'EOF'
# Sutra-Markdown Production Environment Configuration

# Application Environment
APP_ENV=production
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Embedding Configuration (LOCAL for best performance)
EMBEDDING_MODE=local
NOMIC_DEVICE=auto
NOMIC_BATCH_SIZE=64

# LLM API Keys (for Tier 3 conversions - optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Redis Configuration
REDIS_URL=redis://redis:6379/0
ENABLE_CACHE=true
CACHE_TTL=86400

# MinIO Configuration
MINIO_ROOT_USER=${MINIO_ROOT_USER:-minioadmin}
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-$(openssl rand -base64 24)}
MINIO_BUCKET_NAME=sutra-documents

# Performance Settings
MAX_WORKERS=10
BATCH_SIZE=100
MAX_FILE_SIZE_MB=500

# Tier Thresholds
TIER_1_THRESHOLD=0.6
TIER_2_THRESHOLD=0.8

# Security (generate new values in production)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET=your-jwt-secret-change-in-production
EOF
        success ".env.docker created with default configuration"
    else
        info ".env.docker already exists, keeping current configuration"
    fi
    
    # Create necessary directories
    info "Creating required directories..."
    mkdir -p cache logs uploads outputs models
    
    # Set permissions
    chmod 755 cache logs uploads outputs models
    
    success "Environment setup completed"
}

# Build model cache
build_fresh_model_cache() {
    log "📦 Building fresh model cache..."
    
    info "This will download AI models (~2.5GB total):"
    echo "   • Nomic Text v2 Embeddings (~1.8GB)"
    echo "   • Nomic Vision v1.5 Embeddings (~355MB)"
    echo ""
    
    if [ -x "./build_model_cache.sh" ]; then
        info "Using local model cache builder..."
        if ./build_model_cache.sh; then
            success "Model cache built successfully"
        else
            error "Failed to build model cache"
            exit 1
        fi
    else
        warn "build_model_cache.sh not found or not executable"
        info "Building model cache via Docker..."
        
        # Create model cache volume
        docker volume create sutra-markdown_model_cache
        
        # Download models using temporary container
        info "Downloading models using Docker..."
        docker run --rm \
            -v sutra-markdown_model_cache:/app/models \
            -e HF_HOME=/app/models/.cache \
            python:3.11-slim bash -c "
                pip install huggingface_hub sentence-transformers torch
                python -c '
from sentence_transformers import SentenceTransformer
import os

# Set cache directory
os.environ[\"HF_HOME\"] = \"/app/models/.cache\"

# Download models
print(\"Downloading Nomic Text v2...\")
model1 = SentenceTransformer(\"nomic-ai/nomic-embed-text-v1.5\", cache_folder=\"/app/models\")

print(\"Downloading Nomic Vision v1.5...\")  
model2 = SentenceTransformer(\"nomic-ai/nomic-embed-vision-v1.5\", cache_folder=\"/app/models\")

print(\"Models downloaded successfully!\")
'
            "
        
        success "Model cache built via Docker"
    fi
    
    # Verify cache size
    CACHE_SIZE=$(docker run --rm -v sutra-markdown_model_cache:/cache alpine sh -c "du -sm /cache 2>/dev/null | cut -f1" || echo "0")
    if [ "$CACHE_SIZE" -gt 1000 ]; then
        success "Model cache verified (${CACHE_SIZE}MB)"
    else
        warn "Model cache may not be complete (${CACHE_SIZE}MB)"
    fi
}

# Create production environment file
create_production_env() {
    log "📝 Creating production environment configuration..."
    
    # Create optimized .env file for the deployment mode
    cat > .env << EOF
# Production Configuration - Optimized for Performance
BUILD_ENV=${BUILD_ENV}
APP_ENV=production

# Performance Settings
MAX_WORKERS=${MAX_WORKERS:-10}
BATCH_SIZE=${BATCH_SIZE:-100}
NOMIC_BATCH_SIZE=${NOMIC_BATCH_SIZE:-64}
EMBEDDING_WORKERS=${EMBEDDING_WORKERS:-4}

# Resource Limits (adjust based on your hardware)
API_CPU_LIMIT=${API_CPU_LIMIT:-2}
API_MEMORY_LIMIT=${API_MEMORY_LIMIT:-6G}
API_CPU_RESERVE=1
API_MEMORY_RESERVE=3G

# Embedding Worker Resources
EMBEDDING_CPU_LIMIT=2
EMBEDDING_MEMORY_LIMIT=4G
EMBEDDING_CPU_RESERVE=1
EMBEDDING_MEMORY_RESERVE=2G

# Caching
CACHE_ENABLED=true
CACHE_TTL=86400

# MinIO Settings
MINIO_ROOT_USER=sutra
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-$(openssl rand -base64 24)}
MINIO_BUCKET_NAME=sutra-documents

# Development mode settings (only if BUILD_ENV=development)
$(if [ "$BUILD_ENV" = "development" ]; then
    echo "DEV_CODE_MOUNT=./sutra"
    echo "DEV_CODE_MODE=rw"
else
    echo "DEV_CODE_MOUNT=/dev/null"
    echo "DEV_CODE_MODE=ro"
fi)
EOF
    
    success "Environment configuration created"
}

# Remove development dependencies from requirements
optimize_requirements() {
    if [ "$REMOVE_DEV_DEPS" = "true" ] && [ "$BUILD_ENV" = "production" ]; then
        log "🧹 Optimizing requirements for production..."
        
        # Create backup
        cp requirements.txt requirements-full-backup.txt
        
        # Remove development dependencies
        info "Removing Jupyter, testing, and documentation dependencies..."
        
        # Create temporary production requirements
        grep -v -E "(jupyter|ipython|ipdb|pytest|black|ruff|mypy|mkdocs|pre-commit|watchdog)" requirements.txt > requirements-temp.txt
        
        # Replace original with optimized version
        mv requirements-temp.txt requirements.txt
        
        success "Requirements optimized - removed $(wc -l < requirements-full-backup.txt) -> $(wc -l < requirements.txt) packages"
        warn "Full requirements backed up to requirements-full-backup.txt"
    fi
}

# Build application
build_application() {
    log "🏗️ Building production-optimized application..."
    
    # Build with appropriate build arguments
    local build_args="--build-arg BUILD_ENV=${BUILD_ENV}"
    
    info "Building Sutra API service (${BUILD_ENV} mode)..."
    if docker compose build --no-cache ${build_args} sutra-api; then
        success "Sutra API built successfully"
    else
        error "Failed to build Sutra API"
        exit 1
    fi
    
    # Build Web UI
    info "Building Web UI..."
    if docker compose build --no-cache web-ui; then
        success "Web UI built successfully"
    else
        warn "Web UI build failed (continuing without it)"
    fi
    
    # Build embedding workers if using high-performance mode
    if [ "$DEPLOYMENT_MODE" = "high-performance" ]; then
        info "Building embedding workers for high-performance mode..."
        docker compose build --no-cache ${build_args} embedding-worker
        success "Embedding workers built successfully"
    fi
}

# Deploy services
deploy_services() {
    log "🚀 Deploying services in ${DEPLOYMENT_MODE} mode..."
    
    # Start infrastructure services first
    info "Starting infrastructure services (Redis, MinIO)..."
    docker compose up -d redis minio
    
    # Wait for infrastructure
    info "Waiting for infrastructure to be ready..."
    sleep 15
    
    # Check infrastructure health
    for i in {1..30}; do
        if docker compose ps --format json 2>/dev/null | grep -q '"Health":"healthy"'; then
            success "Infrastructure services are healthy"
            break
        fi
        
        if [ $i -eq 30 ]; then
            error "Infrastructure services failed to start"
            docker compose ps
            docker compose logs
            exit 1
        fi
        
        echo -n "."
        sleep 2
    done
    echo ""
    
    # Deploy based on mode
    case "$DEPLOYMENT_MODE" in
        "high-performance")
            info "Deploying high-performance mode with embedding workers..."
            docker compose --profile high-performance up -d sutra-api
            
            # Scale embedding workers
            local workers=${EMBEDDING_SCALE:-3}
            info "Scaling embedding workers to $workers instances..."
            docker compose --profile high-performance up -d --scale embedding-worker=$workers
            ;;
        "development")
            info "Deploying development mode..."
            docker compose --profile api up -d sutra-api
            ;;
        *)
            info "Deploying standard production mode..."
            docker compose --profile api up -d sutra-api
            ;;
    esac
    
    # Wait for application
    info "Waiting for application to be ready..."
    for i in {1..60}; do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            success "Application is running and healthy!"
            break
        fi
        
        if [ $i -eq 60 ]; then
            error "Application failed to start"
            docker compose logs sutra-api
            exit 1
        fi
        
        echo -n "."
        sleep 3
    done
    echo ""
    
    # Start Web UI
    info "Starting Web UI..."
    docker compose up -d web-ui
    sleep 10
}

# Run validation tests
run_validation_tests() {
    log "🧪 Running validation tests..."
    
    # Test API health
    info "Testing API health..."
    if curl -sf http://localhost:8000/health | jq -r '.status' | grep -q "healthy"; then
        success "✅ API health check passed"
    else
        error "❌ API health check failed"
        return 1
    fi
    
    # Test API documentation
    info "Testing API documentation..."
    if curl -sf http://localhost:8000/docs >/dev/null; then
        success "✅ API documentation accessible"
    else
        warn "⚠️ API documentation not accessible"
    fi
    
    # Test conversion endpoint
    info "Testing conversion endpoint..."
    if curl -sf -X POST http://localhost:8000/convert \
        -F "file=@README.md" >/dev/null 2>&1; then
        success "✅ Conversion endpoint working"
    else
        warn "⚠️ Conversion endpoint test failed (may need warmup)"
    fi
    
    success "Validation tests completed"
}

# Show final status
show_final_status() {
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}🎉 PRODUCTION-OPTIMIZED DEPLOYMENT COMPLETED!${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}📊 Deployment Configuration:${NC}"
    echo -e "   • ${GREEN}Mode:${NC}             ${BUILD_ENV^^}"
    echo -e "   • ${GREEN}Deployment:${NC}       ${DEPLOYMENT_MODE^^}"
    echo -e "   • ${GREEN}Dev Dependencies:${NC}  $([ "$REMOVE_DEV_DEPS" = "true" ] && echo "REMOVED ✅" || echo "INCLUDED")"
    
    # Show image size improvements
    local current_size
    current_size=$(docker images --format "{{.Size}}" sutra-markdown-sutra-api:latest 2>/dev/null || echo "Unknown")
    echo -e "   • ${GREEN}Image Size:${NC}       $current_size (vs 3.65GB before optimization)"
    echo ""
    
    echo -e "${CYAN}🌐 Available Services:${NC}"
    echo -e "   • ${GREEN}Sutra API:${NC}        http://localhost:8000"
    echo -e "   • ${GREEN}API Documentation:${NC} http://localhost:8000/docs"  
    echo -e "   • ${GREEN}Health Check:${NC}     http://localhost:8000/health"
    echo -e "   • ${GREEN}Web UI:${NC}           http://localhost:3000"
    
    if [ "$DEPLOYMENT_MODE" = "high-performance" ]; then
        echo -e "   • ${GREEN}Embedding Workers:${NC} $(docker ps --format "table {{.Names}}" | grep embedding-worker | wc -l) instances"
    fi
    echo ""
    echo -e "${CYAN}🔧 Infrastructure:${NC}"
    echo -e "   • ${GREEN}Redis:${NC}            localhost:6379"
    echo -e "   • ${GREEN}MinIO Console:${NC}    http://localhost:9001"
    echo -e "     └─ Username: ${MINIO_ROOT_USER} / Password: ${MINIO_ROOT_PASSWORD}"
    echo ""
    echo -e "${CYAN}💾 System Status:${NC}"
    
    # Get service status
    echo -e "   • ${GREEN}Running Services:${NC}"
    docker compose ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}" | grep -E "(redis|minio|sutra-api|web-ui)" | while read line; do
        echo "     └─ $line"
    done
    
    # Model cache info
    CACHE_SIZE=$(docker run --rm -v sutra-markdown_model_cache:/cache alpine sh -c "du -sm /cache 2>/dev/null | cut -f1" || echo "0")
    echo -e "   • ${GREEN}Model Cache:${NC}      ${CACHE_SIZE}MB (persistent)"
    
    echo ""
    echo -e "${CYAN}⚡ Quick Commands:${NC}"
    echo -e "   • View logs:          ${YELLOW}docker compose logs -f sutra-api${NC}"
    echo -e "   • Stop services:      ${YELLOW}docker compose down${NC}" 
    echo -e "   • Restart services:   ${YELLOW}docker compose restart${NC}"
    echo -e "   • Update services:    ${YELLOW}docker compose pull && docker compose up -d${NC}"
    echo -e "   • Scale API:          ${YELLOW}docker compose up -d --scale sutra-api=3${NC}"
    echo ""
    echo -e "${CYAN}🧪 Test Conversion:${NC}"
    echo -e "   ${YELLOW}curl -X POST http://localhost:8000/convert -F \"file=@yourfile.pdf\"${NC}"
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════${NC}"
}

# Confirmation prompt
confirm_cleanup() {
    echo ""
    warn "⚠️  This will COMPLETELY REMOVE all Docker containers, images, and volumes!"
    warn "⚠️  Any existing data will be lost permanently!"
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Operation cancelled."
        exit 0
    fi
    echo ""
}

# Main execution function
main() {
    print_header
    
    # Ask for confirmation
    confirm_cleanup
    
    # Run all steps
    check_prerequisites
    complete_docker_cleanup
    setup_environment
    create_production_env
    optimize_requirements
    build_fresh_model_cache
    build_application
    deploy_services
    run_validation_tests
    show_final_status
    
    success "🎯 Fresh installation completed successfully!"
    echo ""
    info "🌟 Your Sutra-Markdown system is now ready for production use!"
}

# Handle script arguments
case "${1:-full}" in
    "cleanup-only")
        print_header
        confirm_cleanup
        check_prerequisites
        complete_docker_cleanup
        success "Docker cleanup completed"
        ;;
    "build-only") 
        print_header
        check_prerequisites
        build_fresh_model_cache
        build_application
        success "Build completed"
        ;;
    "deploy-only")
        print_header
        check_prerequisites
        deploy_services
        run_validation_tests
        show_final_status
        success "Deployment completed"
        ;;
    "full"|"")
        main
        ;;
    *)
        echo "Usage: $0 [full|cleanup-only|build-only|deploy-only]"
        echo ""
        echo "  full         - Complete cleanup and fresh installation (default)"
        echo "  cleanup-only - Only perform Docker cleanup"
        echo "  build-only   - Only build model cache and application"  
        echo "  deploy-only  - Only deploy services (assumes already built)"
        echo ""
        echo "Environment Variables:"
        echo "  BUILD_ENV=production|development    - Build mode (default: production)"
        echo "  DEPLOYMENT_MODE=standard|high-performance|development - Deployment type"
        echo "  REMOVE_DEV_DEPS=true|false        - Remove dev dependencies (default: true)"
        echo "  EMBEDDING_SCALE=N                  - Number of embedding workers (high-perf mode)"
        echo ""
        echo "Examples:"
        echo "  ./clean_install.sh                 - Production deployment"
        echo "  BUILD_ENV=development ./clean_install.sh - Development mode"
        echo "  DEPLOYMENT_MODE=high-performance ./clean_install.sh - High performance with workers"
        exit 1
        ;;
esac