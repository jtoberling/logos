# Logos Kubernetes Deployment

This directory contains Kubernetes manifests for deploying Logos in a Kubernetes cluster using Kustomize.

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (1.19+)
- kubectl configured
- Storage class available for PVCs

### Deploy with Kustomize

```bash
# Deploy to logos namespace
kubectl apply -k .

# Check deployment status
kubectl get pods -n logos
kubectl get pvc -n logos
kubectl get services -n logos

# View logs
kubectl logs -n logos deployment/logos-mcp -c logos-mcp
kubectl logs -n logos deployment/logos-mcp -c qdrant
```

### Manual Deployment

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create ConfigMap and Secrets
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Create PersistentVolumeClaims
kubectl apply -f pvc.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 🔧 Configuration

### Environment Variables

Edit `secrets.yaml` to configure:

```yaml
stringData:
  LLM_PROVIDER: "ollama"  # or openai, anthropic, gemini
  LLM_MODEL: "llama2"
  LLM_TEMPERATURE: "0.7"
  # Add API keys for cloud providers
```

### Storage

Default PVC sizes:
- **qdrant-storage**: 10Gi (vector database)
- **logos-data**: 5Gi (documents & memories)
- **logos-logs**: 1Gi (logs)

Adjust in `pvc.yaml` based on your needs.

### Resources

Default resource requests/limits:
- **Qdrant**: 512Mi-1Gi RAM, 0.25-0.5 CPU cores
- **Logos MCP**: 1Gi-2Gi RAM, 0.5-1 CPU cores

## 🌐 Networking

### Service Types

Current configuration uses `ClusterIP`. For external access:

1. **LoadBalancer** (cloud providers):
   ```yaml
   spec:
     type: LoadBalancer
   ```

2. **NodePort** (development):
   ```yaml
   spec:
     type: NodePort
   ```

3. **Ingress** (recommended):
   Uncomment and configure the Ingress in `service.yaml`

### Port Mapping

| Service | Internal Port | External Port | Protocol |
|---------|---------------|---------------|----------|
| Qdrant HTTP | 6333 | 6333 | HTTP |
| Qdrant gRPC | 6334 | 6334 | gRPC |
| Logos MCP | 6335 | 6335 | HTTP |

## 🔍 Monitoring & Troubleshooting

### Health Checks

- **Qdrant**: HTTP `/healthz` endpoint
- **Logos MCP**: TCP connection to port 6335

### Logs

```bash
# All containers
kubectl logs -n logos deployment/logos-mcp --all-containers

# Specific container
kubectl logs -n logos deployment/logos-mcp -c logos-mcp
kubectl logs -n logos deployment/logos-mcp -c qdrant

# Follow logs
kubectl logs -n logos deployment/logos-mcp -c logos-mcp -f
```

### Debugging

```bash
# Check pod status
kubectl describe pods -n logos

# Check events
kubectl get events -n logos --sort-by=.metadata.creationTimestamp

# Exec into container
kubectl exec -n logos -it deployment/logos-mcp -c logos-mcp -- /bin/bash

# Port forward for local testing
kubectl port-forward -n logos svc/logos-service 6335:6335
```

## 📊 Scaling

### Horizontal Scaling

Increase replicas in `deployment.yaml`:

```yaml
spec:
  replicas: 3  # Scale to 3 instances
```

### Vertical Scaling

Adjust resource limits in `deployment.yaml`:

```yaml
resources:
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

## 🔄 Updates

### Rolling Updates

```bash
# Update image
kubectl set image -n logos deployment/logos-mcp logos-mcp=logos-minimal:v1.2.0

# Check rollout status
kubectl rollout status -n logos deployment/logos-mcp

# Rollback if needed
kubectl rollout undo -n logos deployment/logos-mcp
```

### Configuration Updates

```bash
# Update ConfigMap
kubectl apply -f configmap.yaml

# Restart deployment to pick up changes
kubectl rollout restart -n logos deployment/logos-mcp
```

## 💾 Backup & Recovery

### PVC Backup

```bash
# Create backup job (example)
kubectl apply -f backup-job.yaml

# Or manual backup
kubectl exec -n logos deployment/logos-mcp -c logos-mcp -- tar czf /tmp/backup.tar.gz /app/data
kubectl cp logos/$(kubectl get pods -n logos -l app.kubernetes.io/component=mcp-server -o jsonpath='{.items[0].metadata.name}'):/tmp/backup.tar.gz ./backup.tar.gz
```

### Disaster Recovery

```bash
# Delete and recreate PVCs (WARNING: destroys data)
kubectl delete pvc -n logos --all

# Redeploy
kubectl apply -k .
```

## 🔒 Security

### Network Policies

Consider adding network policies to restrict traffic:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: logos-network-policy
  namespace: logos
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: logos
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from: []
    ports:
    - protocol: TCP
      port: 6333  # Qdrant HTTP
    - protocol: TCP
      port: 6334  # Qdrant gRPC
    - protocol: TCP
      port: 6335  # Logos MCP
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 53  # DNS
    - protocol: TCP
      port: 443 # HTTPS
```

### Security Context

Containers run as non-root user (1000:1000) with fsGroup 1000.

## 📈 Performance Tuning

### Memory Optimization

For memory-constrained environments:

```yaml
resources:
  requests:
    memory: "512Mi"
  limits:
    memory: "1Gi"
```

### CPU Optimization

For CPU-intensive workloads:

```yaml
resources:
  requests:
    cpu: "1000m"
  limits:
    cpu: "2000m"
```

## 🧪 Testing

### Port Forwarding

```bash
# Test MCP API locally
kubectl port-forward -n logos svc/logos-service 6335:6335

# Test Qdrant locally
kubectl port-forward -n logos svc/logos-service 6333:6333
```

### Integration Tests

```bash
# Run tests against deployed service
curl http://localhost:6335/version
curl http://localhost:6333/healthz
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kubectl.docs.kubernetes.io/references/kustomize/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Logos Documentation](../docs/)