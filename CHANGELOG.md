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

## [0.3.0] - 2026-02-04

### Added
- **Prompt Management System**: Enterprise-grade prompt versioning
  - `app/prompts.py`: Complete prompt management implementation (280 lines)
  - `prompts/`: Directory for versioned prompt YAML files
  - Semantic versioning support (1.0.0, 1.1.0, 2.0.0)
  - SHA256 integrity verification for tamper detection
  - Lifecycle management (active/deprecated/retired)
  - Hot-reload capability without service restart
- **Versioned Prompts as Code**
  - `prompts/clinical_summarization_v1.0.0.yaml`: Production prompt with governance
  - YAML format with metadata (version, created_at, created_by, status)
  - Template variables for dynamic content
  - Validation rules (max_tokens, temperature)
  - Governance metadata (approvals, regulatory status, testing notes)
- **Audit Trail Enhancement**
  - Prompt version logged with every LLM request
  - Prompt hash logged for integrity verification
  - Complete reproducibility of any output
  - Enhanced `LLMMetrics` model with prompt_version and prompt_hash
- **A/B Testing Infrastructure**
  - Ability to specify prompt version per request
  - Compare different prompt versions in production
  - Version selection via configuration or request parameter
- **Rollback Capability**
  - Change prompt version without code deployment
  - Update YAML status field (active/deprecated)
  - Instant rollback by switching versions
  - No service restart required
- **Testing and Verification**
  - `tests/test_prompts.py`: 16 comprehensive tests for prompt system
  - `verify_prompts.py`: Standalone verification script
  - Tests for versioning, integrity, templates, lifecycle
  - 100% test coverage on prompt management
- **Documentation**
  - `docs/POST_3_LINKEDIN_ARTICLE.md`: Complete article (6,500+ words)
  - `docs/POST_3_SUMMARY.md`: Comprehensive deliverables summary
  - Updated README, ROADMAP, PROJECT_SUMMARY

### Enhanced
- **LLM Service**: Enhanced to use versioned prompts
  - Loads prompts from PromptManager
  - Falls back to legacy hardcoded prompts for backward compatibility
  - Logs prompt version and hash with every call
  - Returns prompt metadata in responses
- **Response Models**: Extended with prompt versioning
  - `LLMResponse` includes prompt_version and prompt_hash
  - `LLMMetrics` tracks prompt metadata
  - Full traceability from request to output
- **Dependencies**: Added prompt management support
  - `pyyaml==6.0.1`: YAML parsing for prompt files
  - Updated `requirements.txt`

### Design Decisions
- **Prompts as Artifacts**: Treat prompts like code, not magic strings
- **Semantic Versioning**: Clear upgrade paths (major.minor.patch)
- **Integrity Verification**: SHA256 hashing prevents tampering
- **Governance Built-In**: Metadata for approvals and regulatory compliance
- **Hot-Reload**: Update prompts without service restart
- **Backward Compatible**: Legacy code continues to work

### Testing
- 16 new tests for prompt management system
- Total test suite: 79 tests (100% passing)
- Covers versioning, integrity, templates, lifecycle, edge cases
- Verification script for quick validation

### Security & Compliance
- SHA256 integrity verification
- Audit trail for every prompt change
- Governance metadata (approvals, testing)
- Regulatory status tracking
- Complete reproducibility

## [Unreleased]

### Planned for Post 4
- Determinism controls and variability measurement
- Temperature tuning experiments
- Output divergence metrics

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

- **0.1.0** - Foundation without AI (Post 1) ✅
- **0.2.0** - LLM integration (Post 2) ✅
- **0.3.0** - Prompt versioning (Post 3) ✅
- **0.4.0** - (Planned) Determinism and variability (Post 4)
- **0.5.0** - (Planned) Evaluation harness (Post 5)
- **0.6.0** - (Planned) Shadow mode deployment (Post 6)
- **0.7.0** - (Planned) Monitoring that triggers action (Post 7)
- **0.8.0** - (Planned) Human feedback loops (Post 8)
- **0.9.0** - (Planned) Failure drills (Post 9)
- **0.10.0** - (Planned) Governance as code (Post 10)
- **0.11.0** - (Planned) From service to platform (Post 11)
- **0.12.0** - (Planned) What this still does not solve (Post 12)
- **1.0.0** - (Planned) Full production release

## Upgrade Notes

### 0.1.0
- Initial release - no upgrades needed

### 0.2.0 → 0.2.0
- New LLM integration with Claude API
- Set `ANTHROPIC_API_KEY` environment variable
- Set `LLM_ENABLED=true` to enable LLM features
- No breaking changes to existing endpoints

### 0.2.0 → 0.3.0
- New prompt management system with versioning
- Install `pyyaml` dependency: `pip install pyyaml==6.0.1`
- Create `prompts/` directory for versioned prompts
- No breaking changes - backward compatible
- Existing LLM calls continue to work with hardcoded prompts
- Optionally migrate to versioned prompts for better governance
---

For details on how to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
