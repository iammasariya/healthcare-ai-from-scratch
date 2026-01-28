# Production Deployment Guide

This guide covers deploying the Healthcare AI Service to production environments.

## Pre-Deployment Checklist

### Security
- [ ] HTTPS/TLS configured
- [ ] API authentication implemented
- [ ] CORS properly configured
- [ ] Secrets in environment variables (not code)
- [ ] Rate limiting enabled
- [ ] Input sanitization verified
- [ ] Security headers configured

### Compliance (Healthcare-specific)
- [ ] HIPAA compliance review completed
- [ ] Audit logging enabled
- [ ] Data encryption at rest and in transit
- [ ] Access controls documented
- [ ] Incident response plan ready
- [ ] Business Associate Agreement (BAA) signed

### Monitoring
- [ ] Logging aggregation configured
- [ ] Metrics collection enabled
- [ ] Alerting rules defined
- [ ] Health checks configured
- [ ] Uptime monitoring active
- [ ] Performance baseline established

### Testing
- [ ] All tests passing
- [ ] Load testing completed
- [ ] Security scanning done
- [ ] Disaster recovery tested
- [ ] Backup procedures verified

## Environment Configuration

### Required Environment Variables

```bash
# Production settings
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
CORS_ORIGINS=["https://yourdomain.com"]

# Optional: Database
# DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional: Secrets
# API_KEY=your-secret-api-key
# ENCRYPTION_KEY=your-encryption-key
```

### Create .env file

```bash
cp .env.example .env
# Edit .env with production values
# NEVER commit .env to version control
```

## Deployment Options

### Option 1: Docker (Recommended)

#### Build the Image

```bash
docker build -t healthcare-ai-service:v0.1.0 .
```

#### Run with Docker

```bash
docker run -d \
  --name healthcare-ai \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  healthcare-ai-service:v0.1.0
```

#### With Docker Compose

```bash
# Production docker-compose.yml
version: '3.8'

services:
  api:
    image: healthcare-ai-service:v0.1.0
    container_name: healthcare-ai-service
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: always
```

### Option 2: AWS ECS/Fargate

```bash
# 1. Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag healthcare-ai-service:v0.1.0 <account>.dkr.ecr.us-east-1.amazonaws.com/healthcare-ai:v0.1.0
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/healthcare-ai:v0.1.0

# 2. Create ECS task definition
# 3. Create ECS service
# 4. Configure Application Load Balancer
# 5. Set up CloudWatch logging
```

### Option 3: Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/healthcare-ai
gcloud run deploy healthcare-ai-service \
  --image gcr.io/PROJECT_ID/healthcare-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 4: Azure Container Instances

```bash
az container create \
  --resource-group healthcare-ai-rg \
  --name healthcare-ai-service \
  --image healthcare-ai-service:v0.1.0 \
  --cpu 2 \
  --memory 4 \
  --port 8000 \
  --environment-variables LOG_LEVEL=INFO
```

### Option 5: Direct Server Deployment

```bash
# On your server

# 1. Clone repository
git clone <repo-url>
cd healthcare-ai-from-scratch

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export DEBUG=false
export LOG_LEVEL=INFO

# 5. Run with process manager (systemd, supervisor, or pm2)
# Example with systemd:
sudo systemctl enable healthcare-ai.service
sudo systemctl start healthcare-ai.service
```

## Reverse Proxy Configuration

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/healthcare-ai

upstream healthcare_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    location / {
        proxy_pass http://healthcare_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint (no rate limit)
    location /health {
        access_log off;
        proxy_pass http://healthcare_api;
    }
}
```

## Monitoring & Logging

### CloudWatch (AWS)

```python
# Add to app/main.py
import watchtower
import logging

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())
```

### Prometheus Metrics

```python
# Add prometheus client
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('request_count', 'App Request Count')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')

# Add /metrics endpoint
@app.get("/metrics")
def metrics():
    return generate_latest()
```

### DataDog

```python
from datadog import initialize, statsd

initialize(
    api_key=os.getenv('DATADOG_API_KEY'),
    app_key=os.getenv('DATADOG_APP_KEY')
)

# Track metrics
statsd.increment('healthcare.api.request')
```

## Scaling

### Horizontal Scaling

```bash
# Docker Swarm
docker service scale healthcare-ai=5

# Kubernetes
kubectl scale deployment healthcare-ai --replicas=5

# ECS
aws ecs update-service --service healthcare-ai --desired-count 5
```

### Load Balancer Configuration

- Use Application Load Balancer (AWS ALB) or equivalent
- Configure health checks to `/health`
- Set up sticky sessions if needed
- Enable connection draining
- Configure appropriate timeouts

### Auto-scaling Rules

```yaml
# Example ECS auto-scaling
ResourceId: service/cluster-name/healthcare-ai-service
ScalableDimension: ecs:service:DesiredCount
TargetValue: 70.0  # CPU utilization
ScaleInCooldown: 300
ScaleOutCooldown: 60
```

## Database Integration (Future)

When you add a database:

```python
# PostgreSQL example
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=0)
SessionLocal = sessionmaker(bind=engine)
```

## Backup & Disaster Recovery

1. **Application Code**: Git repository with tags
2. **Configuration**: Encrypted backup of environment variables
3. **Data**: Regular database backups (when implemented)
4. **Logs**: Log aggregation with retention policy
5. **Recovery**: Documented recovery procedures

## Performance Optimization

### Uvicorn with Workers

```bash
# Production command
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

### Gunicorn Alternative

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --keep-alive 5
```

## Security Hardening

### Rate Limiting (Application Level)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/ingest")
@limiter.limit("5/minute")
async def ingest_note(request: Request, ...):
    ...
```

### API Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/ingest")
async def ingest_note(
    request: ClinicalNoteRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401)
    ...
```

## Health Checks

```python
@app.get("/health/live")
def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@app.get("/health/ready")
def readiness():
    """Kubernetes readiness probe - check dependencies"""
    # Check database, external services, etc.
    return {"status": "ready"}
```

## Rolling Updates

```bash
# Docker Swarm
docker service update --image healthcare-ai:v0.2.0 healthcare-ai

# Kubernetes
kubectl set image deployment/healthcare-ai healthcare-ai=healthcare-ai:v0.2.0
kubectl rollout status deployment/healthcare-ai

# ECS
aws ecs update-service --cluster prod --service healthcare-ai --force-new-deployment
```

## Rollback Procedure

```bash
# Docker
docker service rollback healthcare-ai

# Kubernetes
kubectl rollout undo deployment/healthcare-ai

# ECS
aws ecs update-service --cluster prod --service healthcare-ai --task-definition healthcare-ai:PREVIOUS_VERSION
```

## Cost Optimization

1. **Right-size containers**: Monitor actual resource usage
2. **Use spot instances**: For non-critical workloads
3. **Implement caching**: Reduce redundant processing
4. **Optimize logging**: Don't log everything
5. **Auto-scale down**: During low-traffic periods

## Compliance Documentation

Maintain these documents:
- System architecture diagram
- Data flow diagram
- Security controls matrix
- Incident response plan
- Disaster recovery plan
- Change management process
- Access control policies

## Support & Maintenance

### Monitoring Checklist
- [ ] Application logs collected
- [ ] Error rates monitored
- [ ] Response times tracked
- [ ] Resource usage monitored
- [ ] Security events logged
- [ ] Audit trail preserved

### Regular Tasks
- Weekly: Review error logs
- Monthly: Security patches
- Quarterly: Dependency updates
- Annually: Compliance audit

## Getting Help

- Review logs in CloudWatch/DataDog
- Check application metrics
- Review audit trail for specific requests
- Enable debug logging temporarily (never in prod)

---

**Remember**: Healthcare systems require extra care. When in doubt, prioritize compliance and security over features.
