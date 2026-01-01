# 🚀 Logos Deployment Guide

This guide covers deploying Logos in various environments, from simple Docker Compose setups to production Kubernetes clusters.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Portainer Deployment](#portainer-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Manual Installation](#manual-installation)
- [Configuration Management](#configuration-management)
- [Volume Management](#volume-management)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Backup & Recovery](#backup--recovery)

## Prerequisites

### System Requirements

- **Docker**: 20.10+ with Compose V2
- **Kubernetes**: 1.19+ (for K8s deployment)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 10GB free space for volumes
- **Network**: Internet access for LLM providers

### Software Dependencies

```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
sudo apt-get install docker-compose-plugin

# Kubernetes (optional)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Portainer (optional)
docker run -d -p 9443:9443 --name portainer \
    --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:latest
```

## Quick Start

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd logos
```

### 2. Configure Environment

```bash
cp config/env-example.txt .env
# Edit .env with your settings
```

### 3. Deploy Core Services

```bash
# Start Qdrant + Logos MCP
docker-compose up -d qdrant logos-mcp

# Check health
docker-compose ps
curl http://localhost:6333/healthz  # Qdrant
curl http://localhost:6334/docs    # Logos MCP
```

### 4. Test the System

```bash
# Install CLI (optional)
pip install -e cli/

# Test memory functionality
logos-cli chat --llm ollama --model llama2
```

## Docker Compose Deployment

### Basic Deployment

**Start core services:**

```bash
docker-compose up -d
```

**View service status:**

```bash
docker-compose ps
```

**Check logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f logos-mcp
```

### With Local LLM Support

**Start with Ollama:**

```bash
docker-compose --profile llm up -d
```

**Pull a model in Ollama:**

```bash
docker-compose exec ollama ollama pull llama2
```

### Service Configuration

**Environment Variables:**

```bash
# Core settings
COMPOSE_PROJECT_NAME=logos
DOCKER_BUILDKIT=1

# Resource limits
COMPOSE_DOCKER_CLI_BUILD=1
DOCKER_DEFAULT_PLATFORM=linux/amd64
```

## Portainer Deployment

### Stack Deployment

**1. Access Portainer:**

- Open http://localhost:9443
- Create admin account

**2. Create Stack:**

- Navigate to "Stacks" → "Add Stack"
- Name: `logos`
- Method: "Repository"
- Repository URL: `<your-repo-url>`
- Compose path: `docker-compose.yml`

**3. Environment Variables:**
Add environment variables in Portainer:

```
QDRANT_HOST=qdrant
QDRANT_PORT=6333
LOGOS_MANIFESTO_PATH=/app/docs/MANIFESTO.md
# ... other variables from env-example.txt
```

**4. Deploy:**

- Click "Deploy the stack"
- Monitor deployment in "Stacks" → "logos"

### Volume Management in Portainer

**Named Volumes:**

- `qdrant_storage`: Vector database persistence
- `logos_data`: Document storage
- `logos_logs`: Application logs

**Volume Inspection:**

```bash
# List volumes
docker volume ls | grep logos

# Inspect volume
docker volume inspect logos_qdrant_storage
```

## Kubernetes Deployment

### Using kubectl

**1. Create Namespace:**

```bash
kubectl create namespace logos
```

**2. Apply Manifests:**

```bash
kubectl apply -f k8s/
```

**3. Check Deployment:**

```bash
kubectl get pods -n logos
kubectl get services -n logos
kubectl get pvc -n logos
```

### Using Helm (Alternative)

**1. Add Helm Repository:**

```bash
helm repo add logos https://<your-helm-repo>
helm repo update
```

**2. Install Chart:**

```bash
helm install logos logos/logos \
    --namespace logos \
    --create-namespace \
    --values values.yaml
```

### Kubernetes Manifests Structure

```
k8s/
├── namespace.yaml           # Namespace definition
├── configmap.yaml          # Application configuration
├── secret.yaml             # API keys and secrets
├── qdrant/
│   ├── deployment.yaml     # Qdrant statefulset
│   ├── service.yaml        # Qdrant service
│   └── pvc.yaml           # Persistent volume claim
├── logos/
│   ├── deployment.yaml     # Logos MCP deployment
│   ├── service.yaml        # Logos MCP service
│   └── hpa.yaml           # Horizontal pod autoscaler
└── ingress.yaml           # Ingress configuration
```

### Persistent Volumes

**Storage Class Requirements:**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: logos-storage
provisioner: kubernetes.io/aws-ebs # Adjust for your cloud provider
parameters:
  type: gp3
  encrypted: "true"
```

## Manual Installation

### Local Development Setup

**1. Install Dependencies:**

```bash
# Python 3.12+
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

**2. Start Qdrant:**

```bash
# Via Docker
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant

# Or via binary
wget https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-unknown-linux-gnu.tar.gz
tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz
./qdrant
```

**3. Configure Environment:**

```bash
cp config/env-example.txt .env
# Edit paths for local development
DATA_DIR=./data
LOGS_DIR=./logs
```

**4. Start Logos:**

```bash
python -m src.main
```

### Production Manual Setup

**1. System Dependencies:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv nginx

# Create dedicated user
sudo useradd -r -s /bin/false logos
sudo mkdir -p /opt/logos
sudo chown logos:logos /opt/logos
```

**2. Application Setup:**

```bash
sudo -u logos bash
cd /opt/logos
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Systemd Service:**

```bash
sudo tee /etc/systemd/system/logos.service > /dev/null <<EOF
[Unit]
Description=Logos MCP Server
After=network.target qdrant.service

[Service]
Type=simple
User=logos
WorkingDirectory=/opt/logos
Environment=PATH=/opt/logos/venv/bin
ExecStart=/opt/logos/venv/bin/python -m src.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable logos
sudo systemctl start logos
```

## Configuration Management

### Environment Variables

**Core Configuration:**

```bash
# Logos Identity
LOGOS_PERSONALITY_NAME=Logos
LOGOS_CREATOR_NAME=Janos Toberling
LOGOS_MANIFESTO_PATH=/app/docs/MANIFESTO.md

# Database
QDRANT_HOST=qdrant
QDRANT_PORT=6333
LOGOS_ESSENCE_COLLECTION=logos_essence
PROJECT_KNOWLEDGE_COLLECTION=project_knowledge

# Networking
MCP_HOST=0.0.0.0
MCP_PORT=6334
LOG_LEVEL=INFO
```

**LLM Configuration:**

```bash
# Provider Selection
LLM_PROVIDER=ollama  # ollama, openai, anthropic, gemini

# Model Settings
LLM_MODEL=llama2
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Provider Endpoints
OLLAMA_BASE_URL=http://localhost:11434
LMSTUDIO_BASE_URL=http://localhost:1234/v1

# API Keys (for cloud providers)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GEMINI_API_KEY=your-gemini-key-here
```

### Configuration Validation

**Test Configuration:**

```bash
# Validate config loading
python -c "from src.config import get_config; print('Config loaded:', get_config().llm_provider)"

# Test database connection
python -c "from src.engine.vector_store import LogosVectorStore; vs = LogosVectorStore(); print('DB connected')"
```

### Secrets Management

**Docker Secrets:**

```bash
# Create secrets
echo "sk-your-openai-key" | docker secret create openai_api_key -

# Use in compose
secrets:
  openai_api_key:
    external: true
```

**Kubernetes Secrets:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: logos-secrets
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  anthropic-api-key: <base64-encoded-key>
```

## Volume Management

### Docker Volumes

**Volume Operations:**

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect logos_qdrant_storage

# Backup volume
docker run --rm -v logos_qdrant_storage:/source -v $(pwd):/backup alpine tar czf /backup/qdrant-backup.tar.gz -C /source .

# Restore volume
docker run --rm -v logos_qdrant_storage:/dest -v $(pwd):/backup alpine tar xzf /backup/qdrant-backup.tar.gz -C /dest
```

### Kubernetes PVCs

**PVC Operations:**

```bash
# Check PVC status
kubectl get pvc -n logos

# PVC YAML
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: logos-storage
```

### Data Migration

**Between Environments:**

```bash
# Export from source
docker run --rm -v source_volume:/source -v $(pwd):/export alpine tar czf /export/data.tar.gz -C /source .

# Import to destination
docker run --rm -v dest_volume:/dest -v $(pwd):/import alpine tar xzf /import/data.tar.gz -C /dest .
```

## Monitoring & Troubleshooting

### Health Checks

**Service Health:**

```bash
# Qdrant health
curl http://localhost:6333/healthz

# Logos MCP health
curl http://localhost:6334/health

# Docker health
docker-compose ps
docker stats
```

**Application Logs:**

```bash
# Docker logs
docker-compose logs -f logos-mcp

# Kubernetes logs
kubectl logs -f deployment/logos-mcp -n logos

# Application logs
docker-compose exec logos-mcp tail -f /app/logs/logos.log
```

### Common Issues

**Qdrant Connection Issues:**

```bash
# Check Qdrant logs
docker-compose logs qdrant

# Test connection
curl http://localhost:6333/collections

# Restart Qdrant
docker-compose restart qdrant
```

**Memory Issues:**

```bash
# Check memory usage
docker stats

# Adjust Docker memory limits
docker-compose.yml:
  services:
    logos-mcp:
      deploy:
        resources:
          limits:
            memory: 2G
          reservations:
            memory: 1G
```

**Port Conflicts:**

```bash
# Check port usage
netstat -tlnp | grep :6334

# Change ports in .env
MCP_PORT=8001
QDRANT_PORT=6334
```

**File Permission Issues:**

```bash
# Fix volume permissions
docker-compose exec logos-mcp chown -R logos:logos /app/data
docker-compose exec logos-mcp chown -R logos:logos /app/logs
```

## Backup & Recovery

### Automated Backups

**Docker Backup Script:**

```bash
#!/bin/bash
# backup-logos.sh

BACKUP_DIR="/opt/logos/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup volumes
docker run --rm \
  -v logos_qdrant_storage:/source \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/qdrant_$TIMESTAMP.tar.gz -C /source .

docker run --rm \
  -v logos_data:/source \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/data_$TIMESTAMP.tar.gz -C /source .

echo "Backup completed: $TIMESTAMP"
```

**Kubernetes Backup:**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: logos-backup
spec:
  schedule: "0 2 * * *" # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: alpine
              command: ["/bin/sh", "-c"]
              args:
                - |
                  tar czf /backup/qdrant-$(date +%Y%m%d).tar.gz -C /qdrant .
                  tar czf /data-$(date +%Y%m%d).tar.gz -C /logos-data .
              volumeMounts:
                - name: qdrant-storage
                  mountPath: /qdrant
                - name: logos-data
                  mountPath: /logos-data
                - name: backup
                  mountPath: /backup
          volumes:
            - name: qdrant-storage
              persistentVolumeClaim:
                claimName: qdrant-storage
            - name: logos-data
              persistentVolumeClaim:
                claimName: logos-data
            - name: backup
              persistentVolumeClaim:
                claimName: backup-storage
          restartPolicy: OnFailure
```

### Recovery Procedures

**Complete Recovery:**

```bash
# Stop services
docker-compose down

# Restore volumes
docker run --rm -v logos_qdrant_storage:/dest -v $(pwd):/backup alpine tar xzf /backup/qdrant-backup.tar.gz -C /dest
docker run --rm -v logos_data:/dest -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /dest

# Restart services
docker-compose up -d
```

**Partial Recovery:**

```bash
# Restore specific collection
docker run --rm \
  -v logos_qdrant_storage:/qdrant \
  alpine ash -c "cd /qdrant && find . -name '*project_knowledge*' -delete"

# Re-ingest documents
# Use MCP tools to re-add lost documents
```

### Disaster Recovery

**Multi-Region Setup:**

```yaml
# Kubernetes with cross-region replication
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-storage
spec:
  storageClassName: regional-pd-standard # GCP regional storage
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

---

## Support & Resources

### Getting Help

- **Logs**: Check application and Docker logs
- **Health Checks**: Use provided health endpoints
- **Documentation**: Refer to ARCHITECTURE.md for technical details
- **Issues**: Check common issues section above

### Performance Tuning

- **Memory**: Increase container memory limits
- **CPU**: Adjust CPU allocation in Docker/K8s
- **Storage**: Use SSD storage for vector databases
- **Networking**: Optimize network configuration for LLM calls

This deployment guide provides comprehensive instructions for running Logos in any environment, from local development to production Kubernetes clusters.
