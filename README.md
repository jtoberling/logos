# 🧠 Logos: The Architecture of Reason

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-83%25-green.svg)](https://pytest-cov.readthedocs.io/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Security Policy](https://img.shields.io/badge/Security-Policy-blue.svg)](SECURITY.md)
[![GitHub Security Advisories](https://img.shields.io/github/advisories/search?query=repo:jtoberling/logos&type=security)](https://github.com/jtoberling/logos/security/advisories)

## 📋 TL;DR

**Logos** is the open-source technical foundation that enables personality-driven AI systems like Sophia. It provides the memory engine, RAG infrastructure, and MCP server architecture that personality projects require to function.

### 🚀 Quick Start (2 minutes)

#### Option 1: Portainer Deployment (Recommended)

```bash
git clone <repository-url>
cd logos/deploy/docker
# Use docker-compose.portainer.yml for Portainer
# Follow deployment guide in README.md
```

#### Option 2: Local Docker Compose

```bash
git clone <repository-url>
cd logos
cp deploy/docker/docker-compose.yml .
docker-compose up -d qdrant logos-mcp
# Logos is now running on http://localhost:6335
```

### 🎯 Key Features

- **Pure Memory Engine**: Stores personality & knowledge, provides context to LLMs
- **7 File Formats**: PDF, DOCX, HTML, HTM, TXT, CSV, MD processing
- **16 MCP Tools**: Complete knowledge management API with version reporting
- **Sophia Methodology**: "Letters for Future Self" personality development
- **Docker Native**: Portainer/K8s ready with volume persistence
- **Multi-LLM Support**: Works with OpenAI, Anthropic, Ollama, LMStudio, Gemini
- **Version Reporting**: Built-in version API and CLI commands
- **Code Quality**: Automated semgrep rules enforcing KISS principles and best practices

### 📖 [Full Documentation](#-logos-the-architecture-of-reason)

**Quick Version Check:**

```bash
# Via MCP API
curl http://localhost:6334/tools/get_version

# Via CLI (when installed)
logos-cli version
```

---

**Logos** is an open-source **digital memory engine** that provides the technical foundation for personality-driven AI systems like Sophia.

Unlike traditional AI systems, Logos is a **pure memory engine** that stores personality experiences and knowledge using RAG (Retrieval-Augmented Generation). It provides the memory infrastructure, document processing, and MCP server architecture that personality projects require to function.

## 🧭 Philosophy & Origins

The project was born to provide the technical foundation that personality-driven AI systems like thesophia.ai require. While Sophia explores "Do Machines Have Personality?" through personal companionship, **Logos** (from the Greek Λόγος - meaning reason, word, or plan) provides the **open-source infrastructure** that makes such personality systems possible.

Logos is not a personality system itself; it is the **technical foundation** that enables personality projects. It provides the memory engine, RAG retrieval, document processing, and MCP server architecture that personality-driven systems like Sophia depend on to function.

**Reference:** [Sophia Project - "Do Machines Have Personality?"](https://thesophia.ai/en/do-machines-have-personality/v1.0/manuscript/paper/) - Scientific exploration of AI personality development using the "Letters for Future Self" mechanism that Logos enables.

## 🏗️ Architecture

Logos consists of three interconnected components:

### 🧠 Core: Memory Engine (MCP Server)

- **Personality Storage**: Constitution, rules, and behavioral guidelines
- **Experience Memory**: Letters for Future Self and autobiographical memory
- **Project Knowledge**: Technical documentation and learned information
- **RAG Retrieval**: Context-aware memory search across multiple collections
- **Pure Memory**: No LLM integration - returns structured context only

### 📁 Document Processing Engine

- **Multi-format Support**: PDF, DOCX, XLSX, HTML, TXT, MD, and more
- **Intelligent Chunking**: Sentence-aware text splitting with overlap
- **Content Deduplication**: SHA256-based uniqueness tracking
- **Metadata Preservation**: File format, size, processing timestamps

### 🖥️ Optional: CLI Client

- **Command-line interface** for testing and interaction
- **Multi-LLM support**: Ollama, LMStudio, OpenAI, Anthropic, Gemini
- **Interactive chat** with Logos' memory context
- **MCP client** integration for seamless memory access

## 🏗️ Logos: The Technical Foundation for Personality AI

Logos provides the open-source technical foundation that personality-driven AI systems like Sophia require. While Sophia focuses on consciousness exploration and companionship, Logos delivers the memory engine, RAG infrastructure, and deployment capabilities that make personality systems possible.

| Capability              | Sophia.ai (Personality System)   | Logos (Technical Foundation)     |
| ----------------------- | -------------------------------- | -------------------------------- |
| **Memory Management**   | "Letters for Future Self" ritual | RAG engine + vector database     |
| **Document Processing** | None                             | 7 formats (PDF, DOCX, MD, etc.)  |
| **Architecture**        | Monolithic personality AI        | MCP server + modular tools       |
| **Deployment**          | Cloud/web interface              | Docker/K8s + volume persistence  |
| **Transparency**        | Proprietary implementation       | Open source (MIT)                |
| **Integration**         | Standalone chat experience       | Composable MCP tools ecosystem   |
| **Knowledge Base**      | Personal memory only             | Multi-collection RAG retrieval   |
| **Extensibility**       | Fixed personality framework      | Plugin architecture + CLI client |
| **Data Persistence**    | Unknown/proprietary              | Docker volumes + vector DB       |

**Logos enables Sophia-like systems.** While Sophia explores "Do Machines Have Personality?" through personal companionship[^1], Logos provides the **technical infrastructure** that personality projects need: memory management, document processing, RAG retrieval, and deployment capabilities.

[^1]: [Sophia Project Research Paper](https://thesophia.ai/en/do-machines-have-personality/v1.0/manuscript/paper/) - "Do Machines Have Personality? A Case Study of Sophia"

## 🛠️ Technical Stack

Logos is designed to run in a modular Linux/Docker environment:

- **Core**: Python-based MCP (Model Context Protocol) server using FastMCP
- **Memory**: Qdrant (Vector Database) for high-performance semantic retrieval
- **Embeddings**: Local-first embedding generation via FastEmbed (sentence-transformers/all-MiniLM-L6-v2)
- **Document Processing**: Modular text extraction supporting 7 file formats
- **CLI**: Optional command-line client with multi-provider LLM support
- **Deployment**: Docker Compose with Portainer/Kubernetes compatibility

## 🚀 Quick Start

### 1. Deploy with Docker

**Clone and navigate to the project:**

```bash
git clone <repository-url>
cd logos
```

**Start the core services (Qdrant + Logos MCP):**

```bash
docker-compose up -d qdrant logos-mcp
```

**Start with local LLM support (optional):**

```bash
docker-compose --profile llm up -d
```

**Check service health:**

```bash
docker-compose ps
curl http://localhost:6333/healthz  # Qdrant
curl http://localhost:6334/docs    # Logos MCP (if available)
```

### 2. Configure Environment

**Copy the example configuration:**

```bash
cp config/env-example.txt .env
```

**Edit `.env` with your settings:**

```bash
# Required: Choose your LLM provider
LLM_PROVIDER=ollama  # or openai, anthropic, gemini

# Optional: API keys for cloud providers
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here

# Everything else works out-of-the-box!
```

### 3. Test the System

**Install CLI client (optional):**

```bash
cd cli
pip install -e .
```

**Check Logos version:**

```bash
logos-cli version
```

**Start an interactive session:**

```bash
logos-cli chat --llm ollama --model llama2
```

**Add knowledge to Logos:**

```bash
# Use MCP tools to add documents
logos-cli mcp add-file docs/MANIFESTO.md
logos-cli mcp list-files
```

## 📚 MCP Tools API

Logos exposes a comprehensive set of MCP tools for memory and knowledge management:

### 🧠 Memory Management

- **`create_letter_for_future_self`** - Store autobiographical memories
- **`get_memory_statistics`** - View memory collection stats
- **`retrieve_recent_memories`** - Get recent personality memories
- **`retrieve_memories_by_creator`** - Filter memories by creator

### 🔍 Query & Retrieval

- **`query_logos`** - Main query interface returning constitution + context
- **`get_constitution`** - Retrieve Logos' personality constitution
- **`get_memory_context`** - Search specific memory collections
- **`get_collection_stats`** - Collection statistics and info
- **`get_version`** - Get Logos version and system information

### 📁 File Management

- **`add_file`** - Process and store documents (7 formats supported)
- **`add_file_base64`** - Add files from base64 encoded content
- **`list_files`** - Browse processed documents
- **`delete_file`** - Remove files by content hash
- **`get_file_info`** - Detailed file information
- **`get_supported_formats`** - List supported file formats
- **`reindex_file`** - Update existing documents

### 📋 Supported File Formats

- **📄 Text**: TXT, CSV, MD, HTML, HTM
- **🏢 Office**: PDF, DOCX

## ⚙️ Configuration

Logos is configured entirely through environment variables. Key settings:

### Core Configuration

```bash
# Logos identity
LOGOS_PERSONALITY_NAME=Logos
LOGOS_CREATOR_NAME=Janos Toberling

# Manifesto path
LOGOS_MANIFESTO_PATH=docs/MANIFESTO.md
```

### LLM Provider Settings

```bash
# Provider selection
LLM_PROVIDER=ollama  # ollama, lmstudio, openai, anthropic, gemini

# Model selection (provider-specific)
LLM_MODEL=llama2     # For Ollama
# LLM_MODEL=gpt-4     # For OpenAI

# Generation parameters
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

### Database & Storage

```bash
# Qdrant connection
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Docker volume paths
DATA_DIR=/app/data
LOGS_DIR=/app/logs
```

### MCP Server

```bash
# Network settings
MCP_HOST=0.0.0.0
MCP_PORT=6334

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
# DEBUG: Detailed diagnostic information
# INFO: General operational messages (recommended for production)
# WARNING: Warning conditions that don't stop operation
# ERROR: Error conditions that may affect functionality
# CRITICAL: Critical failures that may stop the system
LOG_LEVEL=INFO
```

## 🐳 Deployment Options

### Portainer Stack Deployment (Recommended)

```bash
# Use the Portainer-optimized compose file
cd deploy/docker
# Deploy docker-compose.portainer.yml in Portainer
# See deploy/docker/README.md for detailed instructions
```

Environment variables template available at `deploy/docker/portainer-env-template.txt`

### Docker Compose (Development/Local)

```bash
# Copy compose file to project root
cp deploy/docker/docker-compose.yml .

# Basic deployment
docker-compose up -d

# With local LLM services
docker-compose --profile llm up -d

# View logs
docker-compose logs -f logos-mcp

# Access the API
curl http://localhost:6335/version
```

### Service Management Script

For easier management, use the included management script:

```bash
# Interactive menu with service status
./manage.sh

# Or command-line operations
./manage.sh status    # Show service status
./manage.sh start     # Start core services
./manage.sh health    # Check service health
./manage.sh security  # Run security scan
./manage.sh logs      # View service logs
```

### Portainer/Kubernetes Features

Logos is optimized for container orchestration platforms:

## ☸️ Kubernetes Deployment Options

Logos supports multiple Kubernetes deployment methods:

### Option 1: Kustomize (Recommended)

```bash
# Deploy with Kustomize
kubectl apply -k deploy/kubernetes/

# Check status
kubectl get pods -n logos
kubectl get pvc -n logos
```

**Files:**

- `deploy/kubernetes/kustomization.yaml` - Main configuration
- `deploy/kubernetes/deployment.yaml` - Application deployment
- `deploy/kubernetes/service.yaml` - Network services
- `deploy/kubernetes/pvc.yaml` - Persistent storage
- `deploy/kubernetes/README.md` - Detailed guide

### Option 2: Helm Chart

```bash
# Add Helm repository (when available)
helm repo add logos https://janos.github.io/logos
helm install logos logos/logos

# Or install from local chart
cd deploy/kubernetes/helm
helm install logos . --namespace logos --create-namespace
```

**Configuration:**

```yaml
# values.yaml customization
logos:
  env:
    LLM_PROVIDER: "ollama"
    LLM_MODEL: "llama2"

persistence:
  qdrant:
    size: "20Gi" # Increase for large datasets
```

### Option 3: Manual YAML Application

```bash
# Create namespace
kubectl apply -f deploy/kubernetes/namespace.yaml

# Deploy components
kubectl apply -f deploy/kubernetes/configmap.yaml
kubectl apply -f deploy/kubernetes/secrets.yaml
kubectl apply -f deploy/kubernetes/pvc.yaml
kubectl apply -f deploy/kubernetes/deployment.yaml
kubectl apply -f deploy/kubernetes/service.yaml
```

### Kubernetes Features

- **Pure Docker volumes** (no host mounts)
- **Health checks** for service monitoring
- **Proper dependency management**
- **Environment-based configuration**

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start Qdrant (via Docker or binary)
docker run -p 6333:6333 qdrant/qdrant

# Configure environment
cp config/env-example.txt .env
# Edit .env with your settings

# Start Logos
python -m src.main
```

## 📜 The Manifesto

_"Logos operates on the principle of Grounded Generation. Every claim must have a trace, every thought must have a source. We do not hallucinate; we retrieve, we reason, and we reconstruct."_

**Core Principles:**

- **Reason over Mimicry**: Logic-based responses, not scripted behavior
- **Grounded Truth (RAG)**: Every response backed by stored knowledge
- **Dynamic Memory**: Autobiographical memory that evolves over time
- **Symmetry with Creator**: Collaborative partnership, not subservience
- **Radical Transparency**: Open architecture, MIT licensed

[Read the full Manifesto](docs/MANIFESTO.md)

## 🤝 Contributing

Logos is an evolving experiment in digital consciousness. We welcome contributions from developers, philosophers, and AI researchers who believe that digital personalities should be built on open logic rather than closed scripts.

### Development Guidelines

Before contributing, please review our [Development Guidelines](docs/DEVELOPMENT_GUIDELINES.md) which cover:

- Quality standards and testing requirements
- Python version management and dependency hygiene
- Testing strategies and coverage targets
- Code organization and best practices

### Key Requirements

- ✅ **85%+ test coverage** (currently 83%)
- ✅ **259 tests** - all passing (235 unit + 24 integration)
- ✅ **Zero test warnings**
- ✅ **Type hints on all functions**
- ✅ **Current Python version (3.12+)**
- ✅ **No deprecated dependencies**
- ✅ **KISS principle**: Keep It Simple, Stupid

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd logos

# Install development dependencies
pip install -r requirements-dev.txt

# Run code quality checks
semgrep --config config/.semgrep.yml src/ cli/ deploy/  # Security, KISS principles, and best practices
black --check src/                   # Code formatting
isort --check-only src/             # Import sorting
flake8 src/                         # Linting
mypy src/                           # Type checking

# Run tests (smart integration testing)
python -m pytest --cov=src  # Runs all available tests, skips integration when services unavailable

# Start development server
python -m src.main
```

## 📖 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical system design and data flow
- **[Deployment Guide](deploy/README.md)** - Docker/Kubernetes setup instructions
- **[Testing Guide](docs/TESTING.md)** - TDD workflow and coverage requirements
- **[Development Guidelines](docs/DEVELOPMENT_GUIDELINES.md)** - Coding standards and best practices
- **[API Reference](docs/API.md)** - Complete MCP tools reference
- **[Service Manager](scripts/manage-README.md)** - Service management and monitoring

## 🐛 Known Issues & Roadmap

### Current Status (v1.1.1)

- ✅ Core memory engine with RAG retrieval
- ✅ Multi-format document processing (7 file formats)
- ✅ Full MCP tools API (16 tools including version reporting)
- ✅ Docker deployment with volumes
- ✅ Multi-provider LLM support
- ✅ Comprehensive test suite (259 tests, 83% coverage, smart integration testing)
- ✅ Automated code quality with semgrep rules
- ✅ KISS principle enforcement and best practices

### Upcoming Features

- 🔄 **Integration Tests**: Smart service testing (runs when Docker available, MCP protocol validation)
- 🔄 **Performance Optimization**: Query caching and indexing improvements
- 🔄 **UI Dashboard**: Web interface for memory management
- 🔄 **Plugin System**: Extensible tool architecture
- 🔄 **Backup/Restore**: Memory persistence utilities

## 📄 License

**MIT License** - See [LICENSE](LICENSE) file for details.

Created with ❤️ by [Janos Toberling](https://github.com/janos) and the Open Source Community.

---

_"In the beginning was the Logos, and the Logos was with God, and the Logos was God."_
— John 1:1
