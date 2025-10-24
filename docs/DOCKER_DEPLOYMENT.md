# 🐳 Docker Deployment Guide for Sutra-Markdown V2

Complete guide to deploying Sutra-Markdown locally using Docker with proper architecture.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture Overview](#-architecture-overview)
- [Deployment Options](#-deployment-options)
- [Configuration](#-configuration)
- [Production Deployment](#-production-deployment)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

# Optional (for GPU acceleration)
- NVIDIA Docker runtime (for GPU support)
- NVIDIA GPU with 8GB+ VRAM
```

### 1. Development Mode (Fastest Setup)

Perfect for testing and development:

```bash
# Clone repository
git clone https://github.com/nranjan2code/sutra-markdown.git
cd sutra-markdown

# Start services
docker-compose -f docker-compose.dev.yml up -d

# Check logs
docker-compose -f docker-compose.dev.yml logs -f sutra-dev

# Access API
curl http://localhost:8000/health
```

**What you get:**
- ✅ Sutra API with hot-reload (port 8000)
- ✅ Redis for caching (port 6379)
- ✅ Local embeddings (FREE)
- ✅ Volume mounts for live code changes

### 2. Production Mode (Full Stack)

Complete production setup with all services:

```bash
# Copy environment file
cp .env.docker.example .env.docker

# Edit configuration (set API keys, passwords, etc.)
nano .env.docker

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**What you get:**
- ✅ Sutra API (port 8000)
- ✅ Redis (port 6379)
- ✅ MinIO (port 9000)
- ✅ MinIO S3 storage (ports 9000, 9001)
- ✅ All monitoring tools (optional)

### 3. Production with Monitoring

```bash
# Start with monitoring stack
docker-compose --profile monitoring up -d

# Access services
# - API: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
# - MinIO Console: http://localhost:9001
```

---

## 🏗️ Architecture Overview

### Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Host                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    Sutra Network                      │ │
│  │                                                        │ │
│  │  ┌──────────────┐      ┌──────────────┐             │ │
│  │  │   Nginx      │──────│  Sutra API   │             │ │
│  │  │  (Reverse    │      │  (FastAPI)   │             │ │
│  │  │   Proxy)     │      │              │             │ │
│  │  └──────────────┘      └───────┬──────┘             │ │
│  │       :80,:443                  │                     │ │
│  │                                 │                     │ │
│  │           ┌─────────────────────┼──────────────┐     │ │
│  │           │                     │              │     │ │
│  │           ↓                     ↓              ↓     │ │
│  │  ┌──────────────┐      ┌──────────────┐  ┌────────┐│ │
│  │  │    Redis     │      │    MinIO     │  │ │
│  │  │   (Cache)    │      │   (Jobs DB)  │  │ (S3)   ││ │
│  │  └──────────────┘      └──────────────┘  └────────┘│ │
│  │       :6379                  :5432          :9000   │ │
│  │                                                      │ │
│  │  ┌──────────────┐      ┌──────────────┐            │ │
│  │  │  Prometheus  │      │   Grafana    │            │ │
│  │  │  (Metrics)   │──────│  (Dashboards)│            │ │
│  │  └──────────────┘      └──────────────┘            │ │
│  │       :9090                  :3000                  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  Volumes:                                                   │
│  • redis_data      • minio_data                            │
│  • redis_data     • minio_data   • prometheus_data                       │
│  • grafana_data    • app_cache                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ 1. Upload document
     ↓
┌────────────────┐
│   Nginx/API    │
└────┬───────────┘
     │ 2. Parse & analyze
     ↓
┌────────────────┐     ┌─────────────┐
│  Sutra API     │────→│   Redis     │ Check cache
│  (Processing)  │←────│   (Cache)   │
└────┬───────────┘     └─────────────┘
     │ 3. No cache hit
     ↓
┌────────────────┐
│  Embeddings    │ Generate embeddings (local/API)
│   Analysis     │
└────┬───────────┘
     │ 4. Route to tier
     ↓
┌────────────────┐
│  Converter     │ Tier 1/2/3
│   (Markdown)   │
└────┬───────────┘
     │ 5. Store result
     ↓
┌────────────────┐     ┌─────────────┐
│     Redis      │←────│   MinIO     │ Optional: store files
│   (Cache)      │     │   (S3)      │
└────┬───────────┘     └─────────────┘
     │ 6. Return markdown
     ↓
┌──────────┐
│  Client  │
└──────────┘
```

---

## 🎛️ Deployment Options

### Option 1: Minimal (Development)

**Use Case:** Local testing, development

```yaml
Services: Sutra API + Redis
Memory: 2GB
CPU: 2 cores
Setup Time: 2 minutes
```

```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Pros:**
- ✅ Fast startup
- ✅ Hot reload for code changes
- ✅ Minimal resource usage

**Cons:**
- ❌ No persistence
- ❌ No monitoring
- ❌ Single worker

---

### Option 2: Standard (Production-Ready)

**Use Case:** Production deployment, small-medium scale

```yaml
Services: API + Redis + MinIO
Memory: 6GB
CPU: 4 cores
Setup Time: 5 minutes
```

```bash
docker-compose up -d
```

**Pros:**
- ✅ Full persistence
- ✅ Distributed caching
- ✅ File storage
- ✅ Job tracking

**Cons:**
- ❌ No monitoring (optional)
- ❌ Single API instance

---

### Option 3: Full Stack (Enterprise)

**Use Case:** High-volume production

```yaml
Services: API + Redis + MinIO + Nginx
Memory: 8GB
CPU: 6 cores
Setup Time: 8 minutes
```

```bash
docker-compose --profile monitoring --profile production up -d
```

**Pros:**
- ✅ Complete monitoring
- ✅ Load balancing
- ✅ Metrics & dashboards
- ✅ SSL/TLS support

**Cons:**
- ❌ Higher resource usage
- ❌ More complex setup

---

### Option 4: GPU-Accelerated

**Use Case:** Maximum performance with local embeddings

**Requirements:**
- NVIDIA GPU (8GB+ VRAM)
- NVIDIA Docker runtime

```yaml
# Add to docker-compose.yml under sutra-api service
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

```bash
# Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Start with GPU support
docker-compose up -d
```

**Performance:**
- 🚀 8-25ms per embedding (vs 80-150ms CPU)
- 🚀 125+ docs/second throughput
- 🚀 Perfect for batch processing

---

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env.docker`:

```bash
# High-Performance Local Embedding Mode
EMBEDDING_MODE=local          # Always local for optimal performance

# High-Performance Settings
EMBEDDING_WORKERS=4           # Embedding worker processes
EMBEDDING_BATCH_SIZE=64       # Dynamic batching (1-128)
EMBEDDING_GPU_MEMORY_FRACTION=0.9  # Use 90% GPU memory
EMBEDDING_CACHE_ENABLED=true # Enable embedding caching

# Performance Targets
EMBEDDING_PERFORMANCE_TARGET_RPS=10000  # 10K+ req/sec
EMBEDDING_PERFORMANCE_TARGET_P95_MS=100 # p95 < 100ms

# Processing
MAX_WORKERS=10                # Concurrent workers
BATCH_SIZE=100                # Batch processing size
MAX_FILE_SIZE_MB=500          # Max upload size

# Thresholds
TIER_1_THRESHOLD=0.6          # Route to Tier 2 if > 0.6
TIER_2_THRESHOLD=0.8          # Route to Tier 3 if > 0.8

# Caching
CACHE_ENABLED=true
CACHE_TTL=86400               # 24 hours

# Security
SECRET_KEY=change_me          # JWT secret
API_KEY_REQUIRED=false        # Require API key
```

### Custom Configuration Files

Create `config/production.yml`:

```yaml
app:
  name: "Sutra-Markdown"
  version: "2.0.0"
  environment: "production"

embedding:
  mode: "local"  # or "api"
  model_path: "/app/models/nomic-embed-v2"
  device: "cuda"  # or "cpu"
  batch_size: 32

conversion:
  tiers:
    tier1:
      enabled: true
      threshold: 0.6
    tier2:
      enabled: true
      threshold: 0.8
    tier3:
      enabled: true
      llm_provider: "openai"  # or "anthropic", "google"

cache:
  enabled: true
  backend: "redis"
  ttl: 86400
  max_size_gb: 10

storage:
  backend: "minio"  # or "s3", "local"
  bucket: "sutra-documents"

monitoring:
  enabled: true
  metrics_port: 9090
  log_level: "INFO"
```

---

## 🚀 Production Deployment

### Step 1: Prepare Environment

```bash
# Create project directory
mkdir -p /opt/sutra-markdown
cd /opt/sutra-markdown

# Clone repository
git clone https://github.com/nranjan2code/sutra-markdown.git .

# Set up environment
cp .env.docker.example .env.docker
nano .env.docker  # Edit configuration
```

### Step 2: Configure Services

```bash
# Set production passwords
export MINIO_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export SECRET_KEY=$(openssl rand -base64 64)

# Update .env.docker
sed -i "s/minioadmin123/$MINIO_PASSWORD/" .env.docker
sed -i "s/change_me/$SECRET_KEY/" .env.docker
```

### Step 3: Download Models (for local embeddings)

```bash
# Run model download script
docker-compose run --rm sutra-api python scripts/download_model.py

# Or manually download and mount
mkdir -p models
# Place model files in ./models/
```

### Step 4: Initialize Database

```bash
# Start Redis
docker-compose up -d redis

# Wait for it to be ready
sleep 5

# Wait for it to be ready
sleep 10

# Run migrations
docker-compose run --rm sutra-api alembic upgrade head
```

### Step 5: Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f sutra-api
```

### Step 6: Configure Nginx (Optional)

```bash
# Create SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt

# Create nginx config
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream sutra_backend {
        least_conn;
        server sutra-api:8000;
        # Add more instances for load balancing:
        # server sutra-api-2:8000;
        # server sutra-api-3:8000;
    }

    server {
        listen 80;
        server_name localhost;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate /etc/nginx/ssl/selfsigned.crt;
        ssl_certificate_key /etc/nginx/ssl/selfsigned.key;

        client_max_body_size 500M;

        location / {
            proxy_pass http://sutra_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts for large files
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }
    }
}
EOF

# Start nginx
docker-compose --profile production up -d nginx
```

### Step 7: Set Up Monitoring

```bash
# Create Prometheus config
mkdir -p monitoring
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'sutra-api'
    static_configs:
      - targets: ['sutra-api:8000']
    metrics_path: '/metrics'
EOF

# Start monitoring stack
docker-compose --profile monitoring up -d
```

### Step 8: Test Deployment

```bash
# Health check
curl http://localhost:8000/health

# Convert a test document
curl -X POST http://localhost:8000/api/v2/convert \
  -F "file=@test.pdf" \
  -H "Content-Type: multipart/form-data"

# Check metrics
curl http://localhost:8000/metrics
```

---

## 🔧 Management Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart sutra-api

# View logs
docker-compose logs -f sutra-api

# Scale API instances
docker-compose up -d --scale sutra-api=3

# Update services
docker-compose pull
docker-compose up -d
```

### Maintenance

```bash
# Backup Redis data
docker exec sutra-redis redis-cli BGSAVE

# Backup Redis
docker exec sutra-redis redis-cli SAVE
docker cp sutra-redis:/data/dump.rdb redis-backup.rdb

# Clean up old data
docker exec sutra-redis redis-cli FLUSHDB

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Debugging

```bash
# Access container shell
docker exec -it sutra-api /bin/bash

# Check environment
docker exec sutra-api env

# Test connections
docker exec sutra-api curl redis:6379
docker exec sutra-api curl redis:6379

# View real-time logs
docker-compose logs -f --tail=100

# Check resource usage
docker stats
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Container Won't Start**

```bash
# Check logs
docker-compose logs sutra-api

# Common causes:
# - Missing environment variables
# - Port conflicts
# - Insufficient resources

# Fix port conflict
docker-compose down
lsof -i :8000  # Find process using port
kill -9 <PID>
docker-compose up -d
```

#### 2. **Out of Memory**

```bash
# Check memory usage
docker stats

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 16G

# Or adjust application settings
MAX_WORKERS=5  # Reduce concurrent workers
```

#### 3. **Slow Performance**

```bash
# Check if using CPU or GPU
docker exec sutra-api python -c "import torch; print(torch.cuda.is_available())"

# Enable GPU support
# See "Option 4: GPU-Accelerated" section

# Increase cache size
CACHE_TTL=604800  # 7 days

# Use multiple workers
docker-compose up -d --scale sutra-api=3
```

#### 4. **Model Download Fails**

```bash
# Manual download
docker exec -it sutra-api bash
python scripts/download_model.py --output /app/models/nomic-embed-v2

# Or mount pre-downloaded model
mkdir -p models
# Copy model files to ./models/
docker-compose up -d
```

#### 5. **Redis Connection Failed**

```bash
# Check Redis status
docker-compose ps redis

# Test connection
docker exec sutra-api redis-cli -h redis ping

# Restart Redis
docker-compose restart redis
```

---

## 📊 Performance Tuning

### For High Volume

```yaml
# docker-compose.override.yml
services:
  sutra-api:
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '8'
          memory: 16G
    environment:
      MAX_WORKERS: 20
      BATCH_SIZE: 200
      
  redis:
    command: redis-server --maxmemory 8gb --maxmemory-policy allkeys-lru
```

### For Low Latency

```yaml
services:
  sutra-api:
    environment:
      EMBEDDING_MODE: local  # Avoid network calls
      CACHE_ENABLED: true
      TIER_1_THRESHOLD: 0.7  # Prefer fast tier 1
```

### For Cost Optimization

```yaml
services:
  sutra-api:
    environment:
      EMBEDDING_MODE: local  # Free embeddings
      TIER_1_THRESHOLD: 0.5  # Aggressive tier 1
      TIER_2_THRESHOLD: 0.9  # Avoid LLM tier
      LLM_PROVIDER: ollama   # Use local LLM
```

---

## 🎯 Best Practices

1. **Always use volumes** for persistent data
2. **Set resource limits** to prevent OOM
3. **Use health checks** for reliability
4. **Monitor metrics** in production
5. **Regular backups** of databases
6. **SSL/TLS** for production
7. **API authentication** enabled
8. **Rate limiting** configured
9. **Log rotation** enabled
10. **Regular updates** for security

---

## 📚 Additional Resources

- [Architecture Documentation](../ARCHITECTURE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Deployment Options](./DEPLOYMENT_OPTIONS.md)
- [Migration Guide](./MIGRATION_GUIDE.md)
- [Docker Quick Start](../DOCKER_QUICKSTART.md)

---

## 💡 Quick Reference

```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d

# With monitoring
docker-compose --profile monitoring up -d

# Scale API
docker-compose up -d --scale sutra-api=3

# Logs
docker-compose logs -f sutra-api

# Stop
docker-compose down

# Clean up
docker-compose down -v
docker system prune -a
```

---

**Ready to deploy! 🚀**

For questions or issues, please open a GitHub issue or contact support.
