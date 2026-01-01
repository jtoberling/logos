# Logos Docker Deployment Guide

This directory contains Docker Compose configurations for deploying Logos in various environments.

## 🚀 Quick Start

### For Portainer Users (Recommended)

1. **Copy the Portainer-optimized compose file:**
   ```bash
   cp docker-compose.portainer.yml docker-compose.yml
   ```

2. **Deploy to Portainer:**
   - Go to Portainer → Stacks
   - Create new stack
   - Upload `docker-compose.portainer.yml`
   - Set environment variables
   - Deploy

### For Docker Compose Users

1. **Basic deployment (core services only):**
   ```bash
   docker-compose up -d
   ```

2. **With local LLM support:**
   ```bash
   docker-compose --profile llm up -d
   ```

## 📁 Compose File Options

### `docker-compose.yml` (Standard)
- General-purpose compose file
- Suitable for local development and testing
- Includes all services and profiles

### `docker-compose.portainer.yml` (Portainer-Optimized)
- **Recommended for production deployment**
- Enhanced with Portainer-specific features:
  - Resource limits and reservations
  - Comprehensive labels for management
  - Environment variable templating
  - Better health checks
  - Docker volume optimization

## 🔧 Configuration

### Required Environment Variables (Portainer)

Set these in Portainer's environment variables section:

```bash
# LLM Configuration
LLM_PROVIDER=ollama          # ollama, openai, anthropic, gemini
LLM_MODEL=llama2            # Provider-specific model name
LLM_TEMPERATURE=0.7         # 0.0-1.0

# API Keys (only if using cloud providers)
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
```

### Optional Services

To enable local LLM services, use the `llm` profile:

```bash
# In Portainer: Add "--profile llm" to deployment command
# Or manually: docker-compose --profile llm up -d ollama lmstudio
```

## 📊 Services Overview

| Service | Port | Purpose | Memory | CPU |
|---------|------|---------|--------|-----|
| **qdrant** | 6333/6334 | Vector database | 512MB-1GB | 0.5 |
| **logos-mcp** | 6335 | MCP server | 1GB-2GB | 0.5-1.0 |
| **ollama** | 11434 | Local LLM | 4GB-8GB | 1.0-2.0 |
| **lmstudio** | 1234 | Local LLM | 4GB-8GB | 1.0-2.0 |

## 🔍 Health Monitoring

All services include health checks:

- **Qdrant**: HTTP `/healthz` endpoint
- **Logos MCP**: TCP connection to port 6335
- **LLM Services**: Automatic health monitoring

## 💾 Data Persistence

All data is stored in named Docker volumes:

- `qdrant_storage`: Vector database data
- `logos_data`: Document and memory data
- `logos_logs`: Application logs
- `ollama_data`: LLM models (optional)
- `lmstudio_data`: LMStudio data (optional)

**Volumes survive container updates and can be backed up independently.**

## 🚦 Portainer Labels

The Portainer-optimized compose file includes comprehensive labels:

```yaml
labels:
  - "com.docker.compose.project=logos"
  - "logos.service.type=core"
  - "logos.service.role=mcp-server"
  - "logos.version=1.1.0"
  - "logos.api.port=6335"
```

These enable better organization and filtering in Portainer.

## 🔄 Updating

### Safe Update Process:

1. **Backup volumes** (optional but recommended):
   ```bash
   docker run --rm -v logos_data:/source -v $(pwd)/backup:/dest alpine tar czf /dest/logos_backup.tar.gz -C /source .
   ```

2. **Pull new images:**
   ```bash
   docker-compose pull
   ```

3. **Update services:**
   ```bash
   docker-compose up -d
   ```

4. **Verify health:**
   ```bash
   docker-compose ps
   ```

## 🐛 Troubleshooting

### Common Issues:

1. **Port conflicts:**
   - Check if ports 6333, 6334, 6335 are available
   - Modify port mappings in compose file if needed

2. **Memory issues:**
   - Increase Docker memory allocation
   - Adjust resource limits in compose file

3. **LLM connection issues:**
   - Ensure LLM_PROVIDER matches running service
   - Check LLM service logs: `docker-compose logs ollama`

### Logs:

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs logos-mcp

# Follow logs
docker-compose logs -f qdrant
```

## 🔒 Security Notes

- All services run as non-root users
- No host directory mounts (Portainer/K8s compatible)
- API keys stored as environment variables
- Network isolation between services

## 📈 Monitoring

Monitor resource usage in Portainer dashboard:

- **Memory**: Watch for spikes during document processing
- **CPU**: LLM services may require dedicated cores
- **Storage**: Vector database grows with memory entries

## 🎯 Production Checklist

- [ ] Set appropriate resource limits
- [ ] Configure environment variables
- [ ] Enable only required LLM services
- [ ] Set up log aggregation
- [ ] Configure backup strategy
- [ ] Test health checks
- [ ] Verify network connectivity

## 📞 Support

For issues specific to Portainer deployment:
- Check Portainer logs
- Verify environment variables
- Test with standard docker-compose first
- Ensure Docker volumes are accessible