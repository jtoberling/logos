# 🔒 Security Policy

## 🛡️ Our Commitment to Security

**Logos** takes security seriously. As an open-source memory engine that powers AI personality systems, we are committed to ensuring the security and privacy of user data, system integrity, and the broader AI ecosystem.

This document outlines our security practices, vulnerability reporting process, and how we handle security issues in Logos.

## 📋 Supported Versions

We provide security updates and patches for the following versions:

| Version | Supported          | Security Updates   | Notes                          |
| ------- | ------------------ | ------------------ | ------------------------------ |
| 1.1.x   | :white_check_mark: | :white_check_mark: | Current stable release         |
| 1.0.x   | :white_check_mark: | :white_check_mark: | LTS until 2026-06-01           |
| < 1.0   | :x:                | :x:                | End of life - upgrade required |

### Version Support Guidelines

- **Current Release (1.1.x)**: Full security support, bug fixes, and new features
- **LTS Release (1.0.x)**: Critical security fixes only until EOL date
- **End of Life**: No security updates provided

To check your current version:

```bash
# Via MCP API
curl http://localhost:6334/tools/get_version

# Via CLI (if installed)
logos-cli version
```

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability in Logos, please help us by reporting it responsibly.

### 📧 How to Report

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead, please report security vulnerabilities using:

#### Primary Contact (Recommended)

- **GitHub Security Advisories**: [Create a private security advisory](https://github.com/jtoberling/logos/security/advisories/new)

#### Alternative Contact

- **GitHub Issues**: For non-critical security concerns, create an issue with "SECURITY:" prefix

Include the following information in your report:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact and severity assessment
- Any suggested fixes or mitigations
- Your contact information for follow-up

### 🔐 Responsible Disclosure

We follow industry-standard responsible disclosure practices:

1. **Report privately** using the email above
2. **Allow time** for us to investigate and fix the issue
3. **Do not publicly disclose** until we've released a fix
4. **Work with us** on coordinated disclosure timing

### ⏱️ Response Timeline

We aim to respond to vulnerability reports within:

- **24 hours**: Initial acknowledgment
- **72 hours**: Initial assessment and reproduction
- **1 week**: Detailed analysis and fix planning
- **2-4 weeks**: Security patch release (depending on severity)

For critical vulnerabilities that could cause immediate harm, we will work to release emergency patches as quickly as possible.

## 🔍 Security Considerations

### Architecture Security

Logos implements several security measures:

#### Memory Engine Security

- **Data Isolation**: Personality and project knowledge stored in separate vector collections
- **Access Control**: MCP tools with granular permission controls
- **Encryption**: Data encryption at rest and in transit (when configured)

#### Vector Database Security

- **Qdrant Integration**: Leverages Qdrant's built-in security features
- **Network Isolation**: Database accessible only within Docker network
- **Volume Encryption**: Docker volume encryption for persistent data

#### MCP Server Security

- **Protocol Security**: MCP protocol with request validation
- **Input Sanitization**: All inputs validated and sanitized
- **Error Handling**: Secure error responses without information leakage

### Deployment Security Best Practices

#### Docker Deployment

```bash
# Use official images only
docker pull logosproject/logos:latest

# Run with non-root user
docker run --user 1000:1000 logosproject/logos

# Use secrets for sensitive configuration
docker secret create logos_env .env

# Network isolation
docker network create --internal logos-net
```

#### Environment Variables

Never commit sensitive information:

```bash
# GOOD: Use environment variables
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# BAD: Hardcode in files
# OPENAI_API_KEY=sk-your-key-here
```

#### Network Security

- Bind services to internal networks only
- Use reverse proxies for external access
- Implement rate limiting on API endpoints
- Enable TLS/SSL for all external communications

## 🛠️ Security Updates

### Update Process

1. **Security Advisory**: Published on GitHub Security Advisories
2. **Patch Release**: Version bump with security fixes
3. **Documentation**: Updated deployment guides with security notes
4. **Communication**: Security mailing list notifications

### Staying Secure

Regularly update your Logos deployment:

```bash
# Check for updates
logos-cli version --check-updates

# Update Docker images
docker-compose pull
docker-compose up -d

# Update CLI client
pip install --upgrade logos-cli
```

## 🔬 Security Testing

We perform regular security assessments:

- **Automated Scanning**: Semgrep rules for code security
- **Dependency Checks**: Regular vulnerability scanning of dependencies
- **Container Security**: Docker image vulnerability scanning
- **Integration Testing**: Security-focused integration tests

Security scan reports are available in `/reports/` directory.

## 🤝 Security Hall of Fame

We appreciate security researchers who help make Logos safer. With your permission, we'll acknowledge your contribution in our security hall of fame.

## 📞 Contact Information

- **Security Issues**: [GitHub Security Advisories](https://github.com/jtoberling/logos/security/advisories/new)
- **General Support**: [GitHub Issues](https://github.com/jtoberling/logos/issues)
- **Documentation**: https://github.com/jtoberling/logos/security
- **GitHub Security Advisories**: https://github.com/jtoberling/logos/security/advisories

## 📜 Legal Notice

This security policy is part of the Logos project and is licensed under the same MIT License as the rest of the codebase.

By participating in our security disclosure program, you agree to abide by the responsible disclosure guidelines outlined above.
