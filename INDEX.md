# 📖 Healthcare AI Service - Documentation Index

Complete guide to navigating this codebase.

## 🎯 Start Here

**New to the project?** Follow this path:

1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** ← START HERE
   - What you're getting
   - 5-minute quick start
   - Core concepts
   
2. **[docs/QUICKSTART.md](docs/QUICKSTART.md)**
   - Detailed setup instructions
   - Common issues and solutions
   - First steps with the API

3. **[README.md](README.md)**
   - Full project documentation
   - API reference
   - Features and usage

## 📚 By Learning Goal

### I Want To...

#### Understand the Architecture
→ **[docs/architecture.md](docs/architecture.md)**
- System design
- Component breakdown
- Design decisions
- Request flow
- Why it's built this way

#### Run It Locally
→ **[docs/QUICKSTART.md](docs/QUICKSTART.md)**
- Prerequisites
- Installation steps
- Running the service
- Testing the API
- Troubleshooting

#### Contribute Code
→ **[CONTRIBUTING.md](CONTRIBUTING.md)**
- Development workflow
- Code style guidelines
- Testing requirements
- PR process
- Healthcare considerations

#### See What's Coming
→ **[ROADMAP.md](ROADMAP.md)**
- Complete series overview (Posts 1-12)
- Detailed post descriptions
- Long-term vision
- How to follow along

#### Track Changes
→ **[CHANGELOG.md](CHANGELOG.md)**
- Version history
- What's new
- Upgrade notes

## 💻 By Code Component

### Core Application

| File | Purpose | Key Functions |
|------|---------|--------------|
| **app/main.py** | FastAPI application | `ingest_note()`, `summarize_note()`, health checks |
| **app/models.py** | Data models | `ClinicalNoteRequest`, `SummarizeNoteResponse`, `LLMMetrics` |
| **app/logging.py** | Audit logging | `log_request()`, `log_response()`, `log_error()` |
| **app/config.py** | Configuration | `Settings` class, environment variables |
| **app/llm.py** | LLM service (Post 2) | `summarize_clinical_note()`, retry logic |
| **app/prompts.py** | Prompt management (Post 3) | `PromptManager`, versioning, integrity |
| **app/variability.py** | Variability control (Post 4) | `VariabilityMeasurer`, `DeterminismController` |
| **app/evaluation.py** | Evaluation harness (Post 5) | `Evaluator`, `GoldenDataset`, `RegressionDetector` |
| **app/shadow.py** | Shadow mode (Post 6) | `ShadowModeRunner`, `HAPIFHIRClient`, `ShadowResultStore` |
| **app/monitoring.py** | Actionable monitoring (Post 7) | `MonitoringService`, `MonitoringStateStore` |
| **app/feedback.py** | Human feedback loop (Post 8) | `FeedbackService`, `FeedbackStore` |
| **app/helm_adapter.py** | HELM integration (Post 5) | `ClinicalModel`, HELM adapter (optional) |

### Testing

| File | Purpose | Coverage |
|------|---------|----------|
| **tests/test_api.py** | API endpoints | Request validation, responses, errors, /summarize |
| **tests/test_logging.py** | Logging system | Audit IDs, privacy controls |
| **tests/test_llm.py** | LLM service (Post 2) | Retries, costs, validation, errors |
| **tests/test_prompts.py** | Prompt system (Post 3) | Versioning, integrity, templates, lifecycle |
| **tests/test_variability.py** | Variability system (Post 4) | Metrics, similarity, seeds, temperature, alerts |
| **tests/test_evaluation.py** | Evaluation harness (Post 5) | Golden datasets, evaluation metrics, regression detection |
| **tests/test_monitoring.py** | Monitoring system (Post 7) | Guardrail actions, snapshots, action expiry |
| **tests/test_feedback.py** | Feedback system (Post 8) | Submission, analytics, queue behavior |

### Examples

| File | Purpose |
|------|---------|
| **examples/test_client.py** | API client example, basic usage |
| **examples/test_summarize.py** | LLM summarization example (Post 2) |
| **examples/test_prompts.py** | Prompt versioning example (Post 3) |
| **examples/test_variability.py** | Variability measurement example (Post 4) |
| **examples/test_evaluation.py** | Evaluation demo (Post 5) |
| **examples/test_shadow_mode.py** | Shadow mode demo with inline HAPI FHIR bundle (Post 6) |
| **examples/test_shadow_hapi_server.py** | Shadow mode demo against a live HAPI FHIR server (Post 6) |
| **examples/helm_evaluation_example.py** | Hybrid evaluation with HELM (Post 5) |

### Infrastructure

| File | Purpose |
|------|---------|
| **Dockerfile** | Container definition |
| **docker-compose.yml** | Container orchestration |
| **Makefile** | Common tasks automation |
| **.env.example** | Configuration template |
| **prompts/** | Versioned prompt files (Post 3) |
| **verify_prompts.py** | Prompt verification script (Post 3) |
| **scripts/shadow_rollout_report.py** | Summarize saved shadow runs (Post 6) |
| **scripts/monitoring_action_report.py** | Evaluate monitoring and print active actions (Post 7) |
| **scripts/feedback_analytics_report.py** | Summarize feedback analytics and review queue (Post 8) |
| **ui/** | Bonus Vite frontend workbench (Posts 1-8) |

## 🔍 By Topic

### Healthcare Engineering

**Audit Trail**
- Implementation: `app/logging.py`
- Usage: `app/main.py` - every endpoint logs
- Testing: `tests/test_logging.py`
- Docs: `docs/architecture.md` - "Auditability First"

**Privacy Controls**
- Implementation: `app/logging.py` - payload truncation
- Configuration: `app/config.py` - `LOG_PAYLOAD_PREVIEW_LENGTH`
- Docs: `docs/architecture.md` - "Privacy by Design"

**HIPAA Considerations**
- Overview: `README.md` - production-minded healthcare AI foundation
- Future: `ROADMAP.md` - "Post 5: Privacy, Security, and Compliance"

### API Design

**Request Validation**
- Models: `app/models.py` - Pydantic validators
- Testing: `tests/test_api.py` - validation tests
- Docs: `README.md` - "API Reference"

**Error Handling**
- Implementation: `app/main.py` - exception handlers
- Testing: `tests/test_api.py` - error scenarios
- Docs: `docs/architecture.md` - "Request Flow"

**Health Checks**
- Implementation: `app/main.py` - `/health` endpoint
- Usage: `docker-compose.yml` - healthcheck
- Docs: `README.md` - health checks and API surface

### Testing

**Unit Tests**
- Location: `tests/test_logging.py`
- Run: `pytest tests/test_logging.py`
- Docs: `CONTRIBUTING.md` - "Testing Guidelines"

**Integration Tests**
- Location: `tests/test_api.py`
- Run: `pytest tests/test_api.py`
- Docs: `CONTRIBUTING.md` - "Testing Guidelines"

**Coverage**
- Config: `pytest.ini`
- Run: `pytest --cov=app --cov-report=html`
- Docs: `CONTRIBUTING.md` - "Test Coverage"

### Deployment

**Docker**
- Definition: `Dockerfile`
- Compose: `docker-compose.yml`
- Run: `docker-compose up`
- Docs: `README.md` - Docker quick start

**Cloud Platforms**
- Docker: `README.md` - container build and run
- Compose: `README.md` - local multi-container setup

**Production**
- Checklist: `README.md` - security and operations sections
- Monitoring: `README.md` - logging and observability overview

## 📋 Quick Reference

### Common Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload
make run

# Test
pytest
make test
pytest --cov=app --cov-report=html

# Docker
docker-compose up
docker build -t healthcare-ai-service .

# Format & Lint
make format
make lint

# Verify
./verify_project.sh
```

### Key URLs (when running locally)

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- Root Info: http://localhost:8000/

### Configuration Files

- **Environment**: `.env` (create from `.env.example`)
- **Dependencies**: `requirements.txt`, `requirements-dev.txt`
- **Tests**: `pytest.ini`
- **Git**: `.gitignore`
- **Docker**: `Dockerfile`, `docker-compose.yml`

## 🎓 Learning Paths

### Path 1: Quick Start (30 minutes)

1. Read **PROJECT_SUMMARY.md**
2. Run **verify_project.sh**
3. Follow **docs/QUICKSTART.md**
4. Explore API at http://localhost:8000/docs
5. Run **examples/test_client.py**

### Path 2: Deep Understanding (2 hours)

1. Read **README.md** completely
2. Study **docs/architecture.md**
3. Review **app/main.py**, **app/models.py**, **app/logging.py**
4. Read **tests/test_api.py** to understand behavior
5. Experiment with modifications

### Path 3: Production Deployment (1 day)

1. Complete Path 2
2. Study **README.md** sections on Docker, logging, and security
3. Set up Docker deployment
4. Configure monitoring
5. Review security checklist
6. Plan cloud deployment

### Path 4: Contribution (ongoing)

1. Complete Path 2
2. Read **CONTRIBUTING.md**
3. Study **ROADMAP.md**
4. Find an area to improve
5. Submit a PR

## 🔗 External Resources

### Official Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **Uvicorn**: https://www.uvicorn.org/
- **Pytest**: https://docs.pytest.org/

### Healthcare Standards
- **HIPAA**: https://www.hhs.gov/hipaa/
- **FHIR**: https://www.hl7.org/fhir/
- **HL7**: https://www.hl7.org/

### Related Topics
- **API Design**: REST best practices
- **Healthcare AI**: FDA guidance
- **Security**: OWASP guidelines
- **Compliance**: Healthcare data standards

## 📞 Getting Help

### In This Codebase
1. Check relevant doc from this index
2. Search code comments
3. Review tests for examples
4. Run verification script

### From Community
1. Open GitHub issue
2. Check existing issues
3. Read discussions
4. Review PRs

### For Security
- Email privately (see CONTRIBUTING.md)
- Don't open public issue
- Include reproduction steps
- Allow time for response

## ✅ Verification Checklist

Before deploying or modifying:

- [ ] Read PROJECT_SUMMARY.md
- [ ] Understand architecture.md
- [ ] All tests passing
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Security reviewed
- [ ] Privacy controls verified
- [ ] Audit trail working
- [ ] Prompt versioning configured (if using LLM)
- [ ] Prompt integrity verified
- [ ] Evaluation harness configured (if using golden datasets)

## 🎯 Remember

**Current Status**: Post 8 completed

- Foundation is built (Post 1)
- LLM integration added (Post 2)
- Prompt versioning implemented (Post 3)
- Variability control implemented (Post 4)
- Evaluation harness implemented (Post 5)
- Shadow mode deployment implemented (Post 6)
- Actionable monitoring implemented (Post 7)
- Human feedback loop implemented (Post 8)
- 4 more posts to complete the series

**The foundation outlives the models.**

---

## 📍 You Are Here

```
Healthcare AI From Scratch (12-Post Series)
│
├─ ✅ Post 1: Foundation Without AI
├─ ✅ Post 2: Adding LLMs Without Breaking Things
├─ ✅ Post 3: Prompting as Versioned Code
├─ ✅ Post 4: Determinism, Variability, and Why Clinicians Notice
├─ ✅ Post 5: Building Your First Evaluation Harness
├─ ✅ Post 6: Shadow Mode Deployment
├─ ✅ Post 7: Monitoring That Triggers Action
├─ ✅ Post 8: Human Feedback Without Burning Clinicians ← YOU ARE HERE
├─ 📋 Post 9: Failure Drills for AI Systems
├─ 📋 Post 10: Governance as Code
├─ 📋 Post 11: From Service to Platform
└─ 📋 Post 12: What This Still Does Not Solve
```

See **ROADMAP.md** for detailed descriptions of each post.

---

**Need help navigating?**

Start with **PROJECT_SUMMARY.md** and follow the learning path that matches your goals.
