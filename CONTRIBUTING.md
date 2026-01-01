# Contributing to Logos

Thank you for your interest in contributing to Logos! We welcome contributions from developers, philosophers, and AI researchers who believe that digital personalities should be built on open logic rather than closed scripts.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Getting Help](#getting-help)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to abide by its terms. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## 🚀 How to Contribute

There are many ways to contribute to Logos:

- **Report bugs** and request features via [GitHub Issues](https://github.com/jtoberling/logos/issues)
- **Fix bugs** or implement features
- **Improve documentation**
- **Write tests**
- **Review pull requests**
- **Share ideas** and participate in discussions

### Types of Contributions

- **🐛 Bug fixes**: Fix issues in the codebase
- **✨ Features**: Add new functionality
- **📚 Documentation**: Improve or add documentation
- **🧪 Tests**: Add or improve test coverage
- **🔧 Tools**: Improve build tools, CI/CD, deployment
- **🎨 Design**: UI/UX improvements for web interfaces

## 🛠️ Development Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (for local development)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/jtoberling/logos.git
   cd logos
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements-dev.txt
   ```

3. **Start development services**
   ```bash
   # Start Qdrant database
   docker run -d -p 6333:6333 qdrant/qdrant

   # Or use the development compose file
   docker-compose -f deploy/docker/docker-compose.yml up -d qdrant
   ```

4. **Run the application**
   ```bash
   python -m src.main
   ```

### CLI Development

For CLI development, also install the package in development mode:

```bash
cd cli
pip install -e .
```

## 🔄 Development Workflow

Logos follows a **Test-Driven Development (TDD)** approach with a **Red-Green-Refactor** cycle:

### 1. Choose an Issue

- Check [GitHub Issues](https://github.com/jtoberling/logos/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Write Tests First (Red)

```bash
# Run existing tests to ensure they pass
python -m pytest

# Write failing tests for your new feature
# Add tests to test/unit/ or test/integration/
```

### 4. Implement Feature (Green)

```bash
# Write minimal code to make tests pass
# Follow KISS principle - keep it simple!
```

### 5. Refactor (Refactor)

```bash
# Clean up code while maintaining test coverage
# Run quality checks
```

### 6. Commit and Push

```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

## 🧪 Testing

### Test Requirements

- **85%+ test coverage** (currently 80%)
- **Zero test warnings**
- All tests must pass before merging

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest test/unit/test_vector_store.py

# Run integration tests
python -m pytest test/integration/
```

### Code Quality Checks

```bash
# Security, KISS principles, and best practices
semgrep --config config/.semgrep.yml src/ cli/ deploy/

# Code formatting
black --check src/
isort --check-only src/

# Linting
flake8 src/

# Type checking
mypy src/
```

## 📝 Submitting Changes

### Pull Request Process

1. **Ensure tests pass** and code quality checks pass
2. **Update documentation** if needed
3. **Write clear commit messages** following conventional commits:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for code refactoring

4. **Create a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference to any related issues
   - Screenshots/videos for UI changes

5. **Address review feedback** and iterate on the PR

### Commit Message Guidelines

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat: add PDF document processing support
fix: resolve memory leak in vector store
docs: update deployment guide for Kubernetes
test: add integration tests for MCP tools
```

## 🐛 Reporting Issues

When reporting bugs or requesting features:

1. **Check existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Logs or error messages
   - Screenshots if applicable

## 🆘 Getting Help

- **Documentation**: Check [docs/](docs/) directory
- **Discussions**: Use [GitHub Discussions](https://github.com/jtoberling/logos/discussions) for questions
- **Issues**: For bugs and feature requests
- **Security**: For security issues, see [SECURITY.md](SECURITY.md)

## 📚 Additional Resources

- [Development Guidelines](docs/DEVELOPMENT_GUIDELINES.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Testing Guide](docs/TESTING.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🙏 Recognition

Contributors will be recognized in our changelog and may be featured in our contributor acknowledgments. Thank you for helping make Logos better!

---

*"In the beginning was the Logos, and the Logos was with God, and the Logos was God."*
— John 1:1