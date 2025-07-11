# CLAUDE.md - Kubernetes Configurations

This directory contains Kubernetes manifests for deploying the Legal AI Agents system.

## Directory Structure

```
k8s/
├── base/                    # Base configurations (Kustomize)
│   ├── unified-api/        # Unified API deployment
│   ├── neo4j/              # Neo4j StatefulSet
│   ├── redis/              # Redis deployment
│   ├── monitoring/         # Prometheus, Grafana
│   └── ingress/            # Ingress configurations
├── overlays/               # Environment-specific configs
│   ├── development/        # Dev environment
│   ├── staging/            # Staging environment
│   └── production/         # Production environment
└── scripts/                # Deployment scripts
```

## Deployment Commands

```bash
# Deploy to development
kubectl apply -k overlays/development

# Deploy to staging
kubectl apply -k overlays/staging

# Deploy to production
kubectl apply -k overlays/production

# Check deployment status
kubectl get all -n legal-ai

# View logs
kubectl logs -n legal-ai deployment/unified-api

# Scale deployment
kubectl scale -n legal-ai deployment/unified-api --replicas=3
```

## Key Concepts

### Kustomize Structure
- Base manifests contain common configurations
- Overlays patch base for environment-specific settings
- Each component has its own directory

### Resource Types
- **Deployments**: Stateless services (API, workers)
- **StatefulSets**: Stateful services (Neo4j)
- **Services**: Internal networking
- **Ingress**: External access
- **ConfigMaps**: Configuration data
- **Secrets**: Sensitive data

### Best Practices
1. Use resource limits and requests
2. Configure health checks
3. Use namespaces for isolation
4. Implement RBAC
5. Use secrets for sensitive data

## Important Notes
- Always test in development first
- Use `--dry-run=client` to preview changes
- Back up persistent volumes before updates
- Monitor resource usage after deployment