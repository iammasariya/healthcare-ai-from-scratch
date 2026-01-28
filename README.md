# Healthcare AI Service - Post 1: Foundation Without AI

A production-grade healthcare clinical text service built without any AI/ML components. This project demonstrates the essential scaffolding every healthcare AI system needs before adding models.

## 🎯 Purpose

This is **Post 1** in a series on building healthcare AI systems from scratch. We intentionally skip the AI to focus on:

- **Auditability**: Every request gets a traceable audit ID
- **Determinism**: Predictable behavior before adding probabilistic models
- **Safety**: Production patterns that survive regulatory scrutiny
- **Extensibility**: A foundation you can build on without rewriting

## 🏗️ What We Built

A minimal clinical text ingestion service that:
- ✅ Accepts clinical notes via REST API
- ✅ Assigns unique audit IDs to every request
- ✅ Logs all operations deterministically
- ✅ Provides structured JSON responses
- ✅ Is ready to extend with AI later

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
│   └── config.py        # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # API endpoint tests
│   └── test_logging.py  # Logging functionality tests
├── examples/
│   └── test_client.py   # Example client usage
├── docs/
│   └── architecture.md  # Architecture decisions
├── .env.example         # Environment variables template
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
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

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "datetime"
}
```

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

- [x] **Post 1**: Foundation without AI (you are here)
- [ ] **Post 2**: Adding LLMs without breaking the foundation
- [ ] **Post 3**: Structured outputs and validation
- [ ] **Post 4**: Handling failures and retries
- [ ] **Post 5**: Privacy, security, and compliance
- [ ] **Post 6**: Monitoring and observability

## 🤝 Contributing

This is an educational project. Feel free to:
- Open issues for questions
- Submit PRs for improvements
- Share your implementations

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built for healthcare engineers who want to do AI right, not fast.
