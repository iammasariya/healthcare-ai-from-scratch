# Healthcare AI Service - From First Principles

A production-grade healthcare AI system built from first principles. This project demonstrates building healthcare AI the right way: foundation first, models second, prompt versioning third, variability control fourth.

## 🎯 Purpose

This is a series on building healthcare AI systems from scratch, starting with the foundation.

**Post 1: Foundation Without AI** - Build the system before the model  
**Post 2: Adding LLMs Safely** - Integrate Claude without breaking the foundation  
**Post 3: Prompting as Versioned Code** - Treat prompts as first-class artifacts  
**Post 4: Variability Control** - Measure and control model consistency  
**Post 5: Evaluation Harness** - Systematic model evaluation and regression detection
**Post 6: Shadow Mode** - Safe model rollout with dual-path execution and HAPI FHIR (current)

We focus on:
- **Auditability**: Every request gets a traceable audit ID
- **Determinism**: Predictable behavior before adding probabilistic models  
- **Safety**: Production patterns that survive regulatory scrutiny
- **Extensibility**: A foundation you can build on without rewriting
- **Reliability**: LLMs with timeouts, retries, and graceful failures
- **Observability**: Cost tracking and latency monitoring
- **Reproducibility**: Versioned prompts with integrity verification

## 🏗️ What We Built

### Post 1: Foundation
A minimal clinical text ingestion service that:
- ✅ Accepts clinical notes via REST API
- ✅ Assigns unique audit IDs to every request
- ✅ Logs all operations deterministically
- ✅ Provides structured JSON responses

### Post 2: LLM Integration
Added Claude-powered clinical note summarization:
- ✅ `/summarize` endpoint with LLM integration
- ✅ Automatic retries with exponential backoff
- ✅ Cost tracking per request (in USD)
- ✅ Latency monitoring
- ✅ Response validation
- ✅ Feature flag for safe rollout
- ✅ Graceful failure handling

### Post 3: Prompt Versioning
Treat prompts as versioned artifacts:
- ✅ Prompts stored in YAML files with semantic versioning
- ✅ SHA256 integrity verification
- ✅ Prompt version and hash logged with every request
- ✅ Hot-reload without service restart
- ✅ A/B testing infrastructure
- ✅ Rollback capability without code deployment
- ✅ Governance metadata (approvals, testing notes)
- ✅ 16 comprehensive tests for prompt management

### Post 4: Variability Control
Measure and control model output variability:
- ✅ Variability measurement system with comprehensive metrics
- ✅ Semantic similarity comparison using difflib
- ✅ Deterministic seed generation from context
- ✅ Temperature recommendation framework by task/risk
- ✅ Variability alerting for production monitoring
- ✅ Acceptability thresholds for clinical use
- ✅ 34 comprehensive tests for variability measurement

**Key Insights:**
- Temperature 0.0: Perfect consistency (100% exact match)
- Temperature 0.3: High consistency (~95% similarity)
- Temperature 0.7: Significant variability (~60% similarity)
- Clinicians notice inconsistency - measure and control it

### Post 5: Evaluation Harness (Current)
Systematic model evaluation and regression detection:
- ✅ Golden dataset management (JSON-based, version-controlled)
- ✅ Evaluation framework with exact and fuzzy matching
- ✅ Regression detection with automated alerts
- ✅ Model version comparison
- ✅ CI/CD integration (JSON output)
- ✅ MedHELM / HELM integration (optional)
- ✅ 26 comprehensive tests for evaluation system

**Key Capabilities:**
- Answer "Is model v2 better than v1?" with data
- Automated regression detection gates deployments
- Evaluation as code, not notebooks
- Optional MedHELM / HELM integration for research-grade metrics

### Post 6: Shadow Mode Deployment (Current)
Safe rollout foundations for candidate models:
- ✅ Shadow-mode comparison service for production vs candidate outputs
- ✅ Divergence scoring built on the Post 5 evaluator
- ✅ Gradual rollout recommendations from recent shadow runs
- ✅ HAPI FHIR bundle support for realistic clinical context
- ✅ `/shadow/summarize` endpoint for dual-path execution
- ✅ 5 shadow-mode tests plus API coverage

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip
- Virtual environment tool (venv)

### Installation

```bash
# Clone the repository
git clone https://github.com/iammasariya/healthcare-ai-from-scratch.git
cd healthcare-ai-from-scratch

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Service

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Test the API

```bash
# Using curl
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-12345",
    "note_text": "Patient presents with acute onset headache. Vital signs stable."
  }'

# Using Python
python examples/test_client.py

# Using the test suite
pytest tests/
```

## 📁 Project Structure

```
healthcare-ai-from-scratch/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # Pydantic models for request/response
│   ├── logging.py       # Structured logging with audit IDs
│   ├── config.py        # Configuration management
│   ├── llm.py           # LLM service with retry logic (Post 2)
│   ├── llm_litellm.py   # Alternative LiteLLM implementation (Post 2)
│   ├── prompts.py       # Prompt management system (Post 3)
│   ├── variability.py   # Variability measurement (Post 4)
│   ├── evaluation.py    # Evaluation harness (Post 5)
│   ├── shadow.py        # Shadow mode utilities (Post 6 foundation)
│   └── helm_adapter.py  # MedHELM / HELM integration (Post 5, optional)
├── prompts/             # Versioned prompt files (Post 3)
│   └── clinical_summarization_v1.0.0.yaml
├── evaluation_datasets/ # Golden datasets (Post 5)
│   └── clinical_summarization_golden.json
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # API endpoint tests
│   ├── test_logging.py  # Logging functionality tests
│   ├── test_llm.py      # LLM service tests (Post 2)
│   ├── test_prompts.py  # Prompt management tests (Post 3)
│   ├── test_variability.py  # Variability tests (Post 4)
│   ├── test_evaluation.py   # Evaluation tests (Post 5)
│   └── test_shadow.py       # Shadow mode tests (Post 6 foundation)
├── examples/
│   ├── test_client.py       # Example client usage
│   ├── test_summarize.py    # LLM summarization example (Post 2)
│   ├── test_prompts.py      # Prompt versioning example (Post 3)
│   ├── test_variability.py  # Variability measurement example (Post 4)
│   ├── test_evaluation.py   # Evaluation demo (Post 5)
│   ├── test_shadow_mode.py  # Shadow mode demo with HAPI FHIR (Post 6 foundation)
│   ├── test_shadow_hapi_server.py  # Live HAPI FHIR demo (Post 6)
│   └── helm_evaluation_example.py  # Hybrid evaluation (Post 5)
├── scripts/
│   ├── compare_evaluators.py  # Compare built-in vs MedHELM / HELM (Post 5)
│   └── shadow_rollout_report.py  # Summarize saved shadow runs (Post 6)
├── docs/
│   ├── QUICKSTART.md
│   └── architecture.md
├── .env.example         # Environment variables template
├── .gitignore
├── .coveragerc
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── CHANGELOG.md
├── ROADMAP.md
├── PROJECT_SUMMARY.md
├── INDEX.md
├── LICENSE
├── verify_project.sh    # Project verification script
├── verify_prompts.py    # Prompt verification script (Post 3)
└── README.md
```

## 🔍 API Reference

### POST /ingest

Ingest a clinical note for processing.

**Request Body:**
```json
{
  "patient_id": "string",
  "note_text": "string"
}
```

**Response:**
```json
{
  "audit_id": "uuid",
  "received_at": "datetime",
  "status": "string"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-12345",
    "note_text": "Patient presents with acute onset headache."
  }'
```

### POST /summarize (Post 2: LLM Integration)

Summarize a clinical note using Claude LLM.

**Requirements:**
- Set `ANTHROPIC_API_KEY` environment variable
- Set `LLM_ENABLED=true` environment variable

**Request Body:**
```json
{
  "patient_id": "string",
  "note_text": "string"
}
```

**Response:**
```json
{
  "audit_id": "uuid",
  "received_at": "datetime",
  "status": "completed|failed",
  "patient_id": "string",
  "summary": "string (if successful)",
  "llm_metrics": {
    "model": "string",
    "tokens_used": "integer",
    "latency_ms": "float",
    "cost_usd": "float"
  },
  "error": "string (if failed)"
}
```

**Example:**
```bash
# Set up environment
export ANTHROPIC_API_KEY="your-key-here"
export LLM_ENABLED=true

# Make request
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-12345",
    "note_text": "Patient presents with acute onset headache. Denies trauma. Vital signs: BP 120/80, HR 72, Temp 98.6F. Neurological exam normal. Assessment: Tension headache. Plan: Acetaminophen 500mg PO PRN."
  }'

# Or use the example client
python examples/test_summarize.py
```

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "datetime"
}
```

### POST /shadow/summarize (Post 6: Shadow Mode)

Run production and candidate summarization paths side by side.

Supports:
- direct `note_text`
- inline HAPI FHIR `Bundle` payloads
- HAPI FHIR server fetch via `hapi_fhir_base_url`

**Request Body Example:**
```json
{
  "patient_id": "patient-101",
  "source_system": "hapi-fhir-r4",
  "fhir_bundle": {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": []
  }
}
```

**Response Highlights:**
- production summary
- shadow summary
- similarity score
- alert severity
- rollout recommendation

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

## 📘 Learn The System

- `README.md` - product overview, API surface, and how the pieces fit together
- `docs/QUICKSTART.md` - setup and first run
- `docs/architecture.md` - architecture and design decisions
- `examples/test_evaluation.py` - runnable Post 5 demonstration with regression detection
- `examples/test_shadow_mode.py` - runnable Post 6 shadow-mode example using HAPI FHIR-style resources
- `examples/test_shadow_hapi_server.py` - live HAPI FHIR fetch example for Post 6

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t healthcare-ai-service:latest .

# Run the container
docker run -p 8000:8000 healthcare-ai-service:latest

# Using docker-compose
docker-compose up
```

## 📊 Logging

All requests are logged with structured JSON including:
- `audit_id`: Unique identifier for request tracing
- `event`: Event type (e.g., "request_received")
- `timestamp`: ISO 8601 timestamp
- `payload_preview`: First 100 characters of clinical text

Example log entry:
```json
{
  "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event": "request_received",
  "timestamp": "2026-01-27T10:30:45.123Z",
  "payload_preview": "Patient presents with acute onset headache. Vital signs stable. Blood pressure 120/80..."
}
```

## 🔒 Security Considerations

- **No PHI in logs**: Only preview first 100 chars, never full patient data
- **Audit trail**: Every request is traceable via audit_id
- **Input validation**: Pydantic models enforce type safety
- **CORS**: Configure appropriately for production
- **HTTPS**: Use reverse proxy (nginx/traefik) in production

## 🏥 Healthcare Reality Check

This foundation matters because:

1. **Regulators care about this layer**: Before they ask about your model's accuracy, they'll ask how you trace requests
2. **This outlives your models**: You'll swap models, but this interface stays stable
3. **Debugging starts here**: When something goes wrong 6 months later, this is where you begin
4. **Auditability > Intelligence**: In healthcare, explainability trumps performance

## 📚 What to Internalize

Before moving to Post 2 (adding LLMs), understand:

- ✅ AI is a dependency, not the system
- ✅ Interfaces matter more than models
- ✅ Traceability is a prerequisite for trust
- ✅ Production systems need structure before intelligence

## 🛣️ Roadmap

### Completed
- [x] **Post 1**: Foundation Without AI
- [x] **Post 2**: Adding LLMs Without Breaking Things
- [x] **Post 3**: Prompting as Versioned Code
- [x] **Post 4**: Determinism, Variability, and Why Clinicians Notice
- [x] **Post 5**: Building Your First Evaluation Harness
- [x] **Post 6**: Shadow Mode Deployment (current)

### Planned
- [ ] **Post 7**: Monitoring That Triggers Action
- [ ] **Post 8**: Human Feedback Without Burning Clinicians
- [ ] **Post 9**: Failure Drills for AI Systems
- [ ] **Post 10**: Governance as Code
- [ ] **Post 11**: From Service to Platform
- [ ] **Post 12**: What This Still Does Not Solve

See [ROADMAP.md](ROADMAP.md) for detailed information on each post.

## 🤝 Contributing

This is an educational project. Feel free to:
- Open issues for questions
- Submit PRs for improvements
- Share your implementations

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built for healthcare engineers who want to do AI right, not fast.

## Disclaimer

This work represents independent professional experience and is not affiliated with any prior employer or specific institutional project.
