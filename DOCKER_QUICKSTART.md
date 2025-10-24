# Sutra-Markdown Docker Deployment Guide

## 🚀 Single Command Production Deployment

### Quick Start (Recommended)

```bash
# One command to rule them all
./clean_install.sh
```

This script automatically:
1. ✅ Stops and removes existing containers
2. ✅ Downloads AI models (~2.5GB) if needed
3. ✅ Builds production-optimized Docker images
4. ✅ Starts complete stack (API + Redis)
5. ✅ Validates all services are healthy
6. ✅ Shows you the API documentation URL

**Time:** ~5 minutes first run, ~30 seconds subsequent runs

### What Gets Deployed

```
┌─────────────────────────────────────────┐
│   Production Stack (V2.2)               │
├─────────────────────────────────────────┤
│ 🌐 Sutra API (app_v2.py)                │
│    Port: 8000                           │
│    Features:                            │
│    • Security middleware stack          │
│    • Dependency injection               │
│    • Structured JSON logging            │
│    • Rate limiting (60/min)             │
│    • Request tracking (SHA256)          │
├─────────────────────────────────────────┤
│ 💾 Redis Cache                          │
│    Port: 6379                           │
│    Memory: 2GB LRU cache                │
├─────────────────────────────────────────┤
│ 🧠 AI Models (Local)                    │
│    Nomic Embed Text V2 (768d)           │
│    Nomic Embed Vision V1.5              │
│    Storage: 2.5GB                       │
└─────────────────────────────────────────┘
```

## 🔧 Manual Deployment (Optional)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 10GB+ free disk space

### Step-by-Step

```bash
# 1. Clone repository
git clone https://github.com/yourusername/sutra-markdown.git
cd sutra-markdown

# 2. Download AI models (one-time)
./build_model_cache.sh

# 3. Build and start services
docker compose up -d --build

# 4. Check status
docker compose ps

# 5. View logs
docker compose logs -f sutra-api

# 6. Test API
curl http://localhost:8000/health
```

## 📊 Service Management

### Check Status
```bash
docker compose ps
```

Expected output:
```
NAME         IMAGE              STATUS    PORTS
sutra-api    sutra-markdown:v2  healthy   0.0.0.0:8000->8000/tcp
redis        redis:7-alpine     healthy   0.0.0.0:6379->6379/tcp
```

### View Logs

```bash
# All services
docker compose logs -f

# API only (structured JSON)
docker compose logs -f sutra-api

# Pretty-print JSON logs
docker compose logs -f sutra-api | jq '.'

# Last 100 lines
docker compose logs --tail=100 sutra-api
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart API only
docker compose restart sutra-api

# Rebuild and restart
docker compose up -d --build sutra-api
```

### Stop Services

```bash
# Stop all (keeps data)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove EVERYTHING (including volumes)
docker compose down -v
```

## 📈 Scaling for Production

### Horizontal Scaling

```bash
# Scale API to 3 instances
docker compose up -d --scale sutra-api=3

# Verify
docker compose ps
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  sutra-api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

## 🔧 Configuration

### Environment Variables

All configuration via `.env.docker` (auto-generated):

```bash
# Application
SUTRA_ENVIRONMENT=production
SUTRA_LOG_LEVEL=INFO
SUTRA_LOG_FORMAT=json  # Use 'text' for development

# Security
SUTRA_RATE_LIMIT_PER_MINUTE=60
SUTRA_MAX_FILE_SIZE_MB=500
SUTRA_ENABLE_AUTH=false  # Set to 'true' for JWT auth
SUTRA_CORS_ORIGINS=*     # Comma-separated origins

# Performance
MAX_WORKERS=10
BATCH_SIZE=100
EMBEDDING_WORKERS=4

# AI Features
EMBEDDING_MODE=local  # Always local
TIER_1_THRESHOLD=0.6
TIER_2_THRESHOLD=0.8
ENABLE_INTELLIGENCE=true

# Cache
CACHE_ENABLED=true
CACHE_TTL=86400  # 24 hours
REDIS_HOST=redis
REDIS_PORT=6379

# Optional: LLM APIs (Tier 3 only)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

### Apply Configuration Changes

```bash
# Edit .env.docker
nano .env.docker

# Restart services
docker compose restart sutra-api
```

## 🧪 Testing Your Deployment

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.2.0",
  "environment": "production",
  "details": {
    "embeddings": {
      "available": true,
      "mode": "local",
      "device": "cuda:0"
    },
    "cache": {
      "enabled": true,
      "stats": {
        "hits": 42,
        "misses": 158,
        "hit_rate": 0.21
      }
    }
  }
}
```

### Convert Document

```bash
# Simple conversion
curl -X POST http://localhost:8000/convert \
  -F "file=@sample.pdf"

# AI-powered with multiple formats
curl -X POST http://localhost:8000/convert \
  -F "file=@sample.pdf" \
  -F "enable_intelligence=true" \
  -F "output_formats=markdown,json,html"

# Check system stats
curl http://localhost:8000/stats
```

### API Documentation

Open in browser: http://localhost:8000/docs

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
# ports:
#   - "8080:8000"  # Use 8080 instead
```

### Out of Memory

```bash
# Check Docker memory
docker stats

# Increase Docker memory limit in Docker Desktop:
# Settings → Resources → Memory → 8GB+

# Or reduce workers
# Edit .env.docker:
MAX_WORKERS=5
EMBEDDING_WORKERS=2
```

### Models Not Found

```bash
# Re-download models
./build_model_cache.sh

# Verify model cache volume
docker volume ls | grep model_cache

# Check models are mounted
docker exec sutra-api ls -lh /app/models
```

### Redis Connection Failed

```bash
# Check Redis is running
docker compose ps redis

# Check Redis logs
docker compose logs redis

# Restart Redis
docker compose restart redis
```

### API Won't Start

```bash
# View detailed logs
docker compose logs sutra-api

# Check for port conflicts
lsof -i :8000

# Rebuild from scratch
docker compose down -v
./clean_install.sh
```

## 📊 Monitoring

### Resource Usage

```bash
# Real-time stats
docker stats

# Container-specific
docker stats sutra-api
```

### Log Aggregation

For production, forward logs to ELK/Splunk:

```yaml
# docker-compose.yml
services:
  sutra-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Or use Filebeat/Fluentd to ship to your log aggregator.

## 🚀 Production Best Practices

### 1. Use Production Log Format
```bash
SUTRA_LOG_FORMAT=json  # Never 'text' in production
```

### 2. Enable Authentication
```bash
SUTRA_ENABLE_AUTH=true
# Configure JWT_SECRET_KEY
```

### 3. Restrict CORS
```bash
SUTRA_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 4. Set Rate Limits
```bash
SUTRA_RATE_LIMIT_PER_MINUTE=60  # Adjust based on load
```

### 5. Monitor Health
```bash
# Setup monitoring tool to check:
curl http://localhost:8000/health

# Alert if status != "healthy"
```

### 6. Backup Redis Data
```bash
# Redis persistence is enabled by default
# Volume: redis_data

# Backup
docker run --rm -v sutra-markdown_redis_data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/redis-backup.tar.gz /data

# Restore
docker run --rm -v sutra-markdown_redis_data:/data \
  -v $(pwd):/backup alpine \
  sh -c "cd / && tar xzf /backup/redis-backup.tar.gz"
```

## 🔐 Security Checklist

- [ ] Change default Redis password (if exposed)
- [ ] Enable JWT authentication (`SUTRA_ENABLE_AUTH=true`)
- [ ] Restrict CORS origins
- [ ] Use HTTPS in production (nginx/traefik)
- [ ] Set rate limits appropriate for your use case
- [ ] Regularly update Docker images
- [ ] Monitor logs for suspicious activity
- [ ] Keep API keys in secure secrets management

## 📚 Next Steps

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete endpoint reference
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Upgrading from V2.1
- **[Architecture](ARCHITECTURE.md)** - System design details

---

**Need help?** Check logs with `docker compose logs -f` or run `./clean_install.sh` to reset everything.