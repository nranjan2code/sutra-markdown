# 🐳 Sutra-Markdown Docker Architecture

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DOCKER HOST                                    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                     Sutra Network (Bridge)                      │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │                   Load Balancer Layer                      │  │   │
│  │  │                                                            │  │   │
│  │  │  ┌───────────────┐                                        │  │   │
│  │  │  │     Nginx     │  Reverse Proxy & SSL Termination       │  │   │
│  │  │  │   :80, :443   │  Rate Limiting, Load Balancing         │  │   │
│  │  │  └───────┬───────┘                                        │  │   │
│  │  └──────────┼──────────────────────────────────────────────┘  │   │
│  │             │                                                   │   │
│  │  ┌──────────┼──────────────────────────────────────────────┐  │   │
│  │  │          ↓       Application Layer                        │  │   │
│  │  │                                                            │  │   │
│  │  │  ┌────────────────────────────────────────────┐          │  │   │
│  │  │  │         Sutra API Containers                │          │  │   │
│  │  │  │                                              │          │  │   │
│  │  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │          │  │   │
│  │  │  │  │ sutra-api│  │sutra-api2│  │sutra-api3│ │          │  │   │
│  │  │  │  │   :8000  │  │   :8000  │  │   :8000  │ │          │  │   │
│  │  │  │  │          │  │          │  │          │ │          │  │   │
│  │  │  │  │ FastAPI  │  │ FastAPI  │  │ FastAPI  │ │          │  │   │
│  │  │  │  │ Uvicorn  │  │ Uvicorn  │  │ Uvicorn  │ │          │  │   │
│  │  │  │  │ 4 workers│  │ 4 workers│  │ 4 workers│ │          │  │   │
│  │  │  │  └────┬─────┘  └────┬─────┘  └────┬─────┘ │          │  │   │
│  │  │  │       │             │             │        │          │  │   │
│  │  │  │       └─────────────┼─────────────┘        │          │  │   │
│  │  │  └────────────────────┼──────────────────────┘          │  │   │
│  │  └───────────────────────┼─────────────────────────────────┘  │   │
│  │                          │                                      │   │
│  │  ┌───────────────────────┼─────────────────────────────────┐  │   │
│  │  │                       ↓     Data Layer                    │  │   │
│  │  │                                                            │  │   │
│  │  │  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐  │  │   │
│  │  │  │    Redis    │   │    MinIO     │   │  │   │
│  │  │  │   :6379     │   │    :5432     │   │  :9000/9001 │  │  │   │
│  │  │  │             │   │              │   │             │  │  │   │
│  │  │  │  Caching    │   │  Job Track   │   │ S3 Storage  │  │  │   │
│  │  │  │  Sessions   │   │  Metadata    │   │ Documents   │  │  │   │
│  │  │  │  Embeddings │   │  Analytics   │   │ Results     │  │  │   │
│  │  │  │             │   │              │   │             │  │  │   │
│  │  │  └─────┬───────┘   └──────┬───────┘   └──────┬──────┘  │  │   │
│  │  │        │                   │                   │         │  │   │
│  │  │  ┌─────┴───────────────────┴───────────────────┴─────┐  │  │   │
│  │  │  │              Persistent Volumes                    │  │  │   │
│  │  │  │  • redis_data      • minio_data                   │  │  │   │
│  │  │  │  • redis_data     • minio_data   • app_cache                    │  │  │   │
│  │  │  │  • models          • logs                         │  │  │   │
│  │  │  └────────────────────────────────────────────────────┘  │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │                                                                │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │               Monitoring Layer (Optional)               │  │   │
│  │  │                                                          │  │   │
│  │  │  ┌────────────┐    ┌────────────┐                      │  │   │
│  │  │  │ Prometheus │───→│  Grafana   │                      │  │   │
│  │  │  │   :9090    │    │   :3000    │                      │  │   │
│  │  │  │            │    │            │                      │  │   │
│  │  │  │  Metrics   │    │ Dashboards │                      │  │   │
│  │  │  │ Collection │    │   Alerts   │                      │  │   │
│  │  │  └────────────┘    └────────────┘                      │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  Host Ports:                                                         │
│  • 80/443 → Nginx                                                    │
│  • 8000   → API                                                      │
│  • 6379   → Redis                                                    │
│  • 6379   → Redis                                               │
│  • 9000   → MinIO API                                                │
│  • 9001   → MinIO Console                                            │
│  • 9090   → Prometheus                                               │
│  • 3000   → Grafana                                                  │
└───────────────────────────────────────────────────────────────────────┘
```

## Data Flow with Docker

### 1. Document Upload Flow
```
Client
  ↓ HTTP POST /api/v2/convert
Nginx (:80/:443)
  ↓ Proxy + SSL termination
Sutra API Container
  ↓ Check cache
Redis Container
  ↓ Cache miss
Document Parser
  ↓ Extract content
Embedding Service (local in container)
  ↓ Generate embeddings
Smart Router
  ↓ Select tier
Converter (Tier 1/2/3)
  ↓ Generate markdown
Cache Result → Redis
  ↓ (Optional) Store file
MinIO Container
  ↓ Return result
Client
```

### 2. Batch Processing Flow
```
Client uploads 100 PDFs
  ↓
API receives batch request
  ↓
Distributes across 3 API containers (Nginx load balancing)
  │
  ├─→ Container 1: 33 docs
  ├─→ Container 2: 33 docs  } Parallel processing
  └─→ Container 3: 34 docs
  │
  └─→ All check Redis cache first
  │
  └─→ Process uncached docs with local embeddings
  │
  └─→ Store results in Redis + MinIO
  │
  └─→ Track progress in Redis
  ↓
Return aggregated results to client
```

### 3. Caching Strategy
```
┌─────────────────────────────────────┐
│         Cache Hierarchy             │
├─────────────────────────────────────┤
│ L1: In-Memory (per container)       │
│     • Hot documents                 │
│     • 256MB per container           │
│     • LRU eviction                  │
├─────────────────────────────────────┤
│ L2: Redis (shared)                  │
│     • Distributed cache             │
│     • 2GB max memory                │
│     • Semantic fingerprinting       │
│     • 24h TTL default               │
├─────────────────────────────────────┤
│ L3: MinIO (cold storage)            │
│     • Permanent storage             │
│     • Large documents               │
│     • S3-compatible                 │
└─────────────────────────────────────┘
```

## Container Resource Allocation

### Development Profile
```yaml
sutra-api:
  CPU: 2 cores
  Memory: 4GB
  Replicas: 1
  
redis:
  CPU: 0.5 cores
  Memory: 1GB
  
Total: 2.5 cores, 5GB RAM
```

### Production Profile
```yaml
sutra-api:
  CPU: 4 cores (limit: 8)
  Memory: 8GB (limit: 16GB)
  Replicas: 3
  
redis:
  CPU: 1 core
  Memory: 2GB
  
postgres:
  CPU: 2 cores
  Memory: 2GB
  
minio:
  CPU: 1 core
  Memory: 1GB
  
nginx:
  CPU: 1 core
  Memory: 512MB
  
Total: 13 cores, 24.5GB RAM
```

### High-Performance Profile (with GPU)
```yaml
sutra-api:
  CPU: 8 cores
  Memory: 16GB
  GPU: 1x NVIDIA (8GB VRAM)
  Replicas: 5
  
redis:
  CPU: 2 cores
  Memory: 8GB
  
Total: 42 cores, 88GB RAM, 1 GPU
```

## Volume Management

### Persistent Volumes
```
volumes/
├── redis_data/          # Redis persistence
│   └── dump.rdb        # Snapshot file
├── postgres_data/       # PostgreSQL data
│   └── ...             # Database files
├── minio_data/          # Object storage
│   └── buckets/
│       └── sutra-documents/
├── app_cache/           # Application cache
├── app_logs/            # Application logs
└── models/              # Embedding models
    └── nomic-embed-v2/  # Downloaded model
```

### Volume Backup Strategy
```bash
# Backup Redis
docker exec sutra-redis redis-cli SAVE
docker cp sutra-redis:/data/dump.rdb ./backups/redis-$(date +%Y%m%d).rdb

# Backup PostgreSQL
docker exec sutra-postgres pg_dump -U sutra sutra | gzip > ./backups/postgres-$(date +%Y%m%d).sql.gz

# Backup MinIO
docker exec sutra-minio mc mirror /data/buckets ./backups/minio-$(date +%Y%m%d)/
```

## Network Architecture

### Bridge Network
- Name: `sutra-network`
- Driver: `bridge`
- Subnet: Auto-assigned
- DNS: Automatic container discovery

### Container Communication
```
sutra-api → redis:6379       (Cache queries)
sutra-api → postgres:5432    (Job tracking)
sutra-api → minio:9000       (File storage)
nginx → sutra-api:8000       (HTTP proxy)
prometheus → sutra-api:8000  (Metrics scraping)
grafana → prometheus:9090    (Data source)
```

### External Access
```
Host:80 → nginx:80 → sutra-api:8000
Host:443 → nginx:443 → sutra-api:8000
Host:8000 → sutra-api:8000 (direct, dev only)
Host:6379 → redis:6379 (direct, dev only)
Host:9090 → prometheus:9090 (monitoring)
Host:3000 → grafana:3000 (dashboards)
```

## Security Considerations

### Container Isolation
- Non-root user in containers
- Read-only root filesystem (where possible)
- Capability dropping
- Resource limits enforced

### Network Security
- Internal bridge network
- No external access to data services
- SSL/TLS termination at nginx
- API key authentication

### Secrets Management
- Environment variables from .env
- Docker secrets (production)
- Encrypted volumes
- No secrets in images

## Scaling Strategies

### Horizontal Scaling (API)
```bash
# Scale to 5 instances
docker-compose up -d --scale sutra-api=5

# Nginx automatically load balances across all instances
```

### Vertical Scaling
```yaml
# Increase resources per container
deploy:
  resources:
    limits:
      cpus: '8'
      memory: 16G
```

### Database Scaling
```yaml
# Add read replicas
postgres-replica:
  image: postgres:16-alpine
  environment:
    POSTGRES_MASTER_HOST: postgres
    POSTGRES_REPLICATION_MODE: slave
```

### Cache Scaling
```yaml
# Redis Cluster (multi-node)
redis-node-1:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes

redis-node-2:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes

redis-node-3:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes
```

## Deployment Modes Comparison

| Feature | Development | Production | Enterprise |
|---------|------------|------------|-----------|
| Containers | 2 (API+Redis) | 5 (Full stack) | 10+ (Scaled) |
| Replicas | 1 | 1-3 | 5-10 |
| Memory | 5GB | 24GB | 88GB+ |
| SSL | No | Self-signed | Let's Encrypt |
| Monitoring | No | Optional | Required |
| Persistence | Optional | Yes | Yes |
| Backups | Manual | Scheduled | Automated |
| Load Balancer | No | Nginx | Nginx + HAProxy |
| Setup Time | 2 min | 10 min | 30 min |

## Health Checks

### API Health
```bash
# Docker health check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Service Dependencies
```yaml
depends_on:
  redis:
    condition: service_healthy
  postgres:
    condition: service_healthy
```

### Monitoring Health
```bash
# Check all services
docker-compose ps

# Check specific service health
docker inspect --format='{{.State.Health.Status}}' sutra-api
```

## Logging Strategy

### Log Aggregation
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Log Access
```bash
# View logs
docker-compose logs -f sutra-api

# Export logs
docker-compose logs --no-color > logs/export.log

# Search logs
docker-compose logs sutra-api | grep "ERROR"
```

### Structured Logging
- JSON format for parsing
- Correlation IDs for request tracking
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Separate files per service

## Disaster Recovery

### Backup Plan
1. **Daily**: Automated PostgreSQL dumps
2. **Hourly**: Redis snapshots
3. **Real-time**: MinIO replication
4. **Weekly**: Full system snapshot

### Recovery Procedures
```bash
# Restore PostgreSQL
docker exec -i sutra-postgres psql -U sutra sutra < backup.sql

# Restore Redis
docker cp backup.rdb sutra-redis:/data/dump.rdb
docker-compose restart redis

# Restore MinIO
docker exec sutra-minio mc cp --recursive backup/ /data/buckets/
```

---

## Quick Start

```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d

# With monitoring
docker-compose --profile monitoring up -d
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for complete documentation.
