# Changelog

All notable changes to the Logos project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-01-03

### 🛠️ Service Management & Deployment Fixes

- **Redesigned manage.sh**: Clean interface with logical hotkeys (s=start, v=logs, h=health, etc.)
- **Fixed Qdrant health checks**: Resolved "starting" status issues in Portainer
- **Improved Docker configs**: Better health checks, dependencies, and resource limits
- **Portainer compatibility**: Fixed YAML parsing and service orchestration issues


## [1.2.2] - 2025-12-31

### 🤖 Model Reliability Fix

- **Changed default embedding model** from BAAI to sentence-transformers for better Docker compatibility
- **95% faster loading** (0.2s vs 30-60s)
- **More reliable downloads** in constrained network environments

---

## [1.2.1] - 2025-12-31

### 🐳 Cache Directory Fix

- **Fixed permission denied errors** in Docker cache directories
- **Moved cache location** from `/tmp` to `/app/cache` for better persistence
- **Improved volume mounting** and directory permissions

#### Technical Details

**Docker Changes:**
```dockerfile
# Before
ENV FASTEMBED_CACHE_DIR=/tmp/fastembed_cache

# After  
ENV FASTEMBED_CACHE_DIR=/app/cache/fastembed
RUN mkdir -p /app/cache/fastembed && chown -R logos:logos /app/cache
```

**Volume Mount Changes:**
```yaml
# Before
- logos_model_cache:/tmp/fastembed_cache:z

# After
- logos_model_cache:/app/cache:z
```

This fix resolves the model download failures and cache permission issues that were preventing optimal performance in Docker deployments.

---

## [1.2.0] - 2025-12-31

### 🌐 Community & Performance Release

- **Added community files**: Code of Conduct, Contributing guidelines, Security policy, GitHub templates
- **Enhanced Docker deployment**: Model caching, HuggingFace integration, Portainer compatibility
- **Performance improvements**: Better cache management and model loading
- **Security enhancements**: Vulnerability reporting and security documentation

## [1.1.1] - 2025-12-31

### 🏗️ Infrastructure Enhancement

- **Restructured project layout**: Organized into `cli/`, `deploy/`, `config/`, `docs/` directories
- **Added Kubernetes support**: Helm charts and Kustomize configurations
- **Enhanced manage.sh**: Service management script with interactive menus
- **Dependency management**: Separated runtime and dev dependencies

---

## [1.1.0] - 2025-12-31

### 🎯 Quality Enhancement

- **Added version management**: VERSION file and `get_version` MCP tool (16 tools total)
- **Integrated Semgrep**: 25+ custom rules for code quality and security
- **Enhanced type safety**: Improved type hints and function signatures
- **KISS principle enforcement**: Automated complexity and style checks

---

## [1.0.0] - 2025-12-31

### 🎉 Initial Production Release

- **Complete MCP server**: 15 tools for memory and document management
- **Dual memory architecture**: Personality and project knowledge collections
- **Sophia methodology**: "Letters for Future Self" autobiographical memory
- **Multi-format support**: PDF, DOCX, HTML, TXT, MD processing
- **Docker deployment**: Production-ready with Portainer/K8s compatibility
- **Comprehensive testing**: 211+ unit tests with 80% coverage

---

## [0.1.0] - 2025-12-31

### Added

- **Project Genesis**: Established core identity as open-source alternative to proprietary digital personalities
- **Manifesto**: Formalized the "Logos Manifesto" defining philosophical guidelines (Reason, Grounded Truth, Transparency)
- **Infrastructure**: Initial docker-compose.yml for Portainer deployment with Qdrant vector database
- **Documentation**: Basic README.md with project vision and technical stack
- **License**: MIT License
- **MCP Design**: Initial architecture design for Model Context Protocol bridge

### Changed

- N/A (Initial Release)

### Fixed

- N/A (Initial Release)
