# Sutra-Markdown Documentation

Welcome to the comprehensive documentation for Sutra-Markdown V2.2!

## 📚 Quick Navigation

### Getting Started
- **[Main README](../README.md)** - Start here! Quick start guide and features overview
- **[Docker Quick Start](../DOCKER_QUICKSTART.md)** - One-command deployment guide
- **[Migration Guide](MIGRATION_GUIDE.md)** - Upgrading from V2.1 to V2.2

### Technical Documentation
- **[Architecture](../ARCHITECTURE.md)** - Complete system architecture and design
- **[API Documentation](API_DOCUMENTATION.md)** - Full API reference
- **[Docker Deployment](DOCKER_DEPLOYMENT.md)** - Production deployment guide
- **[Docker Architecture](DOCKER_ARCHITECTURE.md)** - Container architecture details

### Reference Material
- **[Pydantic Models Reference](PYDANTIC_MODELS_REFERENCE.md)** - Complete model documentation
- **[Deployment Options](DEPLOYMENT_OPTIONS.md)** - Various deployment strategies
- **[Production Model Cache](PRODUCTION_MODEL_CACHE.md)** - AI model caching guide

---

## 📁 Documentation Structure

```
docs/
├── README.md                         # This file - navigation hub
├── API_DOCUMENTATION.md              # Complete API reference
├── DEPLOYMENT_OPTIONS.md             # Deployment strategies
├── DOCKER_ARCHITECTURE.md            # Container architecture
├── DOCKER_DEPLOYMENT.md              # Production deployment
├── MIGRATION_GUIDE.md                # V2.1 → V2.2 upgrade guide
├── PRODUCTION_MODEL_CACHE.md         # Model caching guide
├── PYDANTIC_MODELS_REFERENCE.md      # Model schemas reference
│
├── archive/                          # Historical documentation
│   ├── API_VS_SELFHOSTED.md         # API vs self-hosted comparison
│   ├── DEPLOYMENT_SUMMARY.md        # V2.2 deployment summary
│   ├── QUICK_START_EMBEDDINGS.md    # Legacy embedding guide
│   ├── REFACTORING_PROGRESS.md      # Refactoring history
│   ├── SELF_HOSTED_DISCOVERY.md     # Self-hosted setup (legacy)
│   └── USAGE_TRACKING.md            # Usage tracking documentation
│
└── development/                      # Development phase docs
    ├── DOCUMENTATION_UPDATE_SUMMARY.md  # Doc update history
    ├── PHASE7_COMPLETE.md               # Phase 7 completion
    └── PRODUCTION_HARDENING_COMPLETE.md # Hardening checklist
```

---

## 🎯 Documentation by Use Case

### I want to deploy Sutra-Markdown
1. Start with **[Main README](../README.md)** for overview
2. Follow **[Docker Quick Start](../DOCKER_QUICKSTART.md)** for one-command deployment
3. Reference **[Docker Deployment](DOCKER_DEPLOYMENT.md)** for production setup

### I want to understand the architecture
1. Read **[Architecture](../ARCHITECTURE.md)** for system design
2. Review **[Docker Architecture](DOCKER_ARCHITECTURE.md)** for container details
3. Check **[Pydantic Models Reference](PYDANTIC_MODELS_REFERENCE.md)** for data structures

### I want to use the API
1. Reference **[API Documentation](API_DOCUMENTATION.md)** for endpoints
2. See **[Main README](../README.md)** for quick examples
3. Check **[Migration Guide](MIGRATION_GUIDE.md)** for V2.2 changes

### I want to upgrade from V2.1
1. **[Migration Guide](MIGRATION_GUIDE.md)** - Complete upgrade instructions
2. **[Architecture](../ARCHITECTURE.md)** - Understand new V2.2 features
3. **[Docker Quick Start](../DOCKER_QUICKSTART.md)** - Redeploy with new version

### I'm developing/contributing
1. Read **[Architecture](../ARCHITECTURE.md)** for system design
2. Check **[Pydantic Models Reference](PYDANTIC_MODELS_REFERENCE.md)** for models
3. Review **development/** folder for historical context

---

## 🆕 What's New in V2.2

### Production-Grade Features
- ✅ **Security**: OWASP-compliant middleware stack
- ✅ **Observability**: Structured JSON logging with request tracking
- ✅ **Type Safety**: 100% type-annotated, zero runtime errors
- ✅ **Dependency Injection**: No global state, fully testable
- ✅ **Performance**: Optimized middleware and async operations

See **[Migration Guide](MIGRATION_GUIDE.md)** for complete details.

---

## 📖 Reading Path by Role

### System Administrator
```
1. Main README (overview)
2. Docker Quick Start (deployment)
3. Docker Deployment (production setup)
4. Production Model Cache (optimization)
```

### API Developer
```
1. API Documentation (endpoints)
2. Pydantic Models Reference (schemas)
3. Migration Guide (V2.2 changes)
4. Architecture (system design)
```

### DevOps Engineer
```
1. Docker Architecture (containers)
2. Docker Deployment (production)
3. Deployment Options (strategies)
4. Production Model Cache (performance)
```

### Contributor/Developer
```
1. Architecture (system design)
2. Pydantic Models Reference (code structure)
3. development/ folder (history)
4. Migration Guide (patterns)
```

---

## 🔗 External Resources

- **GitHub Repository**: [sutra-markdown](https://github.com/nranjan2code/sutra-markdown)
- **Issue Tracker**: [GitHub Issues](https://github.com/nranjan2code/sutra-markdown/issues)
- **License**: [MIT License](../LICENSE)

---

## 📝 Contributing to Documentation

Found an error or want to improve the docs?

1. Create an issue describing the problem
2. Submit a pull request with fixes
3. Follow existing documentation style
4. Update this README if adding new docs

---

## ❓ Need Help?

- Check **[FAQ in Migration Guide](MIGRATION_GUIDE.md#faq)**
- Review **[Troubleshooting in Docker Quick Start](../DOCKER_QUICKSTART.md#troubleshooting)**
- Search the **archive/** folder for historical context
- Open an issue on GitHub

---

**Last Updated**: 2025-10-24  
**Version**: V2.2  
**Status**: ✅ Production Ready
