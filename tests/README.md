# Test Suite Documentation

This directory contains the comprehensive test suite for the Healthcare AI Service.

## Test Files

### `test_api.py`
Tests for API endpoints covering both Post 1 and Post 2 functionality.

**Post 1 Tests:**
- Health check endpoint
- Root endpoint
- `/ingest` endpoint validation
- Request/response contracts
- Error handling
- CORS configuration
- Process time middleware

**Post 2 Tests (NEW):**
- `/summarize` endpoint with LLM integration
- Feature flag behavior (LLM_ENABLED)
- Successful summarization with metrics
- LLM failure handling
- Response validation failures
- Missing API key handling
- Unexpected error handling
- Audit trail maintenance
- Long note handling

**Test Count:** 30+ test cases

### `test_llm.py` (NEW - Post 2)
Comprehensive tests for the LLM service layer.

**Coverage:**
- `LLMConfig`: Default and custom configuration
- `LLMResponse`: Response creation and serialization
- `LLMService`: 
  - Service initialization
  - Successful summarization
  - Timeout error handling
  - Rate limit error handling
  - Authentication error handling
  - API error handling
  - Unexpected error handling
  - Response validation (success, empty, too short, incomplete)
  - Cost calculation accuracy
- `get_llm_service`: Singleton pattern

**Test Count:** 20+ test cases

### `test_logging.py`
Tests for the logging system (Post 1).

**Coverage:**
- Audit ID generation
- Privacy-aware logging
- Structured log format
- Request/response logging

## Running Tests

### Prerequisites

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_llm.py -v
pytest tests/test_api.py -v
pytest tests/test_logging.py -v
```

### Run Specific Test Classes

```bash
# Run LLM service tests
pytest tests/test_llm.py::TestLLMService -v

# Run summarize endpoint tests
pytest tests/test_api.py::TestSummarizeEndpoint -v

# Run specific test
pytest tests/test_llm.py::TestLLMService::test_summarize_clinical_note_success -v
```

## Test Coverage Goals

- **Overall**: >80%
- **Core Logic**: >90%
- **API Endpoints**: >85%
- **Post 1**: 100% (achieved)
- **Post 2**: >90% (newly added)

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Use mocks for external dependencies
- Fast execution (<1s per test)

### Integration Tests
- Test API endpoints end-to-end
- Use test client (FastAPI TestClient)
- Mock external services (Anthropic API)

### Test Patterns

#### Mocking LLM Service

```python
from unittest.mock import patch, Mock
from app.llm import LLMResponse

@patch('app.main.get_llm_service')
def test_summarize(mock_get_service):
    mock_service = Mock()
    mock_service.summarize_clinical_note.return_value = (
        LLMResponse(...),
        None
    )
    mock_get_service.return_value = mock_service
    # Test code here
```

#### Testing Error Handling

```python
@patch('app.llm.anthropic.Anthropic')
def test_timeout(mock_anthropic_class):
    mock_client = Mock()
    mock_anthropic_class.return_value = mock_client
    mock_client.messages.create.side_effect = anthropic.APITimeoutError("Timeout")
    # Test code here
```

## Test Data

### Valid Request Fixture

```python
@pytest.fixture
def valid_request():
    return {
        "patient_id": "PT-12345",
        "note_text": "Patient presents with acute onset headache..."
    }
```

### Mock LLM Response

```python
mock_response = LLMResponse(
    content="Clinical summary",
    model="claude-3-5-sonnet-20241022",
    tokens_used=350,
    latency_ms=1250.0,
    cost_usd=0.00525,
    stop_reason="end_turn"
)
```

## Healthcare Testing Considerations

### Privacy
- Never use real PHI in tests
- Use synthetic patient IDs (PT-TEST-XXX)
- Test privacy controls (truncation, masking)

### Audit Trail
- Verify audit IDs are generated
- Verify audit IDs are unique
- Verify audit trail maintained on failure

### Reliability
- Test all error paths
- Test retry logic
- Test timeout handling
- Test rate limit handling

### Cost Tracking
- Test cost calculation accuracy
- Test token usage tracking
- Test metrics reporting

## Continuous Integration

Tests should run on:
- Every commit
- Every pull request
- Before deployment

Example CI configuration:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Test Maintenance

### Adding New Tests

1. Create test class following naming convention
2. Use descriptive test names (test_feature_scenario)
3. Add docstring explaining what's being tested
4. Use fixtures for common setup
5. Mock external dependencies
6. Assert on specific behaviors

### Updating Existing Tests

1. Update tests when API contracts change
2. Update tests when error handling changes
3. Keep tests focused and isolated
4. Maintain test coverage above thresholds

## Troubleshooting

### Import Errors

```bash
# Ensure you're in the project root
cd /path/to/healthcare-ai-from-scratch

# Ensure dependencies are installed
pip install -r requirements-dev.txt
```

### Mock Not Working

```python
# Use correct import path
from unittest.mock import patch

# Patch where the object is used, not where it's defined
@patch('app.main.get_llm_service')  # Used in main.py
def test_something(mock_get_service):
    ...
```

### Test Fails Locally But Passes in CI

- Check environment variables
- Check dependency versions
- Check file paths (use relative paths)
- Check timezone handling

## Post 2 Test Additions Summary

### New Test File
- `tests/test_llm.py`: 20+ tests for LLM service layer

### Updated Test File
- `tests/test_api.py`: Added 12+ tests for `/summarize` endpoint

### Test Coverage
- LLM configuration and initialization
- Successful LLM calls with metrics
- All error scenarios (timeout, rate limit, auth, API)
- Response validation
- Cost calculation
- Graceful degradation
- Audit trail preservation
- Feature flag behavior

### Key Testing Principles Demonstrated

1. **Mock External Dependencies**: Never make real API calls in tests
2. **Test Error Paths**: Every error scenario has a test
3. **Verify Observability**: Test that metrics are tracked
4. **Maintain Audit Trail**: Test that tracing works even on failure
5. **Healthcare Safety**: Test privacy controls and validation

## Next Steps

For Post 3 (Prompt Versioning), add tests for:
- Prompt versioning system
- Prompt template management
- A/B testing infrastructure
- Rollback mechanisms

---

**Note**: These tests use mocking to avoid requiring actual Anthropic API keys or making real API calls. This makes tests fast, deterministic, and suitable for CI/CD.