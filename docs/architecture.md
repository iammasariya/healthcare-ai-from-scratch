# Architecture Documentation

## Overview

This healthcare AI service is intentionally built **without** any AI/ML components to establish a production-grade foundation. The architecture demonstrates the essential scaffolding every healthcare AI system needs before adding models.

## Design Principles

### 1. Auditability First
Every request receives a unique UUID audit ID that flows through the entire system. This enables:
- Complete request tracing
- Regulatory compliance
- Debugging production issues months later
- Accountability in healthcare workflows

### 2. Privacy by Design
- Only preview (first 100 chars) of clinical text is logged
- Full PHI is never written to logs
- Configurable privacy controls
- Ready for HIPAA compliance

### 3. Deterministic Before Probabilistic
- All operations are deterministic
- Predictable behavior
- Easy to test and validate
- Foundation ready for non-deterministic AI

### 4. Contract Stability
- Pydantic models define clear boundaries
- API contracts are versioned
- Models can change, interfaces shouldn't
- Client integration remains stable

## Architecture Layers

```
┌─────────────────────────────────────────┐
│          API Layer (FastAPI)             │
│  - Request validation                    │
│  - Error handling                        │
│  - CORS, middleware                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       Business Logic Layer               │
│  - Request processing                    │
│  - Audit ID assignment                   │
│  - [Future: AI integration here]         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Logging Layer                    │
│  - Structured logging                    │
│  - Privacy-aware truncation              │
│  - Audit trail                           │
└─────────────────────────────────────────┘
```

## Component Details

### FastAPI Application (`app/main.py`)
- Entry point for all requests
- Route definitions
- Middleware configuration
- Global error handlers
- Health check endpoints

**Key features:**
- Automatic OpenAPI documentation
- Request/response validation via Pydantic
- Async support for scalability
- Production-ready ASGI server (uvicorn)

### Data Models (`app/models.py`)
- Pydantic models for type safety
- Input validation
- Response serialization
- OpenAPI schema generation

**Why Pydantic:**
- Runtime type checking
- Clear error messages
- Automatic documentation
- Easy serialization/deserialization

### Logging (`app/logging.py`)
- Structured JSON logging
- Privacy-aware field truncation
- Audit ID generation
- Consistent log format

**Log structure:**
```json
{
  "audit_id": "uuid",
  "event": "event_type",
  "timestamp": "iso8601",
  "payload_preview": "first_100_chars...",
  "metadata": {}
}
```

### Configuration (`app/config.py`)
- Environment-based configuration
- Type-safe settings
- Sensible defaults
- Override via .env or environment variables

## Request Flow

```
1. HTTP Request arrives
   ↓
2. FastAPI middleware (CORS, timing)
   ↓
3. Pydantic validation
   ↓
4. Generate audit_id
   ↓
5. Log request (privacy-aware)
   ↓
6. Process request (currently: acknowledge receipt)
   ↓
7. Log response
   ↓
8. Return structured response
```

## Testing Strategy

### Unit Tests
- Model validation logic
- Logging functionality
- Configuration handling

### Integration Tests
- API endpoint behavior
- Request/response contracts
- Error handling
- Middleware functionality

### Test Coverage Goals
- Core logic: >90%
- API endpoints: >85%
- Overall: >80%

## Security Considerations

### Current Implementation
- Input validation via Pydantic
- No PHI in logs (truncation)
- CORS configuration
- Non-root Docker user

### Production Requirements
- HTTPS termination (nginx/traefik)
- Rate limiting
- Authentication/authorization
- API keys or OAuth2
- Network policies
- Secrets management

## Scalability

### Current Capacity
- Async FastAPI can handle thousands of concurrent requests
- Stateless design enables horizontal scaling
- No database bottlenecks yet

### Future Scaling
- Add load balancer (nginx, AWS ALB)
- Multiple API instances
- Message queue for async processing
- Database for persistence
- Caching layer (Redis)
- CDN for static assets

## Monitoring & Observability

### Current
- Structured JSON logs
- Health check endpoint
- Process time headers
- Request tracing via audit IDs

### Production Requirements
- Log aggregation (ELK, CloudWatch, DataDog)
- Metrics (Prometheus, Grafana)
- Distributed tracing (Jaeger, Zipkin)
- Alerting (PagerDuty, Opsgenie)
- SLO/SLA monitoring

## Deployment

### Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
# Using Docker
docker-compose up -d

# Or direct uvicorn (with process manager)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Cloud Deployment Options
- **AWS**: ECS/Fargate, Lambda (with Mangum), Elastic Beanstalk
- **GCP**: Cloud Run, App Engine, GKE
- **Azure**: Container Instances, App Service, AKS
- **Platform**: Heroku, Railway, Fly.io

## Why This Foundation Matters

### In Real Healthcare Deployments

1. **Regulatory Scrutiny**
   - FDA/regulators ask about traceability first
   - Model accuracy comes second
   - This layer survives audits

2. **Production Longevity**
   - You'll swap models frequently
   - This interface stays stable for years
   - Integration partners depend on contracts

3. **Debugging Reality**
   - Issues surface months later
   - Need to trace specific requests
   - Audit IDs make this possible

4. **Trust Building**
   - Clinicians need explainability
   - Clear data flow builds confidence
   - Deterministic foundation supports probabilistic AI

## Next Steps (Post 2)

Adding LLMs will introduce:
- API key management
- Prompt versioning
- Response validation
- Fallback handling
- Cost tracking
- Latency monitoring

But this foundation remains unchanged. That's the point.

## Questions & Design Decisions

### Why FastAPI over Flask/Django?
- Modern async support
- Automatic OpenAPI docs
- Built-in validation
- High performance
- Active community

### Why structured logging over print statements?
- Machine-parseable
- Consistent format
- Easy aggregation
- Production-grade

### Why audit IDs for every request?
- Healthcare requirement
- Debugging necessity
- Compliance mandate
- Best practice

### Why no database yet?
- Scope management
- Focus on API layer
- Database choice depends on use case
- Easy to add later

## Contributing

When extending this system:
1. Maintain audit trail integrity
2. Keep privacy controls
3. Update tests
4. Document design decisions
5. Version API changes

## References

- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- Healthcare logging: HIPAA security rule
- API design: REST best practices
