# HELM / MedHELM Integration Guide

## Overview

[HELM (Holistic Evaluation of Language Models)](https://github.com/stanford-crfm/helm) is Stanford's evaluation framework for language models. [MedHELM](https://crfm.stanford.edu/helm/medhelm/latest/) is the healthcare-focused benchmark suite built on top of HELM. This guide shows how to use HELM and MedHELM alongside our built-in evaluation harness for more sophisticated metrics.

## When to Use MedHELM / HELM vs Built-in Evaluator

**Use Built-in Evaluator when:**
- You need simple, dependency-free evaluation
- You want fast CI/CD integration
- You need basic metrics (exact match, Jaccard similarity)
- You're starting with evaluation infrastructure

**Use MedHELM / HELM when:**
- You need standardized benchmarks (MMLU, BIG-Bench, etc.)
- You want healthcare-specific benchmark suites such as MedHELM
- You want comprehensive metric suites (accuracy, calibration, efficiency, fairness, robustness)
- You need reproducible research-grade evaluation
- You want to compare against published baselines

**Use Both when:**
- HELM provides gold-standard benchmarks
- Built-in evaluator provides custom healthcare-specific tests
- You want both research-grade and domain-specific evaluation

## Installation

HELM / MedHELM is an optional dependency:

```bash
# Install HELM with MedHELM extras
pip install -U "crfm-helm[summarization,medhelm]"

# Or add to requirements-dev.txt
echo 'crfm-helm[summarization,medhelm]' >> requirements-dev.txt
pip install -r requirements-dev.txt
```

## Basic HELM Usage

### 1. Using HELM's Pre-built Scenarios

HELM provides many pre-built evaluation scenarios:

```python
from helm.common.authentication import Authentication
from helm.proxy.services.remote_service import RemoteService
from helm.benchmark.run import run_entries

# Configure authentication
auth = Authentication(api_key="your-api-key")

# Run a scenario
run_entries([
    {
        "description": "Clinical note summarization",
        "priority": 1,
        "groups": ["clinical_nlp"]
    }
])
```

### 2. Creating Custom HELM Scenarios

For healthcare-specific evaluation:

```python
from helm.benchmark.scenarios.scenario import Scenario, Instance

class ClinicalSummarizationScenario(Scenario):
    """Custom scenario for clinical note summarization."""
    
    name = "clinical_summarization"
    description = "Evaluates clinical note summarization quality"
    
    def get_instances(self):
        # Load your golden dataset
        from app.evaluation import GoldenDataset
        dataset = GoldenDataset("evaluation_datasets/clinical_summarization_golden.json")
        dataset.load()
        
        # Convert to HELM instances
        instances = []
        for example in dataset.examples:
            instances.append(Instance(
                input=example.input_text,
                references=[example.expected_output],
                id=example.id
            ))
        
        return instances
```

### 3. Using HELM Metrics

HELM provides sophisticated metrics:

```python
from helm.benchmark.metrics.metric import Metric
from helm.benchmark.metrics.basic_metrics import ExactMatchMetric, F1Metric
from helm.benchmark.adaptation.adapter_spec import AdapterSpec
from helm.benchmark.run_specs.run_spec import RunSpec

# Configure metrics
metrics = [
    ExactMatchMetric(),
    F1Metric(),
    # HELM also provides: ROUGE, BLEU, BERTScore, etc.
]

# Create run spec
run_spec = RunSpec(
    name="clinical_summarization_claude",
    scenario_spec={"name": "clinical_summarization"},
    adapter_spec=AdapterSpec(method="generation"),
    metric_specs=metrics
)
```

## Hybrid Approach: Built-in + HELM

Recommended pattern for production:

```python
from app.evaluation import GoldenDataset, Evaluator, RegressionDetector
from helm.benchmark.run import Runner
from helm.benchmark.metrics.basic_metrics import ExactMatchMetric, F1Metric

# 1. Quick evaluation with built-in evaluator (CI/CD)
dataset = GoldenDataset("golden_dataset.json")
dataset.load()
evaluator = Evaluator(dataset)

results, summary = evaluator.evaluate_all(
    model_fn=my_model,
    model_version="v2.0",
    pass_threshold=0.85
)

# Gate deployment on built-in metrics
is_regression, reason = RegressionDetector.detect_regression(
    baseline_summary, summary
)

if is_regression:
    print(f"Deployment blocked: {reason}")
    exit(1)

# 2. Comprehensive evaluation with MedHELM / HELM (weekly/research)
if os.getenv("RUN_HELM_EVALUATION"):
    # Run benchmark suite for detailed analysis
    helm_runner = Runner()
    helm_results = helm_runner.run(
        scenario="clinical_summarization",
        model="claude-3-sonnet",
        metrics=[ExactMatchMetric(), F1Metric()]
    )
    
    # Log HELM results for research/analysis
    save_helm_results(helm_results, "helm_results_v2.0.json")
```

## Example: HELM-Compatible Adapter

Create an adapter to use our models with HELM:

```python
# helm_adapter.py
from helm.proxy.models.model import Model
from helm.proxy.services.service import Service
from app.llm import get_llm_service

class CustomClinicalModel(Model):
    """Adapter to use our LLM service with HELM."""
    
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.llm_service = get_llm_service()
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using our LLM service."""
        response = self.llm_service.summarize_clinical_note(
            note_text=prompt,
            temperature=kwargs.get("temperature", 0.3)
        )
        return response.summary

# Register custom model with HELM
from helm.proxy.services.model_registry import register_model
register_model("custom-clinical-model", CustomClinicalModel)
```

## MedHELM / HELM Metrics for Healthcare

Relevant benchmark metrics for clinical AI:

```python
from helm.benchmark.metrics import (
    ExactMatchMetric,      # Structured extraction
    F1Metric,              # Token overlap
    RougeMetric,           # Summarization quality
    BERTScoreMetric,       # Semantic similarity
    BiasMetric,            # Fairness evaluation
    ToxicityMetric,        # Safety evaluation
)

# Healthcare-specific metric configuration
healthcare_metrics = [
    ExactMatchMetric(),           # For ICD codes, medications
    F1Metric(),                   # For entity extraction
    RougeMetric(types=["rouge-l"]), # For summarization
    BERTScoreMetric(),            # For semantic preservation
    BiasMetric(                   # Check for demographic bias
        demographic_categories=["gender", "age", "race"]
    ),
]
```

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Evaluation System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │  Built-in Evaluator  │      │   HELM (Optional)     │    │
│  ├──────────────────────┤      ├──────────────────────┤    │
│  │ • Fast               │      │ • Comprehensive       │    │
│  │ • Simple metrics     │      │ • Research-grade      │    │
│  │ • CI/CD friendly     │      │ • Standardized        │    │
│  │ • No dependencies    │      │ • Many metrics        │    │
│  │ • Custom thresholds  │      │ • Reproducible        │    │
│  └──────────────────────┘      └──────────────────────┘    │
│           ↓                              ↓                   │
│  ┌─────────────────────────────────────────────────┐        │
│  │         Golden Dataset (Shared)                  │        │
│  │  • JSON format                                   │        │
│  │  • Version controlled                            │        │
│  │  • Clinical examples                             │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## CI/CD Integration

**Fast Path (Built-in):** Every PR
```yaml
# .github/workflows/evaluate.yml
- name: Quick Evaluation
  run: python -m pytest tests/test_evaluation.py
```

**Comprehensive Path (HELM):** Weekly or on-demand
```yaml
# .github/workflows/helm-evaluation.yml
- name: HELM Benchmarks
  if: github.event_name == 'schedule'
  run: |
    helm-run --conf-paths helm_config.yaml
    helm-summarize --suite clinical_suite
```

## Cost Considerations

**Built-in Evaluator:**
- 10 examples × $0.002 = $0.02 per evaluation
- Run on every commit
- Cost: ~$10/month

**HELM:**
- Comprehensive benchmarks = 1000s of examples
- Cost: $20-$100 per full evaluation
- Run weekly or on-demand
- Cost: ~$400-$4000/month if run weekly

**Recommendation:** Use built-in for CI/CD, HELM for periodic deep evaluation.

## Migration Path

**Phase 1: Start with Built-in** (Posts 1-5)
- Simple metrics
- Fast feedback
- Learn evaluation fundamentals

**Phase 2: Add HELM Selectively** (Advanced)
- Install HELM as optional dependency
- Run HELM weekly for specific scenarios
- Compare metrics with built-in

**Phase 3: Hybrid Approach** (Production)
- Built-in: Every commit (fast, cheap, custom)
- HELM: Weekly (comprehensive, standardized, research-grade)

## Limitations

**Built-in Evaluator:**
- Simple metrics (Jaccard similarity)
- Limited to custom datasets
- No standardized benchmarks
- Manual threshold tuning

**HELM:**
- Complex setup
- Heavier dependencies
- Slower execution
- Higher API costs
- May not capture domain-specific nuances

**Best Practice:** Use both. Built-in for speed and customization, HELM for standardization and research.

## Example Workflow

```python
# evaluate.py - Hybrid evaluation script

def quick_evaluation(model_fn, dataset):
    """Fast evaluation for CI/CD."""
    from app.evaluation import Evaluator
    evaluator = Evaluator(dataset)
    return evaluator.evaluate_all(model_fn, pass_threshold=0.85)

def comprehensive_evaluation(model_name, dataset):
    """Comprehensive HELM evaluation."""
    from helm.benchmark.run import run_benchmarks
    
    # Convert dataset to HELM format
    helm_dataset = convert_to_helm_format(dataset)
    
    # Run HELM benchmarks
    results = run_benchmarks(
        model=model_name,
        scenarios=["clinical_summarization"],
        metrics=["exact_match", "f1", "rouge", "bertscore"]
    )
    
    return results

# Main evaluation logic
if __name__ == "__main__":
    dataset = GoldenDataset("golden_dataset.json")
    dataset.load()
    
    # Always run quick evaluation
    quick_results, quick_summary = quick_evaluation(my_model, dataset)
    
    # Gate deployment
    if not passes_quality_threshold(quick_summary):
        sys.exit(1)
    
    # Run HELM if requested
    if os.getenv("RUN_HELM"):
        helm_results = comprehensive_evaluation("claude-3", dataset)
        log_helm_results(helm_results)
```

## Resources

- **HELM GitHub**: https://github.com/stanford-crfm/helm
- **HELM Documentation**: https://crfm.stanford.edu/helm/
- **MedHELM Documentation**: https://crfm.stanford.edu/helm/medhelm/latest/
- **HELM Paper**: https://arxiv.org/abs/2211.09110
- **Our Built-in Evaluator**: `docs/POST_5_LINKEDIN_ARTICLE.md`
- **Implementation Summary**: `docs/POST_5_SUMMARY.md`

## Support

For HELM-specific issues, see their GitHub issues.
For integration questions with our system, see our documentation or create an issue.

---

**Summary**: HELM provides research-grade evaluation. Our built-in evaluator provides fast, custom evaluation. Use both for optimal coverage.
