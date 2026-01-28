# Contributing to Healthcare AI Service

Thank you for your interest in contributing! This project aims to demonstrate production-grade healthcare AI engineering practices.

## Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/healthcare-ai-from-scratch.git
   cd healthcare-ai-from-scratch
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. **Run tests to verify setup**
   ```bash
   pytest
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clear, self-documenting code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test
pytest tests/test_api.py::TestIngestEndpoint::test_ingest_valid_request
```

### 4. Format Code

```bash
# Format with black
black app tests examples

# Sort imports
isort app tests examples

# Check linting
flake8 app tests
```

Or use the Makefile:
```bash
make format
make lint
```

### 5. Commit Changes

Follow conventional commits:

```bash
git add .
git commit -m "feat: add new endpoint for batch processing"
# or
git commit -m "fix: correct audit ID generation bug"
# or
git commit -m "docs: update deployment guide"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style Guidelines

### Python Style

We follow PEP 8 with these specifics:

- **Line length**: 100 characters (not 79)
- **Quotes**: Double quotes for strings
- **Imports**: Sorted with isort
- **Formatting**: Automated with black

### Type Hints

Use type hints for all function signatures:

```python
from typing import Optional, Dict, Any

def process_note(note: str, patient_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a clinical note."""
    ...
```

### Documentation

#### Docstrings

Use Google-style docstrings:

```python
def ingest_note(request: ClinicalNoteRequest) -> ClinicalNoteResponse:
    """
    Ingest a clinical note for processing.
    
    Args:
        request: ClinicalNoteRequest containing patient_id and note_text
        
    Returns:
        ClinicalNoteResponse with audit_id, timestamp, and status
        
    Raises:
        HTTPException: If validation fails
    """
    ...
```

#### Comments

- Write code that explains itself
- Use comments for complex logic or healthcare-specific requirements
- Explain *why*, not *what*

```python
# GOOD
# HIPAA requires audit IDs for all PHI access
audit_id = generate_audit_id()

# BAD
# Generate an ID
audit_id = generate_audit_id()
```

## Testing Guidelines

### Test Structure

```python
class TestFeatureName:
    """Tests for specific feature."""
    
    def test_happy_path(self):
        """Test the expected successful case."""
        ...
    
    def test_edge_case(self):
        """Test boundary conditions."""
        ...
    
    def test_error_handling(self):
        """Test error scenarios."""
        ...
```

### Test Coverage

- Aim for >80% coverage overall
- Critical paths (API endpoints, logging) should be >90%
- Write tests before fixing bugs (TDD encouraged)

### Test Data

Use fixtures for test data:

```python
@pytest.fixture
def sample_clinical_note():
    return {
        "patient_id": "PT-TEST-001",
        "note_text": "Test clinical note content"
    }
```

## Healthcare-Specific Considerations

### HIPAA Compliance

When working with healthcare data:

1. **Never log PHI**: Use payload preview, not full content
2. **Audit everything**: All operations must be traceable
3. **Validate inputs**: Prevent injection attacks
4. **Encrypt sensitive data**: At rest and in transit

### Privacy by Design

- Default to privacy-preserving approaches
- Minimize data collection
- Implement access controls
- Document data handling

### Example

```python
# GOOD - Privacy-aware
logger.info({
    "event": "note_received",
    "preview": note_text[:100],  # Only preview
    "length": len(note_text)
})

# BAD - Logs PHI
logger.info({
    "event": "note_received",
    "full_text": note_text  # Don't do this!
})
```

## PR Review Process

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black, isort)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] No sensitive data in commits
- [ ] Commit messages follow conventions

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted
- [ ] CHANGELOG updated
```

### Review Criteria

Reviewers will check:

1. **Code Quality**: Clear, maintainable, follows style guide
2. **Tests**: Adequate coverage, meaningful assertions
3. **Documentation**: Updated and accurate
4. **Security**: No vulnerabilities introduced
5. **Healthcare**: HIPAA considerations addressed

## Project Structure

When adding new code:

```
app/
├── main.py           # FastAPI app and routes
├── models.py         # Pydantic models
├── logging.py        # Logging utilities
├── config.py         # Configuration
└── [new module].py   # Your new module

tests/
├── test_api.py       # API tests
├── test_logging.py   # Logging tests
└── test_[new].py     # Tests for new module
```

## Common Tasks

### Adding a New Endpoint

1. Define Pydantic models in `app/models.py`
2. Add route in `app/main.py`
3. Add logging with audit IDs
4. Write comprehensive tests
5. Update API documentation

Example:

```python
# app/models.py
class NewRequest(BaseModel):
    field: str

class NewResponse(BaseModel):
    result: str
    audit_id: UUID

# app/main.py
@app.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(request: NewRequest) -> NewResponse:
    audit_id = log_request(request.dict())
    # Process request
    return NewResponse(result="success", audit_id=audit_id)

# tests/test_api.py
def test_new_endpoint(client):
    response = client.post("/new-endpoint", json={"field": "value"})
    assert response.status_code == 200
```

### Adding a New Configuration Option

1. Add to `app/config.py`
2. Add to `.env.example`
3. Document in README
4. Add default value

```python
# app/config.py
class Settings(BaseSettings):
    new_option: str = "default_value"
```

## Documentation

### Update These When Changing Features

- `README.md`: Main documentation
- `docs/QUICKSTART.md`: If setup changes
- `docs/DEPLOYMENT.md`: If deployment changes
- `docs/architecture.md`: If architecture changes
- API docstrings: Always update
- Inline comments: For complex logic

### Generating API Docs

API docs are auto-generated by FastAPI at `/docs` and `/redoc`.

Update them by:
- Writing clear docstrings
- Using Pydantic model descriptions
- Adding examples to models

## Questions or Issues?

- **Bugs**: Open an issue with reproducible example
- **Features**: Open an issue for discussion first
- **Questions**: Use discussions or open an issue
- **Security**: Email privately (don't open public issue)

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Remember: this is healthcare software
- When in doubt, prioritize safety and compliance

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping build better healthcare AI systems!
