# Logos Development Guidelines

## 🎯 Quality Standards

### Test Coverage Requirements
- **Target**: Minimum 85% test coverage across all modules
- **Excellent**: 90%+ coverage for core functionality
- **Acceptable**: 94%+ coverage for entry point modules (main.py) where import error handling may be hard to test
- **Zero Warnings**: All tests must pass with zero warnings in output
- **Coverage Areas**: Unit tests, integration tests, error paths, and edge cases

### Code Quality Principles
- **KISS Principle**: Keep It Simple, Stupid - prefer simple solutions over complex ones
- **Type Hints**: Every function and method must have proper type annotations
- **Error Handling**: Comprehensive exception handling with meaningful messages
- **Logging**: Appropriate logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## 🐍 Python Version Management

### Upgrade Policy
- **Stay Current**: Use the latest stable Python version (currently 3.12.x)
- **Proactive Upgrades**: Upgrade Python versions before deprecation warnings become breaking changes
- **Compatibility**: Test compatibility with new versions early in development cycles

### Recent Lessons
- **Python 3.10 → 3.12**: Eliminated Google API deprecation warnings and improved performance
- **Benefits**: Better performance, security updates, and future-proofing

## 📦 Dependency Management

### Audit and Update Policy
- **Regular Audits**: Quarterly dependency reviews for security and deprecation issues
- **Immediate Action**: Update dependencies when deprecation warnings appear
- **Migration Planning**: Plan migrations from deprecated packages (e.g., `google.generativeai` → `google.genai`)

### Recent Migrations
- **google.generativeai** → **google.genai**: Migrated Gemini client to modern Google AI SDK
- **datetime.utcnow()** → **datetime.now(timezone.utc)**: Fixed timezone-aware datetime usage

## 🧪 Testing Strategy

### Systematic Coverage Improvement
1. **Identify Gaps**: Use `pytest --cov` to identify uncovered code
2. **Prioritize**: Focus on high-impact areas (MCP tools, core engines, public APIs)
3. **Break Down**: Divide large uncovered modules into manageable chunks
4. **Edge Cases**: Test error paths, ImportError conditions, and failure scenarios

### Mock Testing Patterns
- **Complex Dependencies**: Use `unittest.mock` for external APIs and databases
- **ImportError Testing**: Test graceful handling when optional dependencies are unavailable
- **Initialization Testing**: Verify proper setup and teardown of global state

### Recent Coverage Achievements
- **query_tools.py**: 0% → 96% (47/47 lines tested)
- **embedder.py**: 28% → 81% (significant improvement)
- **vector_store.py**: 64% → 79% (added missing methods)
- **Overall**: 72% → 89% coverage improvement

## 🔧 Development Workflow

### TDD Approach
1. **Write Tests First**: Red-Green-Refactor cycle
2. **Comprehensive Coverage**: Test happy paths, error cases, and edge conditions
3. **Integration Testing**: Test component interactions and full workflows

### Code Review Checklist
- [ ] Tests pass with 85%+ coverage
- [ ] Zero warnings in test output
- [ ] Type hints on all public functions
- [ ] Comprehensive error handling
- [ ] Dependencies are current and non-deprecated
- [ ] Python version is current and supported

## 📚 Best Practices

### File Organization
```
src/
├── config.py              # Configuration management
├── main.py                # MCP server entry point
├── engine/                # Core technical components
├── personality/           # Identity and prompt management
├── memory/                # Memory operations (Letter protocol)
├── llm/                   # LLM client abstractions
└── tools/                 # MCP tool implementations

test/
├── unit/                  # Unit tests (one per module)
├── integration/           # Workflow tests
└── fixtures/              # Test data and utilities
```

### Naming Conventions
- **Functions**: `snake_case`, descriptive names (`get_user_data`, not `get`)
- **Classes**: `PascalCase` (`LogosVectorStore`, not `VectorStore`)
- **Constants**: `UPPER_CASE` (`DEFAULT_TIMEOUT = 30`)
- **Files**: `snake_case.py` matching class names where possible

### Import Organization
```python
# Standard library
import os
import json
from typing import List, Dict, Optional

# Third-party
import fastmcp
from qdrant_client import QdrantClient

# Local imports (alphabetized)
from .config import get_config
from .engine.vector_store import LogosVectorStore
```

## 🚀 Deployment Considerations

### Docker Best Practices
- **Multi-stage builds** for smaller images
- **Non-root user** for security
- **Minimal dependencies** in final image
- **Proper signal handling** for graceful shutdown

### Volume Management
- **Docker volumes only** (no local binds)
- **Named volumes** for data persistence
- **Volume backups** documented in deployment guide

## 📊 Performance Targets

### Test Performance
- **Fast Execution**: All tests complete in < 10 seconds
- **Parallel Execution**: Tests support parallel execution where possible
- **CI/CD Integration**: Tests run automatically on commits and PRs

### Code Performance
- **Memory Efficient**: No memory leaks in long-running processes
- **Fast Startup**: MCP server starts within 5 seconds
- **Responsive**: Query responses within acceptable time limits

## 🎯 Success Metrics

### Quality Metrics
- ✅ 85%+ test coverage
- ✅ Zero test warnings
- ✅ All type hints present
- ✅ No deprecated dependencies
- ✅ Current Python version

### Community Metrics
- ✅ Clear documentation
- ✅ Reproducible setup
- ✅ Contributing guidelines
- ✅ Issue response time < 48 hours

---

*"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away." - Antoine de Saint-Exupéry*

**Remember KISS**: Keep It Simple, Stupid. Complexity is the enemy of reliability and maintainability.