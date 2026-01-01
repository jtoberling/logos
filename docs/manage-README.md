# Logos Service Manager

A comprehensive management script for Logos services, providing easy control over Docker containers, monitoring, and maintenance operations.

## 🚀 Quick Start

```bash
# Make script executable (first time only)
chmod +x manage.sh

# Show interactive menu
./manage.sh

# Or use command-line interface
./manage.sh status
./manage.sh start
./manage.sh health
./manage.sh security
```

## 📋 Available Commands

### Interactive Mode
Run `./manage.sh` without arguments for a full interactive menu with service status and options.

### Command Line Interface

| Command | Description |
|---------|-------------|
| `status` | Show current service status and health |
| `start` | Start core services (Qdrant + Logos MCP) |
| `start-llm` | Start optional LLM services (Ollama + LMStudio) |
| `stop` | Stop all running services |
| `logs` | View logs for individual services |
| `health` | Perform comprehensive health checks |
| `security` | Run security scan with Semgrep |
| `cleanup` | Remove containers and volumes (⚠️ destructive) |
| `help` | Show usage information |

## 🔍 Service Status

The status display shows:

- **SERVICE**: Component name
- **STATUS**: Current state (running/stopped/not created)
- **PORTS**: Exposed ports
- **UPTIME**: How long the service has been running
- **URL**: Access URL for the service

### Status Colors
- 🟢 **Green**: Service is running and healthy
- 🔴 **Red**: Service is stopped or unhealthy
- 🟡 **Yellow**: Service not created or optional

## 🛠️ Service Management

### Starting Services

```bash
# Start core services only
./manage.sh start

# Start with LLM support
./manage.sh start
./manage.sh start-llm
```

### Stopping Services

```bash
# Stop all services
./manage.sh stop
```

### Viewing Logs

```bash
# Interactive log selection
./manage.sh logs
```

## 🏥 Health Monitoring

```bash
# Check all service health
./manage.sh health
```

The health check verifies:
- **Qdrant**: HTTP health endpoint (`/healthz`)
- **Logos MCP**: TCP connectivity and API version
- **LLM Services**: Basic connectivity (if running)

## 🔒 Security Scanning

```bash
# Run security scan with Semgrep
./manage.sh security
```

The security scan performs:
- **OWASP Top 10** vulnerability detection
- **Secrets detection** (API keys, passwords, tokens)
- **Security audit rules** for common vulnerabilities
- **JSON report generation** in `reports/` directory

**Prerequisites:**
- Semgrep must be installed: `pip install semgrep`
- Reports are saved to `reports/logos_security_scan_TIMESTAMP.json`

**Scan Results:**
- ✅ **Findings count**: Total issues detected
- 🚨 **Blocking issues**: Critical/high-severity problems
- 📄 **Detailed report**: JSON file with all findings

## 🧹 Maintenance

### Cleanup Operations

```bash
# Remove all containers and volumes (WARNING: destroys data!)
./manage.sh cleanup
```

⚠️ **Warning**: The cleanup command permanently removes all containers and volumes, including your data. Make sure to backup important information before running.

## 🔧 Configuration

The script automatically detects your Docker Compose setup and uses the appropriate configuration files:

- `docker/docker-compose.yml` - Standard deployment
- `docker/docker-compose.portainer.yml` - Portainer-optimized

## 📊 Service Information

| Service | Purpose | Ports | URL |
|---------|---------|-------|-----|
| **Qdrant** | Vector database for memories | 6333, 6334 | http://localhost:6333 |
| **Logos MCP** | Memory engine API server | 6335 | http://localhost:6335 |
| **Ollama** | Local LLM provider | 11434 | http://localhost:11434 |
| **LMStudio** | Alternative LLM provider | 1234 | http://localhost:1234 |

## 🐛 Troubleshooting

### Common Issues

1. **"Docker is not running"**
   - Ensure Docker Desktop is started
   - Check `docker info` command

2. **"Service not created"**
   - Run `./manage.sh start` first
   - Check Docker Compose configuration

3. **"Port already in use"**
   - Stop conflicting services
   - Check `netstat -tulpn | grep :6333`

4. **Permission denied**
   - Ensure script is executable: `chmod +x manage.sh`
   - Check Docker permissions

### Debug Mode

For additional debugging information, check the Docker logs directly:

```bash
# View Docker Compose logs
cd docker/
docker-compose logs

# View specific service logs
docker-compose logs logos-mcp
docker-compose logs qdrant
```

## 📈 Advanced Usage

### Custom Docker Compose Files

To use a different compose file:

```bash
# Edit the script variables at the top
DOCKER_COMPOSE_FILE="path/to/your/compose-file.yml"
```

### Automated Health Checks

Integrate with monitoring systems:

```bash
# Cron job for periodic health checks
*/5 * * * * /path/to/logos/manage.sh health >> /var/log/logos-health.log 2>&1
```

### Backup Integration

Combine with backup scripts:

```bash
#!/bin/bash
# Daily backup script
./manage.sh stop
# Perform backup operations here
./manage.sh start
```

## 🎯 Best Practices

1. **Regular Health Checks**: Run `./manage.sh health` daily
2. **Monitor Logs**: Check logs regularly for errors
3. **Clean Shutdowns**: Always use `./manage.sh stop` instead of `docker kill`
4. **Backup Data**: Regular backups of Qdrant data before major operations
5. **Resource Monitoring**: Watch memory usage, especially for LLM services

## 🔗 Integration

The management script integrates with:

- **Docker Compose**: For container orchestration
- **Portainer**: Compatible with Portainer stacks
- **Kubernetes**: Services can be deployed via Helm/Kustomize
- **Monitoring Tools**: Health check endpoints for external monitoring

## 📞 Support

For issues with the management script:

1. Check Docker and Docker Compose versions
2. Verify file permissions
3. Review Docker logs for specific errors
4. Ensure all required ports are available

## 🤝 Contributing

To extend the management script:

1. Follow the modular function structure
2. Add new commands to both CLI and interactive menu
3. Include proper error handling
4. Update this documentation

## 📋 Version Information

- **Logos Version**: 1.1.0
- **Script Version**: 1.0.0
- **Docker Compose**: Compatible with v3.8+
- **Docker**: Requires Docker 20.10+