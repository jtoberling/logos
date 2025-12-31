# 🏗️ Logos Architecture Guide

## Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Data Flow](#data-flow)
- [Memory Architecture](#memory-architecture)
- [Component Design](#component-design)
- [MCP Integration](#mcp-integration)
- [Deployment Architecture](#deployment-architecture)
- [Performance Considerations](#performance-considerations)
- [Security Architecture](#security-architecture)

## Overview

Logos is a **digital memory engine** that implements the Sophia methodology for personality development and knowledge management. Unlike traditional AI systems that integrate LLMs directly, Logos maintains a strict separation between memory storage/retrieval and text generation, allowing any LLM to leverage its knowledge base.

### Core Principles
- **Memory-First Design**: Pure memory engine with RAG capabilities
- **Sophia Methodology**: "Letters for Future Self" for autobiographical memory
- **Multi-Modal Knowledge**: Support for text documents, structured data, and experiences
- **MCP Integration**: Model Context Protocol for standardized AI tool integration
- **Docker-Native**: Container orchestration ready with volume-based persistence

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Logos Ecosystem                           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   CLI Client    │  │   MCP Server    │  │  Web Dashboard  │     │
│  │  (Optional)     │  │   (Core)        │  │   (Future)      │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│           │                       │                       │         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  LLM Providers  │  │ Memory Engine   │  │ Document Engine │     │
│  │ OpenAI/Anthropic│  │   Qdrant DB     │  │ Text Extraction │     │
│  │ Ollama/LMStudio │  │  RAG Search     │  │  13+ Formats    │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### Architectural Layers

1. **Interface Layer**: MCP tools and optional CLI for interaction
2. **Processing Layer**: Document processing and text extraction
3. **Memory Layer**: Vector storage and semantic retrieval
4. **Persistence Layer**: Docker volumes and database storage

## Data Flow

### Document Ingestion Flow

```
User Document → MCP Tool → Document Processor → Text Chunks → Vector Store
       ↓              ↓              ↓              ↓              ↓
   File Path     add_file()    extract_text()   embed_text()   upsert()
   Base64 Data   validation    chunk_text()    similarity     search()
   Metadata      sanitization  deduplication  persistence    retrieval
```

### Memory Query Flow

```
User Query → MCP Tool → Prompt Manager → Vector Search → Context Assembly
      ↓           ↓              ↓              ↓              ↓
  Question    query_logos()  get_constitution() search()    format_json()
  Context     validation     combine_context()  rank_results()  return
  Filters     authentication  personality_ctx   score_cutoff   metadata
```

### Personality Development Flow

```
Interaction → Letter Creation → Memory Storage → Experience Retrieval
      ↓              ↓              ↓              ↓
  User Input  create_letter()  upsert_to_db()  semantic_search()
  Emotional   validation       personality_ctx  context_injection()
  Learning    timestamp        autobiography   prompt_enhancement()
```

## Memory Architecture

### Collection Structure

Logos uses three specialized vector collections in Qdrant:

#### 1. Logos Essence (`logos_essence`)
- **Purpose**: Autobiographical memory and personality development
- **Content**: "Letters for Future Self" - subjective experiences and lessons
- **Structure**:
  ```json
  {
    "letter_id": "uuid",
    "timestamp": "ISO8601",
    "interaction_summary": "What happened",
    "emotional_context": "How it felt",
    "lesson_learned": "What was learned",
    "creator": "Logos",
    "payload": {"additional": "data"}
  }
  ```

#### 2. Project Knowledge (`project_knowledge`)
- **Purpose**: Technical knowledge and documentation
- **Content**: Processed documents, code, specifications
- **Structure**:
  ```json
  {
    "filename": "document.pdf",
    "file_format": "PDF",
    "content_hash": "sha256",
    "chunk_index": 0,
    "total_chunks": 5,
    "text_length": 1000,
    "processed_at": "ISO8601"
  }
  ```

#### 3. Canon (`canon`)
- **Purpose**: Core constitution and unchanging principles
- **Content**: Manifesto, core personality traits, system prompts
- **Structure**: Static documents with version control

### Embedding Strategy

- **Model**: BAAI/bge-small-en-v1.5 (384 dimensions)
- **Chunking**: Sentence-aware splitting with 200-character overlap
- **Indexing**: Cosine similarity with score thresholding
- **Caching**: Content hash-based deduplication

## Component Design

### Core Components

#### Configuration System (`src/config.py`)
```python
class LogosConfig:
    """Centralized configuration management"""
    # Environment-based configuration
    # Validation and defaults
    # Docker volume path handling
```

**Responsibilities:**
- Environment variable loading and validation
- Configuration singleton pattern
- Path resolution for Docker volumes
- LLM provider configuration

#### Vector Store (`src/engine/vector_store.py`)
```python
class LogosVectorStore:
    """Qdrant vector database interface"""
    COLLECTIONS = {
        "logos_essence": "Personality memories",
        "project_knowledge": "Technical knowledge",
        "canon": "Core constitution"
    }
```

**Responsibilities:**
- Collection lifecycle management
- Vector upsert and search operations
- Metadata handling and filtering
- Connection pooling and error handling

#### Document Processor (`src/engine/document_processor.py`)
```python
class DocumentProcessor:
    """Multi-format document processing"""
    PREFERRED_FORMATS = ["PDF", "DOCX", "XLSX", "HTML", "TXT", "MD"]
```

**Responsibilities:**
- File format detection and validation
- Text extraction from 13+ formats
- Intelligent chunking with boundary detection
- Metadata preservation and deduplication

#### Constitution Manager (`src/personality/constitution.py`)
```python
class LogosConstitution:
    """Personality foundation and identity"""
    def get_constitution(self) -> str:
        """Return formatted personality constitution"""
```

**Responsibilities:**
- Manifesto parsing and identity formation
- Personality trait extraction
- Behavioral guideline management
- Dynamic principle addition

#### Letter Protocol (`src/memory/letter_protocol.py`)
```python
@dataclass
class Letter:
    """Sophia methodology memory unit"""
    interaction_summary: str
    emotional_context: str
    lesson_learned: str = ""
```

**Responsibilities:**
- Autobiographical memory creation
- Experience validation and formatting
- Memory retrieval and statistics
- Creator-based filtering

### MCP Tools Architecture

#### Tool Categories

**Memory Tools (`src/tools/memory_tools.py`)**:
- `create_letter_for_future_self`: Personality development
- `retrieve_recent_memories`: Recent experience access
- `retrieve_memories_by_creator`: Filtered memory retrieval
- `get_memory_statistics`: Memory analytics

**Query Tools (`src/tools/query_tools.py`)**:
- `query_logos`: Main context retrieval interface
- `get_constitution`: Personality access
- `get_memory_context`: Collection-specific search
- `get_collection_stats`: Metadata and statistics

**File Tools (`src/tools/file_tools.py`)**:
- `add_file` / `add_file_base64`: Document ingestion
- `list_files`: Knowledge base inventory
- `delete_file`: Content removal
- `get_file_info` / `get_supported_formats`: Metadata access

## MCP Integration

### Server Architecture

```python
from fastmcp import FastMCP

server = FastMCP(
    name="Logos",
    instructions="Digital personality and memory engine",
    version="1.0.0"
)

# Tool registration
server.register_tools(memory_tools)
server.register_tools(query_tools)
server.register_tools(file_tools)
```

### Tool Design Patterns

**Consistent Error Handling**:
```python
@tool()
def example_tool(param: str) -> str:
    if not _component:
        return '{"error": "Component not initialized"}'
    try:
        # Tool logic
        return json.dumps({"result": data})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Parameter Validation**:
- Type hints for all parameters
- Runtime validation with clear error messages
- Sanitization of user inputs

**Response Formatting**:
- JSON responses for structured data
- Human-readable strings for simple operations
- Consistent error response format

## Deployment Architecture

### Docker Compose Structure

```yaml
services:
  qdrant:        # Vector database
  logos-mcp:     # Main application
  ollama:        # Optional LLM (profile: llm)
  lmstudio:      # Optional LLM (profile: llm)

volumes:
  qdrant_storage:    # Vector data persistence
  logos_data:        # File storage
  logos_logs:        # Log persistence
```

### Volume Strategy

**Pure Docker Volumes** (Portainer/K8s Compatible):
- No host directory mounts
- Named volumes for data persistence
- Volume backup/restore capabilities
- Cross-platform compatibility

### Service Dependencies

```
logos-mcp → qdrant (required)
ollama/lmstudio → logos-mcp (optional)
CLI client → logos-mcp (external)
```

## Performance Considerations

### Query Optimization

**Semantic Search Tuning**:
- Configurable result limits (default: 3-5 per collection)
- Score thresholding to filter irrelevant results
- Collection-specific search parameters
- Caching strategies for frequent queries

**Chunking Strategy**:
- 1000-character chunks with 200-character overlap
- Sentence boundary detection
- Word boundary fallbacks
- Memory-efficient processing

### Memory Management

**Vector Database Optimization**:
- Collection partitioning by content type
- Index optimization for semantic search
- Connection pooling and reuse
- Background indexing and maintenance

**Resource Usage**:
- Local embeddings (no API calls)
- Configurable batch sizes
- Memory-efficient text processing
- Graceful degradation on resource limits

## Security Architecture

### Container Security

**Docker Best Practices**:
- Non-root user execution
- Minimal base image (python:3.12-slim)
- No privileged containers
- Read-only filesystems where possible

### Data Protection

**Volume Security**:
- Encrypted volume backups
- Access control through Docker/K8s
- Secure credential management
- Audit logging for sensitive operations

### API Security

**MCP Tool Security**:
- Input validation and sanitization
- Rate limiting considerations
- Authentication through MCP protocol
- Secure configuration management

### LLM Integration Security

**Provider Isolation**:
- API keys through environment variables
- No key storage in application code
- Secure credential rotation
- Provider-specific security practices

---

## Integration Points

### Existing Infrastructure

**Document Processing**: Leverages existing text extraction system from neighboring project for 13+ file format support.

**Vector Storage**: Integrates with Qdrant for high-performance semantic search and persistence.

**LLM Providers**: Modular client architecture supporting multiple LLM backends without coupling to core memory engine.

### Extension Points

**Plugin System**: MCP tools can be extended for new memory types and processing capabilities.

**Custom Embeddings**: Embedding model can be swapped for domain-specific requirements.

**Alternative Storage**: Vector store abstraction allows migration to other databases (Pinecone, Weaviate, etc.).

This architecture provides a solid foundation for digital personality development while maintaining flexibility for future enhancements and integrations.