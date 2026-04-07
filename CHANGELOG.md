# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] - 2026-04-07

### Added
- Workflow-first production UI navigation for completed platform capabilities:
  - `/command-center`, `/patient-workspace`, `/quality-evaluation`, `/rollout-monitoring`, `/feedback-review`
- Control-plane backend and UI modules:
  - `GET /audits/search`
  - `GET/POST /incidents`, `POST /incidents/sync-monitoring`, `POST /incidents/{incident_id}/resolve`
  - Audit Explorer and Incident Workspace pages
- Release gate and command-center workflow wiring in UI
- SMART on FHIR hardening updates:
  - SMART launch route improvements for launch/callback context
  - iframe embed mode via `?embed=1`
- End-to-end UI smoke suite using Playwright (`ui/e2e/workflows.spec.ts`)
- Production deployment bundle for full platform runtime:
  - `ui/Dockerfile`
  - `ui/nginx.conf.template` with configurable `FRAME_ANCESTORS`
  - `docker-compose.yml` updated to run API + UI

### Changed
- Backend version updated to `0.8.1`
- Overview and app shell shifted from tutorial-only navigation to workflow-centered operations UX
- README/ROADMAP/QUICKSTART/UI docs updated for one-command full-stack deployment and SMART embedding guidance

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

## [0.4.0] - 2026-02-06

### Added
- **Variability Measurement System**: Production-grade variability monitoring (Post 4)
  - `app/variability.py`: Complete variability measurement and control implementation (450+ lines)
  - Comprehensive metrics for model output consistency
  - Semantic similarity comparison using difflib
  - Pairwise similarity scoring between outputs
  - Exact match rate and unique output counting
- **Determinism Controls**
  - Context-aware deterministic seed generation (patient ID + version + date)
  - Temperature recommendation framework by task type and risk level
  - Guidelines for extraction, summary, generation, and research tasks
- **Variability Alerting**
  - Alert detection for concerning divergence
  - Acceptability thresholds for clinical use
  - Configurable similarity and uniqueness limits
- **Output Analysis Tools**
  - Output hashing for duplicate detection (SHA256)
  - Length statistics (mean, standard deviation)
  - Comprehensive test suite (34 tests)
- **Testing and Examples**
  - `tests/test_variability.py`: 34 comprehensive tests for variability system
  - `examples/test_variability.py`: Interactive demonstrations of all concepts
  - Test coverage for similarity, seeds, temperature, alerts, edge cases

### Enhanced
- **Test Suite**: Expanded to 113 total tests (79 + 34 new)
  - Post 1: 27 tests
  - Post 2: 36 tests
  - Post 3: 16 tests
  - Post 4: 34 tests
- **Documentation**: Updated with Post 4 implementation details

### Design Decisions
- **Semantic Similarity**: Use difflib for simplicity (no heavy dependencies)
  - Production systems may use sentence-transformers or BERT score
  - Character-level matching effective for detecting major differences
- **Deterministic Seeds**: Context-aware but reproducible
  - Same patient + version + date = same seed
  - Different contexts = different seeds for variety
- **Temperature Matrix**: Task-type + risk-level recommendations
  - Extraction/high-risk: 0.0 (maximum determinism)
  - Summary/high-risk: 0.2 (high consistency)
  - Generation/balanced: 0.3-0.5
  - Research/low-risk: 0.7-0.8 (creative)
- **Acceptability Thresholds**: Clinical context determines tolerance
  - ICD extraction: 0% variability acceptable
  - Clinical summaries: <10% variability acceptable
  - Differential diagnosis: <30% variability acceptable

### Testing
- 34 new tests for variability measurement
- Total test suite: 113 tests (100% passing)
- Covers metrics, similarity, seeds, temperature, alerts, integration
- Backward compatibility: all existing tests still pass

### Clinical Insights
- Temperature 0.0: Perfect consistency (100% exact match)
- Temperature 0.3: Mostly consistent (~95% similarity)
- Temperature 0.7: Significant variability (~60% similarity)
- Clinicians notice inconsistency - same note → different summary = lost trust

### Key Metrics Tracked
- Run count and unique output ratio
- Pairwise similarity (average, min, max)
- Exact match rate
- Length statistics (mean, std dev)
- Temperature and seed values
- Alert triggers for concerning patterns

## [0.6.0] - 2026-03-02

### Added - Post 6: Shadow Mode Deployment
- **Shadow Mode Runner**: Dual-path execution comparing production and candidate models side by side
- **HAPI FHIR Client**: Minimal client for fetching patient context from open HAPI FHIR servers
- **FHIR Bundle Parser**: Convert HAPI FHIR Bundles (Patient, Encounter, Condition, Observation, MedicationRequest) into clinical note text
- **Divergence Detection**: Automatic flagging when shadow output diverges from production using Post 5's fuzzy match metric
- **Rollout Recommendations**: Data-driven promotion algorithm with tiered traffic percentages (10%/25%/50%/100%)
- **Alert System**: Critical and warning severity alerts for shadow failures and low similarity
- **Result Persistence**: JSON-based shadow run history for rollout analysis
- **Shadow Rollout Report**: CLI script to summarize saved shadow runs and print promotion recommendations
- **11 New Tests**: 8 shadow unit tests + 3 API endpoint tests (Total: 150 tests)

### Files Added
- `app/shadow.py` - Shadow mode service (590+ lines)
- `tests/test_shadow.py` - 8 comprehensive shadow mode tests
- `examples/test_shadow_mode.py` - Demo with inline HAPI FHIR bundle
- `examples/test_shadow_hapi_server.py` - Demo against live HAPI FHIR server
- `scripts/shadow_rollout_report.py` - CLI rollout report

### Files Modified
- `app/config.py` - Shadow mode and HAPI FHIR settings
- `app/models.py` - ShadowModeRequest, ShadowModeResponse, RolloutDecision models
- `app/main.py` - `/shadow/summarize` endpoint
- `tests/test_api.py` - 3 new shadow endpoint tests
- `.env.example` - Shadow mode and HAPI FHIR environment variables

### New Configuration
- `SHADOW_MODE_ENABLED` - Feature flag for shadow mode (default: false)
- `SHADOW_CANDIDATE_MODEL` - Model for the candidate path
- `SHADOW_CANDIDATE_TEMPERATURE` - Temperature for candidate inference
- `SHADOW_SIMILARITY_THRESHOLD` - Minimum similarity before flagging divergence
- `SHADOW_ALERT_SIMILARITY_THRESHOLD` - Critical alert threshold
- `SHADOW_PROMOTION_MIN_REQUESTS` - Minimum runs before promotion decisions
- `HAPI_FHIR_BASE_URL` - Optional HAPI FHIR server URL
- `HAPI_FHIR_TIMEOUT_SECONDS` - FHIR request timeout

---

## [0.7.0] - 2026-03-24

### Added - Post 7: Monitoring That Triggers Action
- **Actionable Monitoring Service**: Evaluates recent shadow runs and applies runtime guardrails
- **Quality Guardrail**: Automatic `pause_shadow_mode` action when divergence/critical-alert rates breach policy
- **Performance Guardrail**: Automatic `freeze_candidate_rollout` action when average latency/cost budgets are exceeded
- **Monitoring State Persistence**: JSON state store with TTL-based action expiry
- **Monitoring API Endpoints**:
  - `GET /monitoring/status`
  - `POST /monitoring/evaluate`
  - `POST /monitoring/actions/reset`
- **Monitoring CLI Report**: `scripts/monitoring_action_report.py`
- **7 New Tests**: 4 monitoring unit tests + 3 API tests for action behavior

### Files Added
- `app/monitoring.py` - Monitoring engine and action/state models
- `tests/test_monitoring.py` - Monitoring unit tests
- `scripts/monitoring_action_report.py` - Monitoring action report CLI

### Files Modified
- `app/main.py` - Monitoring endpoints and shadow guardrail enforcement
- `app/models.py` - Monitoring response models
- `app/config.py` - Monitoring settings and version update
- `tests/test_api.py` - Monitoring API and guardrail tests
- `.env.example` - Monitoring environment variables

### New Configuration
- `MONITORING_ENABLED`
- `MONITORING_WINDOW_SIZE`
- `MONITORING_MIN_RUNS_FOR_ACTIONS`
- `MONITORING_MAX_DIVERGENCE_RATE`
- `MONITORING_MAX_CRITICAL_ALERT_RATE`
- `MONITORING_MAX_AVG_SHADOW_LATENCY_MS`
- `MONITORING_MAX_AVG_SHADOW_COST_USD`
- `MONITORING_ACTION_TTL_MINUTES`
- `MONITORING_STATE_FILE`

---

## [0.8.0] - 2026-04-07

### Added - Post 8: Human Feedback Without Burning Clinicians
- **Feedback Service**: Low-friction clinician feedback capture with append-only JSONL storage
- **Feedback Submission Endpoint**: `POST /feedback` with `up/down` signal, categories, and optional inline correction
- **Feedback Analytics Endpoint**: `GET /feedback/analytics` for coverage, sentiment, and category metrics
- **High-Priority Queue Endpoint**: `GET /feedback/queue` for targeted review of risky feedback
- **Served Response Tracking**: `/summarize` and `/shadow/summarize` now register served responses for response-rate analytics
- **Feedback Analytics Report CLI**: `scripts/feedback_analytics_report.py`
- **8 New Tests**: 4 feedback service tests + 4 API feedback endpoint tests

### Files Added
- `app/feedback.py` - Feedback capture, analytics, and queue logic
- `tests/test_feedback.py` - Feedback service tests
- `scripts/feedback_analytics_report.py` - Feedback analytics report CLI
- `docs/POST_8_LINKEDIN_ARTICLE.md` - Post 8 article
- `docs/POST_8_SUMMARY.md` - Post 8 implementation summary

### Files Modified
- `app/main.py` - Feedback endpoints and served-response instrumentation
- `app/models.py` - Feedback request/response models
- `app/config.py` - Feedback configuration and version update
- `tests/test_api.py` - Feedback endpoint tests
- `.env.example` - Feedback environment variables

### New Configuration
- `FEEDBACK_ENABLED`
- `FEEDBACK_STORE_DIR`
- `FEEDBACK_DEFAULT_ANALYTICS_DAYS`
- `FEEDBACK_MAX_CATEGORIES`
- `FEEDBACK_MAX_QUEUE_ITEMS`
- `FEEDBACK_HIGH_PRIORITY_CATEGORIES`

---

## [0.5.0] - 2026-02-16

### Added - Post 5: Evaluation Harness
- **Golden Dataset Management**: JSON-based test example storage
- **Evaluation Framework**: Systematic model performance measurement
- **Regression Detection**: Automated version comparison
- **26 New Tests**: Comprehensive test coverage (Total: 139 tests)

### Files Added
- `app/evaluation.py` - Core evaluation harness (500+ lines)
- `tests/test_evaluation.py` - 26 comprehensive tests
- `examples/test_evaluation.py` - Working demonstration
- `evaluation_datasets/clinical_summarization_golden.json` - Sample dataset
- `docs/POST_5_LINKEDIN_ARTICLE.md` - Publication-ready article
- `docs/POST_5_SUMMARY.md` - Technical summary

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
- **0.4.0** - Determinism and variability (Post 4) ✅
- **0.5.0** - Evaluation harness (Post 5) ✅
- **0.6.0** - Shadow mode deployment (Post 6) ✅
- **0.7.0** - Monitoring that triggers action (Post 7) ✅
- **0.8.0** - Human feedback loops (Post 8) ✅
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

### 0.3.0 → 0.4.0
- New variability measurement system
- No new dependencies required (uses stdlib only)
- New module `app/variability.py` available for import
- No breaking changes - backward compatible
- Existing code continues to work unchanged
- Optionally use variability tools for consistency monitoring

### 0.4.0 → 0.5.0
- New evaluation harness with golden dataset management
- New module `app/evaluation.py` available for import
- No breaking changes - backward compatible

### 0.5.0 → 0.6.0
- New shadow mode deployment with dual-path execution
- Set `SHADOW_MODE_ENABLED=true` to enable shadow mode
- Optionally set `HAPI_FHIR_BASE_URL` for FHIR-based inputs
- Configure `SHADOW_CANDIDATE_MODEL` to compare different models
- No breaking changes - backward compatible
- New endpoint: `POST /shadow/summarize`

### 0.6.0 → 0.7.0
- Added actionable monitoring with automatic guardrail actions
- New endpoints: `GET /monitoring/status`, `POST /monitoring/evaluate`, `POST /monitoring/actions/reset`
- Added monitoring configuration values in `.env.example`
- Shadow execution can now be automatically paused by monitoring policy

### 0.7.0 → 0.8.0
- Added structured clinician feedback capture and analytics
- New endpoints: `POST /feedback`, `GET /feedback/analytics`, `GET /feedback/queue`
- Added feedback configuration values in `.env.example`
- Summarization and shadow responses are now tracked for feedback coverage metrics

---

For details on how to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
