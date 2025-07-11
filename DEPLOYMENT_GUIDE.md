# 🚀 Deployment Guide

This guide explains how to deploy the Legal AI Agents system using Docker Compose.

## 📋 Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- Domain name with DNS configured
- Linux server with at least 8GB RAM and 4 CPU cores
- OpenAI API key
- (Optional) AWS S3 credentials for backups

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Cyarun/Legal-AI-Agents-IND.git
cd Legal-AI-Agents-IND

# Copy environment files
cp .env.prod.example .env.prod
cp unified-api/.env.example unified-api/.env
```

### 2. Configure Environment

Edit `.env.prod` with your values:
```bash
# Required configurations
DOMAIN=your-domain.com
ACME_EMAIL=your-email@domain.com
OPENAI_API_KEY=sk-...
NEO4J_PASSWORD=strong-password-here
GRAFANA_PASSWORD=another-strong-password
```

### 3. Generate Basic Auth for Traefik

```bash
# Install htpasswd if not available
sudo apt-get install apache2-utils

# Generate password
htpasswd -nb admin your-password
# Copy the output to TRAEFIK_AUTH in .env.prod
```

### 4. Start Services

```bash
# Start all services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📦 Services Overview

### Core Services
- **Unified API**: https://api.your-domain.com
- **API Docs**: https://api.your-domain.com/docs
- **Neo4j Browser**: Port 7474 (not exposed externally)

### Monitoring
- **Grafana**: https://grafana.your-domain.com
- **Prometheus**: https://prometheus.your-domain.com
- **Traefik Dashboard**: https://traefik.your-domain.com

## 🔒 Security Features

### SSL/TLS
- Automatic Let's Encrypt certificates via Traefik
- HTTP to HTTPS redirect
- TLS 1.2+ only

### Authentication
- Basic auth for monitoring dashboards
- API key authentication for services
- Network isolation between containers

### Firewall Rules
```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 📊 Monitoring Setup

### 1. Access Grafana
- URL: https://grafana.your-domain.com
- Login with credentials from .env.prod
- Prometheus datasource is pre-configured

### 2. Import Dashboards
```bash
# Copy dashboard files
cp monitoring/dashboards/*.json /path/to/grafana/dashboards/
```

### 3. Set Up Alerts
- Configure alert channels in Grafana
- Set up Prometheus alerting rules
- Test alert notifications

## 🔄 Backup Configuration

### Automatic Backups
Backups run daily at 2 AM by default:
- Neo4j database dumps
- Redis snapshots
- Optional S3 upload

### Manual Backup
```bash
# Run backup manually
docker exec backup-service /backup.sh

# Check backup files
ls -la ./backups/
```

### Restore from Backup
```bash
# Stop services
docker-compose -f docker-compose.prod.yml stop neo4j redis

# Restore Neo4j
tar -xzf backups/neo4j/neo4j_backup_TIMESTAMP.tar.gz -C /var/lib/docker/volumes/legal-ai-agents-ind_neo4j_data/_data/

# Restore Redis
cp backups/redis/redis_backup_TIMESTAMP.rdb /var/lib/docker/volumes/legal-ai-agents-ind_redis_data/_data/dump.rdb

# Restart services
docker-compose -f docker-compose.prod.yml start neo4j redis
```

## 🚨 Troubleshooting

### Check Service Health
```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Check specific service logs
docker-compose -f docker-compose.prod.yml logs unified-api

# Test API health
curl https://api.your-domain.com/health
```

### Common Issues

#### SSL Certificate Issues
```bash
# Check Traefik logs
docker logs traefik

# Manually trigger certificate renewal
docker exec traefik traefik renew --cert
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Adjust limits in docker-compose.prod.yml
```

#### Connection Issues
```bash
# Check network
docker network ls
docker network inspect legal-ai-agents-ind_unified-network

# Test internal connectivity
docker exec unified-api ping neo4j
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# In docker-compose.prod.yml
unified-api:
  deploy:
    replicas: 3
```

### Vertical Scaling
Adjust resource limits in docker-compose.prod.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

## 🔄 Updates and Maintenance

### Update Services
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Recreate containers
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### Maintenance Mode
```bash
# Scale down API
docker-compose -f docker-compose.prod.yml scale unified-api=0

# Perform maintenance
# ...

# Scale back up
docker-compose -f docker-compose.prod.yml scale unified-api=2
```

## 📋 Production Checklist

- [ ] Domain DNS configured
- [ ] Environment variables set
- [ ] SSL certificates working
- [ ] Monitoring dashboards accessible
- [ ] Backups configured and tested
- [ ] Firewall rules applied
- [ ] Resource limits set appropriately
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Alert notifications working

## 🆘 Support

For issues:
1. Check service logs
2. Review this guide
3. Check GitHub issues
4. Contact support

Remember to never commit `.env.prod` or any files containing secrets!