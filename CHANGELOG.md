# Changelog

All notable changes to the Logos project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-01-03

### 🚀 Production Deployment & Management Enhancement Release

This release focuses on production deployment stability, comprehensive service management, and enhanced user experience for deploying and managing Logos in production environments.

#### Added

**🛠️ Advanced Service Management**
- **Redesigned Management Interface**: Complete overhaul of `manage.sh` with logical hotkey assignments and organized menu structure
- **Service Control Groups**: Separated service control and monitoring functions with clear visual boundaries
- **Interactive Menu System**: Color-coded boxes and intuitive single-letter hotkeys (s=start, v=view logs, h=health, etc.)
- **Enhanced Help System**: Comprehensive command reference with hotkey documentation

**🐳 Production Deployment Infrastructure**
- **Portainer-Optimized Configurations**: Advanced Docker Compose files specifically designed for Portainer deployment
- **Service Health Orchestration**: Proper dependency management and health check sequencing
- **Volume Management**: Optimized Docker volumes for data persistence and performance
- **Network Configuration**: Enhanced service networking with proper isolation

#### Changed

**🚀 Docker & Deployment Improvements**
- **Health Check Optimization**: Improved Qdrant health checks with proper timing and retry logic
- **Service Startup Sequencing**: Better dependency handling between Qdrant and Logos MCP services
- **Container Configuration**: Enhanced environment variables and volume mounting
- **Resource Management**: Optimized CPU and memory limits for production workloads

**📋 Management Interface Redesign**
- **Menu Structure**: Organized into logical sections (Service Control, Monitoring, System)
- **Hotkey Assignments**: Intuitive single-letter keys replacing confusing number/letter combinations
- **Visual Design**: Box-drawn borders and color coding for better user experience
- **Command Organization**: Grouped related functions together for easier navigation

**🔧 Configuration Management**
- **Environment Variables**: Enhanced Docker environment configuration for production use
- **Volume Paths**: Standardized volume mounting and cache directory management
- **Service Labels**: Comprehensive Docker labels for Portainer organization and management

#### Fixed

**🐳 Docker Deployment Issues**
- **Qdrant Health Checks**: Resolved "starting" status issues with proper endpoint validation
- **Service Dependencies**: Fixed dependency management between Qdrant and MCP services
- **Cache Directory Permissions**: Enhanced volume permissions for model caching
- **Portainer Compatibility**: Resolved YAML parsing errors and configuration issues

**🛠️ Management Script Issues**
- **Menu Navigation**: Fixed confusing hotkey assignments and menu organization
- **Command Execution**: Improved error handling and user feedback
- **Service Detection**: Enhanced container detection and status reporting
- **Help Documentation**: Updated usage instructions and command references

#### Technical Details

**Service Management Improvements:**
- New menu structure with 8 logical command groups
- Single-letter hotkeys for all major functions
- Enhanced status reporting and service monitoring
- Comprehensive error handling and user guidance

**Docker Deployment Enhancements:**
- Optimized health check intervals and timeouts
- Improved service startup sequencing
- Enhanced volume management and persistence
- Better resource allocation and limits

**Configuration Updates:**
- Streamlined environment variable management
- Improved Docker Compose compatibility
- Enhanced Portainer integration
- Better production readiness

---

## [Unreleased] - 2025-01-03

### 🧪 Testing Infrastructure Complete & Production Ready

This release marks the completion of comprehensive testing infrastructure and production readiness verification.

#### Added

**🧪 Complete Test Suite (235 Tests, 83% Coverage)**
- **Unit Tests**: 235 comprehensive unit tests covering all core components
- **Integration Tests**: End-to-end testing of MCP protocol, Docker services, and workflows
- **Performance Tests**: Load testing, memory leak detection, and response time validation
- **Coverage Achievement**: 83% code coverage across all modules

**🔧 Testing Infrastructure**
- **Reusable Test Suite**: All tests can be rerun anytime without external dependencies
- **CI/CD Ready**: pytest-cov integration with HTML reports and coverage tracking
- **Test Fixtures**: Comprehensive mocking and test data generation
- **Integration Verification**: MCP client-server communication testing

**📊 Quality Assurance**
- **Production Verification**: All Docker services tested and working
- **Performance Validation**: <2s response times under load conditions
- **Memory Testing**: No memory leaks detected in extended operation
- **Network Testing**: Docker Swarm networking and service communication verified

#### Changed

**📖 Documentation Updates**
- **README.md**: Updated coverage badges (83%) and test counts (235 tests)
- **TESTING.md**: Added integration testing guide and current status
- **Coverage Reporting**: Real-time coverage tracking and reporting

#### Technical Details

**Test Coverage Breakdown:**
```
TOTAL: 1290 lines → 218 missed → 83% coverage ✅

Key Components:
├── config.py           95% ✅
├── document_processor.py  92% ✅
├── constitution.py     88% ✅
├── letter_protocol.py  86% ✅
├── memory_tools.py     85% ✅
├── llm_client.py       91% ✅
├── file_tools.py       81% ✅
├── query_tools.py      81% ✅
├── vector_store.py     79% ✅
├── embedder.py         76% ✅
└── main.py            55% (server startup - acceptable)
```

**Integration Test Results:**
- ✅ **MCP Protocol**: 16 tools verified working
- ✅ **Docker Services**: Portainer + Swarm deployment functional
- ✅ **Load Performance**: <2s average response times
- ✅ **Memory Usage**: Stable memory usage, no leaks detected
- ✅ **Network Connectivity**: All services communicating properly

## [1.2.2] - 2025-12-31

### 🤖 Model Reliability & Performance Improvement

This patch release changes the default embedding model to a more reliable and faster alternative that works better in Docker environments and constrained network conditions.

#### Changed

**🤖 Default Embedding Model**

- **New Default Model**: Changed from `BAAI/bge-small-en-v1.5` to `sentence-transformers/all-MiniLM-L6-v2`
- **Performance Improvement**: ~95% faster model loading (0.2s vs ~30-60s for BAAI model)
- **Reliability**: More stable downloads in Docker containers and Portainer environments
- **Compatibility**: Better support for various network conditions and resource constraints

**📊 Model Characteristics**

| Model | Dimensions | Load Time | Reliability |
|-------|------------|-----------|-------------|
| `BAAI/bge-small-en-v1.5` | 384 | 30-60s | Moderate |
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | ~0.2s | High |

#### Technical Details

**Why the Change:**
- The BAAI model frequently failed downloads in Docker environments due to network timeouts
- The sentence-transformers model is smaller, more popular, and more reliable
- Maintains the same 384-dimensional embeddings for compatibility
- Significantly improves startup performance and user experience

**Backward Compatibility:**
- Existing installations can override with `EMBEDDING_MODEL` environment variable
- API and vector dimensions remain unchanged
- All existing functionality preserved

---

## [1.2.1] - 2025-12-31

### 🐳 Cache Directory Permission Fix

This patch release fixes critical cache directory permission issues that prevented FastEmbed model caching from working properly in Docker containers.

#### Fixed

**🐳 Docker Cache Directory Issues**

- **Permission Denied Errors**: Fixed `[Errno 13] Permission denied` errors when FastEmbed tried to create cache directories
- **Cache Directory Location**: Moved FastEmbed cache from `/tmp/fastembed_cache` to `/app/cache/fastembed` for better permission control
- **Directory Creation**: Ensured cache directories are created with proper permissions during Docker build
- **Volume Mounting**: Updated Docker Compose volume mounts to use the new cache location

**🔧 Technical Fixes**

- **Robust Error Handling**: Added try-catch blocks around cache directory creation to handle permission failures gracefully
- **Fallback Mechanisms**: Improved error handling with clear troubleshooting messages for cache issues
- **Dockerfile Updates**: Added proper directory creation and ownership for cache directories
- **Environment Variables**: Updated `FASTEMBED_CACHE_DIR` environment variable to use the new location

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

### 🌐 Community & Performance Enhancement Release

This release focuses on community engagement, performance optimizations, deployment improvements, and enhanced user experience while maintaining full backward compatibility with the 1.1.x series.

#### Added

**🤝 Community & Governance**

- **Code of Conduct**: Comprehensive community guidelines for respectful and inclusive participation
- **Contributing Guidelines**: Detailed development workflow and contribution process
- **Security Policy**: Structured vulnerability reporting and security maintenance procedures
- **Issue & PR Templates**: Standardized GitHub templates for consistent issue reporting and PR submissions
- **Community Health Files**: GitHub-optimized community files with proper licensing

**🔒 Security Enhancements**

- **Security Documentation**: Comprehensive SECURITY.md with vulnerability reporting process
- **Security Badges**: Added security status badges to README.md
- **GitHub Security Integration**: Automated security advisories and vulnerability tracking
- **Responsible Disclosure**: Structured process for security researchers

**🐳 Docker & Deployment Improvements**

- **Model Caching**: Persistent volume for FastEmbed model cache (`logos_model_cache`)
- **HuggingFace Integration**: Proper HuggingFace cache configuration in Docker
- **Cache Optimization**: Improved model loading performance with persistent caching
- **Telemetry Control**: Disabled HuggingFace telemetry for privacy
- **Portainer Compatibility**: Enhanced Docker Compose configurations for Portainer deployment

#### Changed

**⚡ Performance Optimizations**

- **Embedding Cache Management**: Intelligent cache directory handling with permission checks
- **Model Loading Feedback**: Enhanced logging with loading time metrics and user guidance
- **Cache Validation**: Automatic cache directory creation and write permission verification
- **Error Handling**: Improved fallback mechanisms with detailed troubleshooting guidance

**🚀 Deployment Configuration**

- **Volume Management**: Added model cache volume to Docker Compose configurations
- **Environment Variables**: Enhanced Docker environment with cache directory configurations
- **Directory Permissions**: Proper cache directory ownership and permissions in Docker
- **Network Configuration**: Optimized service networking for better performance

**📚 Documentation Updates**

- **Security Documentation**: Added comprehensive security reporting and maintenance guides
- **Community Guidelines**: Enhanced contributing process with clear expectations
- **Deployment Guides**: Updated Docker and Kubernetes deployment instructions

#### Fixed

**🐛 Docker & Container Issues**

- **Cache Directory Issues**: Resolved model cache persistence and permission problems
- **Volume Mounting**: Fixed Docker volume mount configurations for cache directories
- **Model Loading**: Improved error handling for model download and caching failures
- **Container Permissions**: Corrected file ownership issues in cache directories

**🔧 Configuration Fixes**

- **Environment Handling**: Better environment variable validation and defaults
- **Path Resolution**: Improved cache directory path handling across platforms
- **Dependency Management**: Enhanced requirements organization and compatibility

#### Technical Details

**Performance Improvements:**
- Model loading time reduced by ~70% with persistent caching
- Cache directory validation prevents common deployment issues
- Enhanced logging provides better user feedback during startup

**Community Features:**
- GitHub Issue and PR templates for consistent reporting
- Code of Conduct for community health and inclusivity
- Security policy with responsible disclosure process

**Docker Enhancements:**
- Multi-volume support for data, logs, and model cache
- HuggingFace cache integration for better performance
- Telemetry controls for privacy compliance

---

## [1.1.1] - 2025-12-31

### 🏗️ Infrastructure & Deployment Enhancement Release

This release introduces major infrastructure improvements, comprehensive deployment options, and enhanced project organization while maintaining full backward compatibility.

#### Added

**🏗️ Project Structure Restructuring**
- **Organized Directory Structure**: Reorganized codebase into logical directories (`cli/`, `deploy/`, `config/`, `docs/`)
- **Modular Architecture**: Separated concerns with dedicated directories for different components
- **Clean Repository**: Removed redundant files and improved file organization

**🚀 Deployment Infrastructure**
- **Kubernetes Support**: Complete Helm charts and Kustomize configurations for cloud deployment
- **Enhanced Docker Compose**: Improved service orchestration with Portainer compatibility
- **Multi-Environment Support**: Separate configurations for development, staging, and production

**🛠️ Management & Monitoring**
- **Service Management Script** (`manage.sh`): Comprehensive CLI tool for service control and monitoring
- **Interactive Management Interface**: Color-coded status displays and menu-driven operations
- **Health Monitoring**: Automated health checks and service status reporting
- **Security Scanning**: Integrated Semgrep security analysis with report generation

**📦 Dependency Management**
- **Requirements Organization**: Separated runtime and development dependencies with `.in` files
- **Optimized Dependencies**: Streamlined dependency tree for better compatibility
- **Version Pinning**: Improved dependency version management and security

**🔧 Configuration Management**
- **Structured Configuration**: Organized configuration files in dedicated `config/` directory
- **Environment Templates**: Standardized environment variable templates for different deployments
- **Docker Integration**: Improved container configuration and volume management

#### Changed

**📁 File Organization**
- **CLI Relocation**: Moved command-line tools from `logos-cli/` to `cli/` for better structure
- **Documentation Restructuring**: Centralized documentation in `docs/` with improved organization
- **Deployment Centralization**: All deployment configurations moved to `deploy/` directory

**🐳 Docker Improvements**
- **Volume Management**: Enhanced Docker volume configuration for better persistence
- **Service Orchestration**: Improved inter-service communication and dependency management
- **Portainer Compatibility**: Optimized configurations for Portainer deployment platform

**🔒 Security & Quality**
- **Syntax Error Fixes**: Resolved configuration file syntax issues
- **Code Quality Improvements**: Enhanced error handling and configuration validation
- **Security Scanning**: Automated vulnerability detection and reporting

#### Fixed

**🐛 Configuration Issues**
- **Syntax Errors**: Fixed indentation and syntax errors in configuration files
- **Import Issues**: Resolved module import and dependency conflicts
- **Environment Handling**: Improved environment variable validation and defaults

**🚀 Deployment Fixes**
- **Kubernetes Templates**: Corrected Helm template syntax and configuration issues
- **Docker Compose**: Fixed service dependencies and volume mounting issues
- **Port Management**: Resolved port conflicts and improved service isolation

#### Technical Details

**Infrastructure Added:**
- Service management script with 15+ commands
- Kubernetes deployment with Helm charts
- Enhanced Docker Compose configurations
- Security scanning and reporting system

**Directory Structure:**
```
├── cli/                    # Command-line interface
├── config/                 # Configuration files
├── deploy/                 # Deployment configurations
│   ├── docker/            # Docker Compose files
│   └── kubernetes/        # K8s manifests and Helm
├── docs/                  # Documentation
└── reports/               # Security scan reports
```

**New Commands:**
- `manage.sh status` - Service status and health
- `manage.sh security` - Run security scans
- `manage.sh deploy` - Deployment management
- `manage.sh cleanup` - Maintenance operations

---

## [1.1.0] - 2025-12-31

### 🎯 Quality Enhancement Release

This release focuses on code quality, security, and development tooling improvements while maintaining full backward compatibility with the 1.0.0 API.

#### Added

**🏷️ Version Management**

- **VERSION File**: Centralized version management with automatic loading from `VERSION` file
- **`get_version` MCP Tool**: New tool providing comprehensive version and system information (16th MCP tool total)

**🔍 Code Quality & Security**

- **Semgrep Integration**: Comprehensive static analysis rules aligned with KISS principles
- **Custom Quality Rules**: 25+ custom semgrep rules covering security, performance, and code quality
- **KISS Principle Enforcement**: Automated checks for complex code patterns, long functions, and over-engineering

**🛡️ Security Enhancements**

- **Dangerous Operations Detection**: Rules for `eval()`, `exec()`, and unsafe `pickle.load()` usage
- **Environment Variable Safety**: Checks for unsafe environment variable access patterns
- **Hardcoded Secrets Detection**: Automated detection of potential security vulnerabilities

**📏 Code Quality Rules**

- **Type Hint Enforcement**: Automated checks for missing return type annotations
- **Function Complexity Limits**: Rules against functions longer than 30 lines (KISS principle)
- **Import Organization**: Enforcement of relative imports within packages
- **Magic Numbers Detection**: Identification of unexplained numeric literals

**⚡ Performance Optimizations**

- **Inefficient Operations**: Detection of string concatenation in loops and inefficient list operations
- **Multiple Method Calls**: Identification of repeated method calls that could be cached
- **Context Manager Usage**: Enforcement of proper file handling with context managers

#### Changed

**🔧 Development Workflow**

- **Enhanced Type Safety**: Improved type hints across all modules with proper return type annotations
- **Function Signatures**: Updated `main()` function with explicit return type annotation
- **Import Organization**: Better import structure following project guidelines

**📚 Documentation Updates**

- **MANIFESTO.md**: Enhanced philosophical documentation and project vision
- **Development Guidelines**: Strengthened KISS principle documentation and coding standards

#### Technical Details

**New Dependencies:**

- `semgrep>=1.70.0`: Static analysis and code quality checking

**Quality Metrics:**

- **Test Coverage**: Maintained 80%+ coverage across all modules
- **Code Quality**: 25+ automated quality checks now enforced
- **Security**: Comprehensive security scanning integrated into development workflow

**Tool Count:** 16 MCP tools (added `get_version`)

---

## [1.0.0] - 2025-12-31

### 🎉 Major Release: Complete Memory Engine & MCP Implementation

This release transforms Logos from a concept into a fully functional, production-ready digital memory engine with comprehensive MCP (Model Context Protocol) integration.

#### Added

**🧠 Core Memory Engine**

- **Complete MCP Server**: Full FastMCP implementation with 15 tools
- **Dual Memory Architecture**: Separate collections for personality (logos_essence) and project knowledge
- **Sophia Methodology**: "Letters for Future Self" protocol for autobiographical memory
- **RAG Implementation**: Semantic search with context retrieval across memory collections

**📁 Document Intelligence**

- **Multi-Format Processing**: Support for 13+ file formats (PDF, DOCX, XLSX, HTML, TXT, MD, etc.)
- **Intelligent Chunking**: Sentence-aware text splitting with configurable overlap
- **Content Deduplication**: SHA256-based uniqueness tracking and metadata preservation
- **Document Metadata**: Comprehensive file information storage and retrieval

**🛠️ MCP Tools Suite (15 Tools)**

- **Memory Management** (4 tools): `create_letter_for_future_self`, `retrieve_recent_memories`, `retrieve_memories_by_creator`, `get_memory_statistics`
- **Query Interface** (4 tools): `query_logos`, `get_constitution`, `get_memory_context`, `get_collection_stats`
- **File Management** (7 tools): `add_file`, `add_file_base64`, `list_files`, `delete_file`, `get_file_info`, `get_supported_formats`, `reindex_file`

**🏗️ System Architecture**

- **Configuration System**: Environment-based configuration with validation
- **LLM Abstraction**: Multi-provider LLM client (OpenAI, Anthropic, Ollama, LMStudio, Gemini)
- **Vector Store**: Consolidated Qdrant interface with collection management
- **Personality Framework**: Constitution-based identity with dynamic prompt management
- **Document Processor**: Modular text extraction leveraging existing infrastructure

**🐳 Production Deployment**

- **Docker Infrastructure**: Production-ready Dockerfile with security best practices
- **Portainer/K8s Compatible**: Pure Docker volumes (no host mounts)
- **Service Orchestration**: docker-compose.yml with health checks and optional LLM services
- **Configuration Management**: Comprehensive environment variable documentation

**🧪 Quality Assurance**

- **Comprehensive Testing**: 211+ unit tests with 80% coverage
- **TDD Implementation**: Test-Driven Development throughout the codebase
- **Mock Infrastructure**: Complete test fixtures and mocking framework
- **CI/CD Ready**: pytest configuration with coverage reporting

**📚 Documentation & Guidelines**

- **Complete README**: Comprehensive project documentation with deployment guides
- **Configuration Guide**: Detailed environment variable documentation (`config/env-example.txt`)
- **Development Guidelines**: KISS principle, type hints, error handling standards
- **Architecture Overview**: Technical system design and data flow documentation

#### Changed

**🔄 Architecture Refactoring**

- **From Concept to Implementation**: Complete rewrite from basic structure to full MCP server
- **Memory-First Design**: Pure memory engine architecture (LLM integration moved to optional CLI)
- **Modular Components**: Clean separation of concerns across multiple modules
- **Docker Volume Compliance**: Removed all local directory mounts for container orchestration compatibility

**📋 File Structure Overhaul**

- **Organized Modules**: Clear separation into `config`, `engine`, `personality`, `memory`, `tools`, `llm`
- **CLI Separation**: Optional command-line client moved to dedicated `cli/` directory
- **Test Organization**: Comprehensive test suite with fixtures and mocking
- **Documentation Structure**: Organized docs with clear navigation and purpose

#### Fixed

**🐛 Implementation Issues**

- **Import Resolution**: Fixed circular imports and module loading issues
- **Global State Management**: Proper initialization and cleanup of MCP server state
- **Error Handling**: Comprehensive exception handling with meaningful error messages
- **Type Safety**: Full type hints across all functions and methods

#### Technical Details

**Dependencies Added:**

- `fastmcp`: MCP server framework
- `qdrant-client`: Vector database client
- `fastembed`: Local embedding generation
- `python-dotenv`: Environment configuration
- Document processing libraries: `PyPDF2`, `python-docx`, `beautifulsoup4`, etc.
- LLM SDKs: `openai`, `anthropic`, `httpx`, `google-genai`

**Breaking Changes:**

- **CLI Integration**: LLM integration moved from core to optional CLI client
- **Configuration**: Environment variables now required for all settings
- **File Paths**: All paths now use Docker volume conventions
- **API Structure**: Complete MCP tools API replacing previous basic interface

**Performance Metrics:**

- **Test Coverage**: 80%+ across all modules
- **Memory Efficiency**: Optimized chunking and embedding strategies
- **Query Performance**: Semantic search with configurable result limits
- **Container Size**: Minimal Docker image with multi-stage builds

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
