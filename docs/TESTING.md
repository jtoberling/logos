# 🧪 Logos Testing Guide

This guide covers the testing philosophy, infrastructure, and practices for the Logos project, emphasizing Test-Driven Development (TDD) and quality assurance.

## Table of Contents
- [Testing Philosophy](#testing-philosophy)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Coverage Requirements](#coverage-requirements)
- [Writing Tests](#writing-tests)
- [Test Fixtures](#test-fixtures)
- [CI/CD Integration](#cicd-integration)
- [Debugging Tests](#debugging-tests)
- [Performance Testing](#performance-testing)

## Testing Philosophy

### TDD (Test-Driven Development)

Logos follows strict TDD principles:

1. **Red**: Write a failing test first
2. **Green**: Write minimal code to pass the test
3. **Refactor**: Improve code while maintaining test passes

**Example TDD Workflow:**
```python
# 1. Write failing test
def test_add_file_success():
    result = add_file("/path/to/test.pdf")
    assert "successfully" in result

# 2. Write minimal implementation
@tool()
def add_file(file_path: str) -> str:
    return "File processed successfully"

# 3. Refactor with proper implementation
@tool()
def add_file(file_path: str) -> str:
    if not _file_processor:
        return "not properly initialized"
    # Full implementation...
```

### Quality Standards

- **Zero test warnings**: All tests must pass cleanly
- **Type hints**: 100% coverage on all functions
- **Documentation**: All public functions documented
- **No deprecated dependencies**: Keep dependencies current
- **KISS principle**: Keep tests simple and focused

## Test Structure

### Directory Organization

```
test/
├── __init__.py                 # Test package marker
├── conftest.py                 # Shared fixtures and configuration
├── fixtures/                   # Test data and utilities
│   ├── __init__.py
│   ├── test_data.py           # Sample data generators
│   └── sample_documents/      # Test document files
│       ├── sample.txt
│       ├── sample.md
│       └── empty.txt
├── unit/                       # Unit tests (isolated components)
│   ├── __init__.py
│   ├── test_config.py         # Configuration tests
│   ├── test_vector_store.py   # Vector store tests
│   ├── test_document_processor.py
│   ├── test_memory_tools.py
│   └── test_file_tools.py
└── integration/                # Integration tests (full workflows)
    ├── __init__.py
    └── test_mcp_server.py     # MCP server integration
```

### Test Categories

#### Unit Tests (`test/unit/`)
- **Isolation**: Mock all external dependencies
- **Speed**: Fast execution (< 100ms per test)
- **Focus**: Single component or function
- **Coverage**: 100% of testable code paths

#### Integration Tests (`test/integration/`)
- **Real Dependencies**: Use actual services where possible
- **Workflow Testing**: End-to-end functionality
- **Performance**: Validate real-world performance
- **Coverage**: Critical user journeys

## Running Tests

### Basic Test Execution

**Run all tests:**
```bash
python -m pytest
```

**Run with coverage:**
```bash
python -m pytest --cov=src --cov-report=html
```

**Run specific test file:**
```bash
python -m pytest test/unit/test_config.py
```

**Run specific test:**
```bash
python -m pytest test/unit/test_config.py::TestLogosConfig::test_load_config_from_env
```

### Test Options

**Verbose output:**
```bash
python -m pytest -v
```

**Stop on first failure:**
```bash
python -m pytest -x
```

**Show test durations:**
```bash
python -m pytest --durations=10
```

**Run tests in parallel:**
```bash
python -m pytest -n auto
```

### Coverage Analysis

**Generate coverage report:**
```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

**Coverage thresholds:**
```bash
python -m pytest --cov=src --cov-fail-under=80
```

**View HTML report:**
```bash
open htmlcov/index.html
```

### Test Environments

**Development testing:**
```bash
# Full test suite with coverage
python -m pytest --cov=src --cov-report=term-missing -v
```

**CI/CD testing:**
```bash
# Strict mode with coverage requirements
python -m pytest --cov=src --cov-fail-under=80 --strict-markers
```

**Pre-commit testing:**
```bash
# Quick validation before commits
python -m pytest test/unit/ -x --tb=short
```

## Coverage Requirements

### Current Status: 80%+ Coverage

**Coverage Breakdown:**
- **Core Components**: 85%+ (config, vector_store, prompt_manager)
- **MCP Tools**: 75%+ (memory_tools, query_tools, file_tools)
- **Document Processing**: 80%+ (text extraction, chunking)
- **Integration Tests**: 90%+ (critical workflows)

### Coverage Goals

**Target Coverage by Component:**
```python
# pytest-cov configuration in setup.cfg or pyproject.toml
[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
    --strict-markers

[coverage:run]
source = src
omit =
    src/__init__.py
    src/llm/__init__.py
    */venv/*
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
```

### Uncovered Code Analysis

**Acceptable Exclusions:**
```python
# Error handling branches (rare edge cases)
if rare_condition:  # pragma: no cover
    handle_rare_case()

# Debug-only code
if self.debug:  # pragma: no cover
    self.logger.debug("Debug info")

# Platform-specific code
if sys.platform == "win32":  # pragma: no cover
    windows_specific_code()
```

## Writing Tests

### Test Naming Conventions

**File Naming:**
- `test_*.py` for all test files
- `Test*` for test classes
- `test_*` for test functions

**Example Structure:**
```python
class TestDocumentProcessor:
    """Test cases for DocumentProcessor."""

    def test_initialization_success(self):
        """Test successful processor initialization."""
        pass

    def test_initialization_with_missing_deps(self):
        """Test initialization when dependencies unavailable."""
        pass
```

### Unit Test Patterns

**Mock External Dependencies:**
```python
import pytest
from unittest.mock import MagicMock, patch

def test_add_file_with_mock():
    """Test file addition with mocked dependencies."""
    with patch('src.tools.file_tools._file_processor') as mock_processor:
        mock_processor.return_value.process_file_from_path.return_value = mock_metadata

        result = add_file("/test/file.pdf")

        assert "successfully" in result
        mock_processor.return_value.process_file_from_path.assert_called_once()
```

**Test Exception Handling:**
```python
def test_add_file_not_found():
    """Test file addition when file doesn't exist."""
    with patch('src.tools.file_tools._file_processor') as mock_processor:
        mock_processor.return_value.process_file_from_path.side_effect = FileNotFoundError("File not found")

        result = add_file("/nonexistent/file.pdf")

        assert "File not found" in result
```

**Test Parameterized Cases:**
```python
@pytest.mark.parametrize("file_format,expected", [
    ("PDF", True),
    ("DOCX", True),
    ("TXT", True),
    ("UNKNOWN", False),
])
def test_format_support(file_format, expected):
    """Test file format support detection."""
    processor = DocumentProcessor()
    assert processor.is_format_supported(file_format) == expected
```

### Integration Test Patterns

**Full Workflow Testing:**
```python
def test_memory_creation_workflow():
    """Test complete memory creation workflow."""
    # Setup real components
    vector_store = LogosVectorStore()
    letter_protocol = LetterProtocol(vector_store=vector_store)

    # Execute workflow
    letter = letter_protocol.create_letter(
        interaction_summary="Test interaction",
        emotional_context="productive",
        lesson_learned="Learned testing"
    )

    success = letter_protocol.store_letter(letter)

    # Verify results
    assert success
    assert letter.letter_id is not None

    # Cleanup
    # Note: In real integration tests, consider test isolation
```

## Test Fixtures

### Shared Fixtures (`conftest.py`)

**Mock Components:**
```python
@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    client = MagicMock()
    collections = MagicMock()
    collections.collections = [
        MagicMock(name="logos_essence"),
        MagicMock(name="project_knowledge"),
        MagicMock(name="canon")
    ]
    client.get_collections.return_value = collections
    return client

@pytest.fixture
def mock_vector_store(mock_qdrant_client):
    """Mock vector store for testing."""
    store = MagicMock()
    store.search.return_value = []
    return store
```

**Test Data:**
```python
@pytest.fixture
def sample_manifesto():
    """Sample manifesto content for testing."""
    return """
THE LOGOS TEST MANIFESTO
I. Reason over Mimicry
Logos operates on logic, not imitation.
"""

@pytest.fixture
def sample_letter():
    """Sample letter data for testing."""
    return {
        "interaction_summary": "Test interaction with user",
        "emotional_context": "productive",
        "lesson_learned": "Learned about testing methodologies"
    }
```

### Global Test State Management

**Reset Global Variables:**
```python
@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global variables between tests."""
    import src.tools.file_tools as ft
    ft._file_processor = None
    ft._vector_store = None
```

## CI/CD Integration

### GitHub Actions Example

**`.github/workflows/test.yml`:**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run tests with coverage
      run: |
        python -m pytest --cov=src --cov-report=xml --cov-fail-under=80

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

**`.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest
        language: system
        pass_filenames: false
        args: [test/unit/, -x, --tb=short]
```

## Debugging Tests

### Common Test Failures

**Mock Not Working:**
```bash
# Check mock setup
from unittest.mock import patch
with patch('module.Class.method') as mock_method:
    mock_method.return_value = expected_value
    # Run test
```

**Global State Issues:**
```bash
# Reset globals between tests
@pytest.fixture(autouse=True)
def reset_state():
    module.global_var = None
```

**Async Test Issues:**
```bash
# For async tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Debugging Tools

**Verbose Test Output:**
```bash
python -m pytest -v -s --tb=long
```

**Debug Specific Test:**
```bash
python -m pytest test_file.py::TestClass::test_method -v -s --pdb
```

**Log Test Output:**
```bash
python -m pytest --log-cli-level=DEBUG --log-cli-format="%(asctime)s %(levelname)s %(message)s"
```

### Test Isolation

**Database Isolation:**
```python
@pytest.fixture
def clean_database():
    """Ensure clean database state."""
    # Reset database before each test
    vector_store.clear_all_collections()
    yield
    # Cleanup after test
    vector_store.clear_all_collections()
```

**File System Isolation:**
```python
@pytest.fixture
def temp_dir():
    """Temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
```

## Performance Testing

### Benchmark Tests

**Response Time Testing:**
```python
import time

def test_query_performance(benchmark):
    """Benchmark query performance."""
    def run_query():
        result = query_logos("test question")
        return result

    # Benchmark with pytest-benchmark
    benchmark(run_query)
```

### Load Testing

**Concurrent Requests:**
```python
import asyncio
import aiohttp

async def test_concurrent_queries():
    """Test multiple concurrent queries."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):
            tasks.append(make_query(session, f"query {i}"))

        results = await asyncio.gather(*tasks)
        assert all("success" in result for result in results)
```

### Memory Usage Testing

**Memory Profiling:**
```python
import memory_profiler

@profile
def test_memory_usage():
    """Test memory usage during document processing."""
    processor = DocumentProcessor()

    # Process large document
    metadata = processor.process_document(large_content)

    assert metadata.text_length > 10000
```

---

## Test Maintenance

### Keeping Tests Green

**Regular Test Runs:**
```bash
# Daily test execution
cron: "0 6 * * * cd /path/to/logos && python -m pytest"

# Pre-commit validation
pre-commit run --all-files
```

**Test Refactoring:**
- Remove obsolete tests
- Update tests for API changes
- Improve test performance
- Add missing edge case coverage

### Test Documentation

**Test Documentation Standards:**
```python
def test_complex_workflow():
    """
    Test complex document processing workflow.

    This test validates the complete pipeline from file ingestion
    through text extraction, chunking, and vector storage.

    Steps:
    1. Create test document
    2. Process through DocumentProcessor
    3. Verify chunks in vector store
    4. Query and validate retrieval
    """
    # Implementation...
```

This testing guide ensures Logos maintains high quality through comprehensive, maintainable test suites that validate both individual components and complete workflows.