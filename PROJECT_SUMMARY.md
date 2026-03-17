# 🏥 Healthcare AI From Scratch - Complete Codebase

## 📦 What You're Getting

This is a **production-grade** healthcare AI system built from first principles through six foundational posts:

- **Post 1**: Foundation without AI - The scaffolding every healthcare system needs
- **Post 2**: LLM Integration - Adding Claude with safety guarantees
- **Post 3**: Prompt Versioning - Treating prompts as first-class artifacts
- **Post 4**: Variability Control - Measuring and controlling model consistency
- **Post 5**: Evaluation Harness - Systematic model evaluation and regression detection
- **Post 6**: Shadow Mode - Safe model rollout with dual-path execution and HAPI FHIR

This demonstrates how to build healthcare AI the right way: foundation first, models second, governance third, consistency fourth, evaluation fifth, safe rollout sixth.

## 🎯 Key Features

### Post 1: Foundation
✅ **Full Audit Trail** - Every request gets a unique UUID for traceability  
✅ **Privacy-Aware Logging** - Only logs preview of clinical text, never full PHI  
✅ **Type-Safe Validation** - Pydantic models ensure data integrity  
✅ **Production Patterns** - Health checks, monitoring, error handling  

### Post 2: LLM Integration
✅ **Claude API Integration** - Clinical note summarization with retry logic  
✅ **Cost Tracking** - Per-request cost monitoring in USD  
✅ **Latency Monitoring** - Track LLM response times  
✅ **Feature Flags** - Safe rollout without breaking production  
✅ **Graceful Failures** - System continues when LLM fails  

### Post 3: Prompt Versioning
✅ **Versioned Prompts** - YAML files with semantic versioning (1.0.0, 1.1.0, 2.0.0)  
✅ **Integrity Verification** - SHA256 hashing prevents tampering  
✅ **Audit Trails** - Every request logs prompt version and hash  
✅ **Hot-Reload** - Update prompts without restarting  
✅ **A/B Testing** - Compare prompt versions in production  
✅ **Rollback Capability** - Change versions without deployment  

### Post 4: Variability Control
✅ **Variability Measurement** - Comprehensive metrics for model consistency  
✅ **Semantic Similarity** - Pairwise comparison using difflib  
✅ **Deterministic Seeds** - Context-aware reproducibility  
✅ **Temperature Recommendations** - Task/risk-based guidance  
✅ **Acceptability Thresholds** - Clinical context determines tolerance  
✅ **Production Monitoring** - Alert detection for concerning patterns  

### Post 5: Evaluation Harness
✅ **Golden Dataset Management** - JSON-based, version-controlled test examples
✅ **Evaluation Framework** - Exact and fuzzy matching metrics
✅ **Regression Detection** - Automated alerts for quality degradation
✅ **Model Comparison** - Data-driven version comparison
✅ **CI/CD Integration** - JSON output for automated pipelines
✅ **HELM Integration** - Optional Stanford HELM for research-grade metrics

### Post 6: Shadow Mode
✅ **Dual-Path Execution** - Production and candidate models run side by side
✅ **HAPI FHIR Support** - Fetch real clinical data from FHIR servers
✅ **Divergence Detection** - Automatic flagging when outputs differ
✅ **Rollout Recommendations** - Data-driven promotion decisions (hold/advance/promote)
✅ **Alert System** - Critical and warning alerts for quality issues
✅ **Result Persistence** - JSON-based shadow run history

### Infrastructure
✅ **Comprehensive Tests** - 150 tests with 100% core coverage
✅ **Docker Ready** - Container deployment with docker-compose  
✅ **Full Documentation** - Architecture, deployment, contributing guides  

## 📁 Project Structure

```
healthcare-ai-from-scratch/
├── app/                      # Main application code
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app and routes
│   ├── models.py            # Pydantic request/response models
│   ├── logging.py           # Structured logging with audit IDs
│   ├── config.py            # Configuration management
│   ├── llm.py               # LLM service with retry logic (Post 2)
│   ├── prompts.py           # Prompt management system (Post 3)
│   ├── variability.py       # Variability measurement (Post 4)
│   ├── evaluation.py        # Evaluation harness (Post 5)
│   └── shadow.py            # Shadow mode deployment (Post 6)
│
├── prompts/                  # Versioned prompt files (Post 3)
│   └── clinical_summarization_v1.0.0.yaml
│
├── tests/                    # Test suite (150 tests)
│   ├── __init__.py
│   ├── test_api.py          # API endpoint tests (31 tests)
│   ├── test_logging.py      # Logging functionality tests (12 tests)
│   ├── test_llm.py          # LLM service tests (24 tests) - Post 2
│   ├── test_prompts.py      # Prompt management tests (16 tests) - Post 3
│   ├── test_variability.py  # Variability tests (34 tests) - Post 4
│   ├── test_evaluation.py   # Evaluation tests (26 tests) - Post 5
│   └── test_shadow.py       # Shadow mode tests (8 tests) - Post 6
│
├── examples/                 # Usage examples
│   ├── test_client.py       # Example API client
│   ├── test_summarize.py    # LLM summarization example (Post 2)
│   ├── test_prompts.py      # Prompt versioning example (Post 3)
│   ├── test_variability.py  # Variability measurement example (Post 4)
│   ├── test_evaluation.py   # Evaluation demo (Post 5)
│   ├── test_shadow_mode.py  # Shadow mode demo with inline FHIR (Post 6)
│   └── test_shadow_hapi_server.py  # Shadow mode with live HAPI FHIR (Post 6)
│
├── docs/                     # Curated learning docs
│   ├── architecture.md      # Architecture decisions
│   └── QUICKSTART.md        # 5-minute quick start
│
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── pytest.ini               # Test configuration
├── Dockerfile               # Container definition
├── docker-compose.yml       # Container orchestration
├── Makefile                 # Common tasks automation
├── .env.example             # Environment variable template
├── .gitignore              # Git ignore rules
├── README.md               # Main documentation
├── CONTRIBUTING.md         # Contribution guidelines
├── CHANGELOG.md            # Version history
├── ROADMAP.md              # Project roadmap
├── LICENSE                 # MIT License
├── verify_project.sh       # Project verification script
└── verify_prompts.py       # Prompt verification script (Post 3)
```

## 🚀 Quick Start (5 Minutes)

### 1. Verify Prerequisites

```bash
# Run verification script
chmod +x verify_project.sh
./verify_project.sh
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Service

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation!

### 4. Test It

```bash
# Run example client
python examples/test_client.py

# Or use curl
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-12345",
    "note_text": "Patient presents with acute onset headache."
  }'
```

## 🧪 Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## 🐳 Docker Deployment

```bash
# Using docker-compose (easiest)
docker-compose up

# Or build and run manually
docker build -t healthcare-ai-service .
docker run -p 8000:8000 healthcare-ai-service
```

## 📚 Documentation Guide

1. **Start Here**: `README.md` - Project overview and quick start
2. **5-Min Setup**: `docs/QUICKSTART.md` - Get running fast
3. **Understanding It**: `docs/architecture.md` - How it works and why
4. **Contributing**: `CONTRIBUTING.md` - How to contribute
5. **What's Next**: `ROADMAP.md` - Future plans

## 🔑 Core Concepts

### 1. Audit IDs for Traceability

Every request gets a unique UUID that flows through the entire system:

```python
# In app/logging.py
audit_id = uuid.uuid4()  # Generated for each request

# Logged with every operation
logger.info({
    "audit_id": str(audit_id),
    "event": "request_received",
    ...
})
```

### 2. Privacy-Aware Logging

Never log full PHI, only previews:

```python
# Only first 100 characters logged
payload_preview = note_text[:100]
if len(note_text) > 100:
    payload_preview += "..."
```

### 3. Type-Safe Validation

Pydantic models enforce contracts:

```python
class ClinicalNoteRequest(BaseModel):
    patient_id: str = Field(..., min_length=1, max_length=50)
    note_text: str = Field(..., min_length=1, max_length=10000)
```

### 4. Structured Error Handling

Consistent error responses:

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            timestamp=datetime.utcnow()
        ).dict()
    )
```

## 🎓 What You'll Learn

By working through this codebase, you'll understand:

1. **Healthcare Engineering Patterns**
   - Audit trails for compliance
   - Privacy-aware logging
   - Deterministic operations
   - Error handling in critical systems

2. **Production FastAPI**
   - Proper project structure
   - Request/response validation
   - Middleware patterns
   - Error handling
   - Health checks

3. **Testing Healthcare Systems**
   - Comprehensive test coverage
   - Testing validation logic
   - Testing privacy controls
   - Integration tests

4. **Deployment Best Practices**
   - Docker containerization
   - Configuration management
   - Secrets handling
   - Production considerations

## ❓ Common Questions

### Why no AI in Post 1?

This foundation outlives any model. Build it first, add AI second.

### Why so much logging?

Healthcare requires complete traceability. Audit IDs enable debugging production issues months later.

### Why Pydantic models everywhere?

Type safety prevents entire classes of bugs. In healthcare, bugs can have serious consequences.

### Is this HIPAA compliant?

This is a foundation. Full HIPAA compliance requires additional controls (encryption, access controls, BAAs, etc.). See Post 5 in the roadmap.

### Can I use this in production?

This is educational code. For production, add:
- Authentication/authorization
- Database persistence
- Enhanced monitoring
- Security hardening
- Compliance review

## 🛠️ Common Tasks

### Adding a New Endpoint

1. Define models in `app/models.py`
2. Add route in `app/main.py`
3. Add tests in `tests/test_api.py`
4. Update documentation

### Changing Configuration

1. Update `app/config.py`
2. Update `.env.example`
3. Update documentation

### Running in Different Modes

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload

# Production (with workers)
uvicorn app.main:app --workers 4

# Custom port
uvicorn app.main:app --port 8080

# Using Makefile
make run          # Development
make run-prod     # Production
```

## 📊 Project Stats

- **Lines of Code**: ~4,000 (excluding tests and docs)
- **Tests**: 150 comprehensive tests (100% passing)
- **Test Coverage**: >90% on all modules
- **Documentation**: 17+ comprehensive guides
- **Dependencies**: Minimal (FastAPI, Pydantic, Uvicorn, Anthropic, PyYAML)
- **Docker Image**: ~150MB
- **Startup Time**: <1 second

## 🤝 Contributing

We welcome contributions! See `CONTRIBUTING.md` for:
- Development workflow
- Code style guidelines
- Testing requirements
- PR process
- Healthcare-specific considerations

## 📈 What's Next?

This is a **12-post series** building healthcare AI from first principles. Progress so far:

### Completed
- ✅ **Post 1**: Foundation Without AI
- ✅ **Post 2**: Adding LLMs Without Breaking Things
- ✅ **Post 3**: Prompting as Versioned Code
- ✅ **Post 4**: Determinism, Variability, and Why Clinicians Notice
- ✅ **Post 5**: Building Your First Evaluation Harness
- ✅ **Post 6**: Shadow Mode Deployment

### Coming Next
- **Post 7**: Monitoring That Triggers Action
- **Post 8**: Human Feedback Without Burning Clinicians
- **Post 9**: Failure Drills for AI Systems
- **Post 10**: Governance as Code
- **Post 11**: From Service to Platform
- **Post 12**: What This Still Does Not Solve

See `ROADMAP.md` for detailed descriptions of each post.

## 💡 Key Takeaways

1. ✅ **Build the foundation before adding AI**
2. ✅ **Audit trails are non-negotiable in healthcare**
3. ✅ **Privacy controls must be baked in, not bolted on**
4. ✅ **Type safety prevents entire classes of bugs**
5. ✅ **Production patterns outlive any specific model**

## 🆘 Getting Help

- **Questions?** Open an issue
- **Found a bug?** Open an issue with reproduction steps
- **Want to contribute?** See CONTRIBUTING.md
- **Security concern?** Email privately (see CONTRIBUTING.md)

## 📄 License

MIT License - See LICENSE file for details.

Free to use for learning, commercial projects, or anything else.

## 🙏 Acknowledgments

Built for healthcare engineers who want to do AI **right**, not fast.

This codebase demonstrates that production-grade healthcare AI starts with solid engineering fundamentals, not with picking the shiniest model.

---

## 🎯 Final Note

**This is not a tutorial. This is a foundation.**

Everything here is production-grade because healthcare deserves production-grade engineering.

The AI you'll add in Post 2 is powerful, but this foundation is what makes it safe, traceable, and maintainable.

Start here. Build on this. Do healthcare AI right.

---

**Ready to begin?**

```bash
# Verify setup
./verify_project.sh

# Start building
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs and explore!
