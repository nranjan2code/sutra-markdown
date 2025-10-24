# Sutra-Markdown Project Structure

**Last Updated**: 2025-10-24  
**Version**: V2.2  
**Status**: ✅ Production Ready

## 📂 Root Directory (Clean & Organized)

```
sutra-markdown/
├── README.md                    # 🚀 START HERE - Main documentation
├── ARCHITECTURE.md              # 🏗️ System architecture & design
├── DOCKER_QUICKSTART.md         # 🐳 Quick Docker deployment guide
├── PROJECT_STRUCTURE.md         # 📁 This file - project organization
├── LICENSE                      # 📄 MIT License
│
├── docker-compose.yml           # 🐳 Docker orchestration (production)
├── Dockerfile                   # 🐳 Container definition
├── .env.docker                  # ⚙️ Environment configuration
├── .env.example                 # 📝 Environment template
│
├── pyproject.toml              # 📦 Python project configuration
├── requirements.txt            # 📦 Python dependencies (all)
├── requirements-production.txt # 📦 Production dependencies only
├── requirements-dev.txt        # 📦 Development dependencies
│
├── clean_install.sh            # 🚀 One-command deployment script
├── build_model_cache.sh        # 🧠 AI model downloader
│
├── docs/                       # 📚 Documentation (see below)
├── sutra/                      # 🧠 Core application code
├── tests/                      # 🧪 Test suite
├── scripts/                    # 🔧 Utility scripts
├── nginx/                      # 🌐 Nginx configuration
│
├── models/                     # 🧠 AI models (cached, 2.5GB)
├── cache/                      # 💾 Application cache
├── logs/                       # 📊 Application logs
├── uploads/                    # 📤 File uploads (temporary)
├── outputs/                    # 📥 Conversion outputs
└── samples/                    # 📄 Sample documents
```

---

## 📚 Documentation Structure (`docs/`)

### Main Documentation (User-Facing)
```
docs/
├── README.md                    # 📖 Documentation navigation hub
├── API_DOCUMENTATION.md         # 📡 Complete API reference
├── MIGRATION_GUIDE.md           # 🔄 V2.1 → V2.2 upgrade guide
├── DOCKER_DEPLOYMENT.md         # 🐳 Production deployment guide
├── DOCKER_ARCHITECTURE.md       # 🏗️ Container architecture
├── DEPLOYMENT_OPTIONS.md        # 🚀 Various deployment strategies
├── PRODUCTION_MODEL_CACHE.md    # 🧠 AI model caching guide
└── PYDANTIC_MODELS_REFERENCE.md # 📋 Model schemas reference
```

### Archive (`docs/archive/`)
Historical and legacy documentation for reference:
```
docs/archive/
├── API_VS_SELFHOSTED.md        # API vs self-hosted comparison
├── DEPLOYMENT_SUMMARY.md       # V2.2 deployment summary
├── REFACTORING_PROGRESS.md     # Refactoring history
├── QUICK_START_EMBEDDINGS.md   # Legacy embedding guide
├── SELF_HOSTED_DISCOVERY.md    # Self-hosted setup (legacy)
└── USAGE_TRACKING.md           # Usage tracking documentation
```

### Development (`docs/development/`)
Internal development and phase completion documentation:
```
docs/development/
├── DOCUMENTATION_UPDATE_SUMMARY.md  # Documentation update history
├── PHASE7_COMPLETE.md               # Phase 7 completion notes
└── PRODUCTION_HARDENING_COMPLETE.md # Production hardening checklist
```

---

## 🧠 Application Code (`sutra/`)

```
sutra/
├── __init__.py                 # Package initialization
├── config.py                   # ⚙️ Configuration system (Pydantic)
├── exceptions.py               # ❌ Exception hierarchy
├── logging_config.py           # 📊 Structured logging setup
│
├── api/                        # 🌐 FastAPI application
│   ├── app_v2.py              # ✨ Production API (V2.2)
│   ├── app.py                 # (Legacy, use app_v2.py)
│   ├── dependencies.py        # 💉 Dependency injection
│   ├── security.py            # 🔒 Security middleware
│   └── models.py              # 📋 Request/response models
│
├── intelligence/               # 🧠 AI services
│   ├── embeddings.py          # Nomic embedding service
│   ├── complexity_analyzer.py # Document complexity analysis
│   └── ...
│
├── converters/                 # 🔄 Conversion engines
│   ├── tier1.py               # Rule-based converter (90%)
│   ├── tier2.py               # Spatial-aware converter (5%)
│   ├── tier3.py               # LLM-enhanced converter (5%)
│   ├── content_analyzer.py    # Semantic structure extraction
│   ├── outputs.py             # Multi-format output generation
│   └── ...
│
├── parsers/                    # 📄 Document parsers
│   ├── pdf.py                 # PDF parsing
│   ├── docx.py                # DOCX parsing
│   ├── pptx.py                # PowerPoint parsing
│   └── ...
│
├── router/                     # 🎯 Smart routing logic
│   └── smart_router.py        # AI-powered tier routing
│
├── cache/                      # 💾 Caching system
│   ├── manager.py             # Cache manager
│   ├── embedding_cache.py     # Embedding cache
│   └── ...
│
└── models/                     # 📋 Data models
    ├── document.py            # Document models
    ├── enums.py               # Enumerations
    └── ...
```

---

## 🧪 Testing Structure (`tests/`)

```
tests/
├── test_complete_quality.py   # End-to-end quality tests
├── unit/                      # Unit tests
├── integration/               # Integration tests
├── fixtures/                  # Test fixtures
└── archived/                  # Old tests
```

---

## 🔧 Scripts (`scripts/`)

```
scripts/
├── download_model.py          # Download text embedding models
├── download_vision_model.py   # Download vision models
└── healthcheck.sh             # Docker health check script
```

---

## 🎯 Quick Start Paths

### For Users (Deployment)
```
1. README.md                    # Overview
2. DOCKER_QUICKSTART.md         # One-command deployment
3. docs/API_DOCUMENTATION.md    # API reference
```

### For Developers (Code)
```
1. ARCHITECTURE.md              # System design
2. sutra/api/app_v2.py         # API entry point
3. sutra/converters/            # Conversion logic
4. docs/PYDANTIC_MODELS_REFERENCE.md  # Data models
```

### For DevOps (Infrastructure)
```
1. docker-compose.yml           # Orchestration
2. Dockerfile                   # Container build
3. docs/DOCKER_DEPLOYMENT.md    # Production guide
4. docs/DOCKER_ARCHITECTURE.md  # Architecture details
```

---

## 📏 Organization Principles

### ✅ Root Directory
**Purpose**: Essential files only  
**Contains**: 
- Main documentation (README, ARCHITECTURE, DOCKER_QUICKSTART)
- Docker configuration (docker-compose.yml, Dockerfile)
- Project configuration (pyproject.toml, requirements.txt)
- Deployment scripts (clean_install.sh, build_model_cache.sh)

### ✅ Documentation (`docs/`)
**Structure**:
- **Root**: Current, user-facing documentation
- **archive/**: Historical documentation for reference
- **development/**: Internal development notes

**Principle**: Users see only what they need, developers have full history

### ✅ Application Code (`sutra/`)
**Organization**: By functional responsibility
- `api/` - Web layer
- `intelligence/` - AI services
- `converters/` - Business logic
- `parsers/` - Input processing
- `cache/` - Performance optimization
- `models/` - Data structures

### ✅ Configuration
**Principle**: Single source of truth
- Environment variables (`.env.docker`)
- Pydantic validation (`sutra/config.py`)
- Docker orchestration (`docker-compose.yml`)

---

## 🔗 Cross-References

### Documentation Links
All documentation uses **relative paths**:
- Root → docs: `docs/FILE.md`
- docs → Root: `../FILE.md`
- docs → docs: `./FILE.md`

### Code Imports
All code uses **absolute imports**:
```python
from sutra.api.dependencies import EmbeddingServiceDep
from sutra.config import Settings
from sutra.exceptions import ConversionError
```

---

## 📝 Naming Conventions

### Files
- Markdown: `UPPERCASE_SNAKE_CASE.md` (e.g., `README.md`, `MIGRATION_GUIDE.md`)
- Python: `lowercase_snake_case.py` (e.g., `app_v2.py`, `dependencies.py`)
- Scripts: `lowercase_snake_case.sh` (e.g., `clean_install.sh`)

### Directories
- Documentation: `lowercase` (e.g., `docs`, `archive`, `development`)
- Code: `lowercase` (e.g., `sutra`, `tests`, `scripts`)

### Versions
- Code: `v2`, `v2.2` in filenames (e.g., `app_v2.py`)
- Docs: `V2.2` in titles and headers

---

## 🚀 Deployment Files

### Essential for Production
```
✅ docker-compose.yml          # Orchestration
✅ Dockerfile                  # Container definition
✅ .env.docker                 # Configuration
✅ clean_install.sh            # Deployment script
✅ build_model_cache.sh        # Model downloader
✅ requirements-production.txt # Dependencies
```

### Development Only
```
requirements-dev.txt           # Dev dependencies
.env.example                   # Config template
web-ui/                        # (Optional) Web interface
```

---

## 🎓 Best Practices Implemented

1. ✅ **Clean Root**: Only essential files in root directory
2. ✅ **Organized Docs**: User-facing vs historical vs development
3. ✅ **Clear Navigation**: README.md in every directory
4. ✅ **Relative Links**: All documentation uses relative paths
5. ✅ **Single Source**: Configuration in one place
6. ✅ **Separation**: Code, docs, tests, scripts in separate dirs
7. ✅ **Versioning**: Clear version markers (V2.2, app_v2.py)
8. ✅ **Consistency**: Naming conventions throughout

---

## 📊 Metrics

### Documentation
- **Main Docs**: 8 files (user-facing)
- **Archive**: 6 files (historical)
- **Development**: 3 files (internal)
- **Total**: 17 documentation files

### Code
- **Python Files**: 50+ modules
- **Lines of Code**: ~15,000 lines
- **Test Coverage**: 80%+ target

### Size
- **Repository**: ~50 MB (without models)
- **AI Models**: ~2.5 GB (cached locally)
- **Docker Images**: ~2 GB (production build)

---

## ✅ Organization Checklist

- [x] Root directory cleaned (only essential files)
- [x] Documentation organized (main/archive/development)
- [x] All links updated and verified
- [x] Navigation README added to docs/
- [x] Project structure documented
- [x] Naming conventions consistent
- [x] Cross-references working
- [x] Deployment path clear
- [x] Development path clear
- [x] Best practices documented

---

## 🆘 Finding What You Need

### "Where is the...?"

| What | Where |
|------|-------|
| Quick start guide | `README.md` |
| Deployment instructions | `DOCKER_QUICKSTART.md` |
| System architecture | `ARCHITECTURE.md` |
| API documentation | `docs/API_DOCUMENTATION.md` |
| Migration guide | `docs/MIGRATION_GUIDE.md` |
| Production setup | `docs/DOCKER_DEPLOYMENT.md` |
| Code entry point | `sutra/api/app_v2.py` |
| Configuration | `sutra/config.py`, `.env.docker` |
| Historical docs | `docs/archive/` |
| Development notes | `docs/development/` |

---

## 🎉 Summary

Sutra-Markdown V2.2 now has a **clean, organized structure** with:

- ✅ **Clean root directory** - Only essential files
- ✅ **Organized documentation** - Easy navigation
- ✅ **Updated links** - All references working
- ✅ **Clear structure** - Logical organization
- ✅ **Production ready** - One-command deployment

**To deploy**: Just run `./clean_install.sh` - everything else is handled! 🚀

---

**Maintained By**: Sutra-Markdown Team  
**License**: MIT  
**Version**: V2.2  
**Status**: ✅ Production Ready
