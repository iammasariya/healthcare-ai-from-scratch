# Healthcare AI Service - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- **Python 3.9+** - Check with `python3 --version`
- **pip** - Package installer for Python
- **Git** - For cloning the repository
- **(Optional) Anthropic API Key** - For LLM features

## Option 1: Automated Setup (Recommended)

We provide an automated setup script that handles everything:

```bash
# Clone the repository
git clone https://github.com/iammasariya/healthcare-ai-from-scratch.git
cd healthcare-ai-from-scratch

# Run setup script
chmod +x setup.sh
./setup.sh
```

The script will:
- ✓ Check Python version
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Create .env file
- ✓ Run tests to verify
- ✓ Verify prompt system

**That's it!** Skip to the "Start the Service" section below.

## Option 2: Manual Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/iammasariya/healthcare-ai-from-scratch.git
cd healthcare-ai-from-scratch
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env (optional for basic testing)
# nano .env  # or use your preferred editor
```

### 5. Verify Installation

```bash
# Run test suite
python -m pytest tests/ -v

# Verify prompts
python verify_prompts.py
```

## Start the Service

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the development server
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Explore the API

### 1. Interactive Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Try the Basic Endpoint

**Using curl:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-12345",
    "note_text": "Patient presents with acute onset headache. Vital signs stable."
  }'
```

**Expected Response:**
```json
{
  "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "received_at": "2026-02-04T16:30:00.123456",
  "status": "received",
  "patient_id": "PT-12345"
}
```

### 3. Run Example Scripts

```bash
# Test basic ingestion (no API key needed)
python examples/test_client.py

# Test prompt versioning (Post 3, no API key needed)
python examples/test_prompts.py

# Test LLM summarization (Post 2, requires API key)
export ANTHROPIC_API_KEY="your-key-here"
python examples/test_summarize.py
```

## Enable LLM Features (Optional)

To use the `/summarize` endpoint with Claude:

### 1. Get API Key

1. Sign up at https://console.anthropic.com/
2. Navigate to API Keys
3. Create a new API key
4. Copy the key (starts with `sk-ant-`)

### 2. Configure

Edit `.env` file:
```bash
# Set your API key
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Enable LLM features
LLM_ENABLED=true
```

### 3. Test LLM Endpoint

```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-12345",
    "note_text": "Patient presents with acute onset headache. Denies trauma. Vital signs: BP 120/80, HR 72, Temp 98.6F. Neurological exam normal. Assessment: Tension headache. Plan: Acetaminophen 500mg PO PRN."
  }'
```

**Expected Response:**
```json
{
  "audit_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "received_at": "2026-02-04T16:35:00.123456",
  "status": "completed",
  "patient_id": "PT-12345",
  "summary": "Patient with tension headache, treated with acetaminophen...",
  "llm_metrics": {
    "model": "claude-3-5-sonnet-20241022",
    "tokens_used": 145,
    "latency_ms": 892.5,
    "cost_usd": 0.00435,
    "prompt_version": "1.0.0",
    "prompt_hash": "86b5034ea5aae0ac..."
  },
  "error": null
}
```

## Explore Prompt Versioning (Post 3)

### View Current Prompts

```bash
# List prompt files
ls -la prompts/

# View prompt details
python examples/test_prompts.py
```

### Create New Prompt Version

```bash
# 1. Copy existing prompt
cp prompts/clinical_summarization_v1.0.0.yaml \
   prompts/clinical_summarization_v1.1.0.yaml

# 2. Edit the new version
# Update: version, description, prompts, metadata
nano prompts/clinical_summarization_v1.1.0.yaml

# 3. Verify new version loads
python verify_prompts.py

# 4. No restart needed! New version is live
```

### Use Specific Prompt Version

The LLM service automatically uses the latest active version, but you can specify a version in your code:

```python
from app.llm import get_llm_service

llm = get_llm_service()
response, error = llm.summarize_clinical_note(
    note_text="...",
    audit_id="...",
    prompt_version="1.0.0"  # Use specific version
)
```

## Common Tasks

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_prompts.py

# With coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Check Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type check
mypy app/
```

### View Logs

The application logs to stdout in JSON format. Each log entry includes:
- `audit_id` - Unique request identifier
- `timestamp` - ISO 8601 timestamp
- `event` - Event type
- `payload_preview` - First 100 chars (privacy-aware)

### Stop the Service

Press `Ctrl+C` in the terminal running uvicorn.

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Failing

```bash
# Check Python version (need 3.9+)
python3 --version

# Reinstall dev dependencies
pip install -r requirements-dev.txt

# Run specific failing test for details
pytest tests/test_prompts.py::TestPromptManager::test_load_single_prompt -v
```

### LLM Endpoint Returns 503

This means LLM features are disabled. Check:

1. `.env` has `LLM_ENABLED=true`
2. `ANTHROPIC_API_KEY` is set correctly
3. Restart the service after changing `.env`

### Prompt Not Found

```bash
# Verify prompts directory exists
ls -la prompts/

# Check prompt file exists
ls -la prompts/clinical_summarization_v1.0.0.yaml

# Verify prompt loads
python verify_prompts.py
```

## Next Steps

### Learn More

1. **Architecture**: Read `docs/architecture.md`
2. **Post 1 Article**: Read `docs/POST_1_LINKEDIN_ARTICLE.md`
3. **Post 2 Article**: Read `docs/POST_2_LINKEDIN_ARTICLE.md`
4. **Post 3 Article**: Read `docs/POST_3_LINKEDIN_ARTICLE.md`
5. **Full Roadmap**: Read `ROADMAP.md`

### Try Advanced Features

1. **Create Custom Prompts**: Add new prompt files for different tasks
2. **A/B Test Prompts**: Run multiple versions and compare results
3. **Monitor Costs**: Track LLM costs per request
4. **Deploy**: See `docs/DEPLOYMENT.md` for production deployment

### Contribute

See `CONTRIBUTING.md` for contribution guidelines.

## Getting Help

- **Documentation**: Check `docs/` directory
- **Examples**: See `examples/` directory  
- **Issues**: Open a GitHub issue
- **Tests**: Look at test files for usage examples

## Summary of Endpoints

| Endpoint | Method | Purpose | Requires API Key |
|----------|--------|---------|------------------|
| `/` | GET | Service info | No |
| `/health` | GET | Health check | No |
| `/docs` | GET | API documentation | No |
| `/ingest` | POST | Ingest clinical note | No |
| `/summarize` | POST | Summarize with LLM | Yes |
| `/metrics` | GET | Basic metrics | No |

## What You've Built

After completing this quickstart, you have:

✅ **Post 1**: Foundation with audit trails and logging  
✅ **Post 2**: LLM integration with cost tracking  
✅ **Post 3**: Prompt versioning with governance  

**Next**: Post 4 - Determinism and Variability

---

**Questions?** Check `INDEX.md` for navigation help or open an issue.

**Ready for production?** See `docs/DEPLOYMENT.md` for deployment guide.