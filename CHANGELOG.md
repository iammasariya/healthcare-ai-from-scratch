# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-27

### Added
- Initial release of Healthcare AI Service foundation
- FastAPI application with `/ingest` endpoint for clinical notes
- Unique audit ID generation for every request (UUID4)
- Privacy-aware structured logging (JSON format)
- Pydantic models for type-safe request/response validation
- Health check endpoint (`/health`) for monitoring
- Comprehensive test suite with pytest
- Docker support with Dockerfile and docker-compose
- Full API documentation (auto-generated via FastAPI)
- Configuration management via pydantic-settings
- CORS middleware for frontend integration
- Request timing middleware
- Global error handling
- Examples of client usage
- Extensive documentation:
  - README with quick start
  - Architecture documentation
  - Deployment guide
  - Contributing guidelines
  - Quick start guide

### Design Decisions
- **No AI/ML components**: Intentionally building foundation first
- **Audit ID for every request**: Required for healthcare traceability
- **Privacy controls**: Only log preview of clinical text (100 chars)
- **Deterministic operations**: Predictable behavior before adding probabilistic AI
- **Structured logging**: JSON format for log aggregation
- **Type safety**: Pydantic models throughout
- **Production patterns**: Health checks, monitoring, error handling

### Security Features
- Input validation via Pydantic
- No PHI in logs (truncation)
- Configurable CORS
- Non-root Docker user
- Environment-based configuration

### Testing
- 100% test coverage on core functionality
- Unit tests for logging
- Integration tests for API endpoints
- Test fixtures for reusability

### Documentation
- Inline code documentation
- API examples
- Deployment instructions
- Architecture decisions
- Healthcare considerations

## [0.2.0] - 2026-02-03

### Added
- **LLM Integration**: Full Claude API integration with production-grade reliability
  - `app/llm.py`: Core LLM service with retry logic and error handling
  - `app/llm_litellm.py`: Alternative LiteLLM implementation for multi-provider support
  - Automatic retries with exponential backoff
  - Configurable timeouts (default 30s)
  - Comprehensive error handling (timeout, rate limit, auth, API errors)
- **New `/summarize` Endpoint**: Clinical note summarization using Claude
  - Validates input with Pydantic models
  - Full audit trail with unique IDs
  - Graceful failure handling with detailed error messages
  - Feature flag support via `LLM_ENABLED` environment variable
- **Cost and Latency Tracking**
  - Real-time token usage tracking (input + output)
  - Automatic cost calculation based on Claude pricing
  - Latency monitoring in milliseconds
  - Structured metrics in `LLMMetrics` model
- **Response Validation**
  - Validates response completeness
  - Checks for minimum quality criteria
  - Verifies stop reason (end_turn vs max_tokens)
  - Extensible validation framework
- **New Pydantic Models**
  - `SummarizeNoteResponse`: Response model with summary and metrics
  - `LLMMetrics`: Structured metrics for observability
  - Enhanced error responses with LLM context
- **Configuration Management**
  - New `LLM_ENABLED` feature flag
  - `ANTHROPIC_API_KEY` support
  - `LITELLM_MODEL` configuration for alternative providers
  - Updated `app/config.py` with LLM settings
- **Testing and Examples**
  - `tests/test_llm.py`: Comprehensive LLM service tests (Post 2)
  - `tests/test_api.py`: Updated with /summarize endpoint tests
  - `examples/test_summarize.py`: Comprehensive testing script
  - Example prompts and expected outputs
  - Cost estimation examples
  - Test coverage for error handling, retries, validation
- **Documentation Updates**
  - Updated README with LLM integration guide
  - API usage examples for `/summarize` endpoint
  - Environment variable documentation
  - Cost and performance guidelines

### Enhanced
- **Error Handling**: Extended to handle LLM-specific errors
  - `LLMTimeoutError`, `LLMRateLimitError`, `LLMAuthenticationError`
  - Structured error responses with audit trail
- **Logging**: Enhanced with LLM metrics
  - Token usage logging
  - Cost tracking per request
  - Latency monitoring
  - Success/failure metrics
- **Dependencies**: Added LLM client libraries
  - `anthropic>=0.39.0`: Official Claude SDK
  - `litellm>=1.0.0`: Multi-provider LLM gateway
  - Updated `requirements.txt`

### Design Decisions
- **Synchronous LLM Calls**: Easier to reason about failures in healthcare context
- **Explicit Timeouts**: Never wait forever (30s default)
- **Cost Awareness**: Track every API call's cost for budget management
- **Graceful Degradation**: Return errors, don't crash the service
- **Audit Everything**: Full traceability for every LLM interaction
- **Feature Flags**: Enable/disable LLM without code changes

### Security Considerations
- API keys via environment variables only
- No PHI in LLM prompts (summary only)
- Audit trail for all LLM calls
- Timeout protection against hanging requests
- Rate limit handling

## [Unreleased]

### Planned for Post 3
- Structured outputs with validation
- Prompt versioning and management
- Advanced fallback strategies
- A/B testing framework

### Future Enhancements
- Database integration for persistence
- Asynchronous processing queue
- Batch processing endpoint
- Advanced monitoring (Prometheus metrics)
- Rate limiting
- API authentication
- Structured outputs with validation
- FHIR compatibility

---

## Version History

- **0.1.0** - Foundation without AI (Post 1)
- **0.2.0** - LLM integration (Post 2)
- **0.3.0** - (Planned) Structured outputs
- **0.4.0** - (Planned) Production hardening
- **1.0.0** - (Planned) Full production release

## Upgrade Notes

### 0.1.0
- Initial release - no upgrades needed
### 0.2.0
- LLM integration
---

For details on how to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
