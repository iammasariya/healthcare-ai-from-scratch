# Quick Start Guide

Get the Healthcare AI Service running in under 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd healthcare-ai-from-scratch

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Run the Service

```bash
# Start the development server
uvicorn app.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

## Step 3: Verify It's Working

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see the interactive API documentation!

## Step 4: Test the API

### Option A: Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click on "POST /ingest"
3. Click "Try it out"
4. Use this example:
   ```json
   {
     "patient_id": "PT-12345",
     "note_text": "Patient presents with acute onset headache. Vital signs stable."
   }
   ```
5. Click "Execute"

### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-12345",
    "note_text": "Patient presents with acute onset headache. Vital signs stable."
  }'
```

### Option C: Using the Example Client

```bash
python examples/test_client.py
```

## Expected Response

You should get a response like:

```json
{
  "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "received_at": "2026-01-27T10:30:45.123456Z",
  "status": "received",
  "patient_id": "PT-12345"
}
```

## Step 5: Run Tests (Optional)

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## What You Just Built

You now have a production-grade healthcare service that:

✅ Validates clinical note inputs  
✅ Assigns unique audit IDs  
✅ Logs all operations (with privacy controls)  
✅ Returns structured responses  
✅ Provides interactive API documentation  
✅ Is ready to extend with AI  

## Common Issues

### Port Already in Use

If you see "Address already in use" error:

```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Module Not Found

If you see "ModuleNotFoundError":

```bash
# Make sure you're in the project root
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Python Version Too Old

If you see version errors:

```bash
# Check Python version
python --version

# Should be 3.9 or higher
# If not, install a newer Python version
```

## Next Steps

1. **Explore the code**: Start with `app/main.py` and `app/models.py`
2. **Read the architecture**: See `docs/architecture.md`
3. **Run the tests**: `pytest -v`
4. **Modify and experiment**: The foundation is yours to build on

## Development Tips

### Auto-reload is your friend
When running with `--reload`, the server automatically restarts when you change code. This makes development fast.

### Use the interactive docs
http://localhost:8000/docs is invaluable for testing and understanding the API.

### Check the logs
The service logs all operations. Watch the terminal to see audit IDs and events.

### Start simple
Don't add AI yet. Understand this foundation first. Post 2 will add LLMs.

## Docker Deployment (Optional)

If you prefer Docker:

```bash
# Build and run with Docker Compose
docker-compose up

# Or build manually
docker build -t healthcare-ai-service .
docker run -p 8000:8000 healthcare-ai-service
```

## Getting Help

- **Code issues**: Check the tests in `tests/`
- **API questions**: See the interactive docs at `/docs`
- **Architecture**: Read `docs/architecture.md`
- **Configuration**: Check `.env.example`

## What Makes This Production-Grade?

Unlike tutorial code, this includes:

- ✅ Comprehensive error handling
- ✅ Input validation
- ✅ Structured logging
- ✅ Health checks
- ✅ Full test coverage
- ✅ Docker support
- ✅ Security considerations
- ✅ Privacy controls
- ✅ Documentation

This is what real healthcare systems need before adding AI.

---

**You're ready!** You've built a foundation that outlives any model you'll add later.

Next: Post 2 will show how to add LLMs without breaking this structure.
