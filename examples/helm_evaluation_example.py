"""
Hybrid Evaluation Example: Built-in + HELM

This demonstrates using both evaluation systems:
- Built-in evaluator: Fast, simple, CI/CD friendly
- HELM: Comprehensive, standardized, research-grade

Usage:
    # Quick evaluation only (no HELM required)
    python examples/helm_evaluation_example.py
    
    # With HELM / MedHELM (requires benchmark extras)
    RUN_HELM=true python examples/helm_evaluation_example.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.evaluation import GoldenDataset, Evaluator, RegressionDetector
from app.helm_adapter import check_helm_availability, ClinicalModel, register_clinical_model


def create_sample_dataset():
    """Create a small sample dataset for demonstration."""
    from app.evaluation import GoldenExample
    
    dataset = GoldenDataset()
    
    examples = [
        {
            "id": "demo-001",
            "input": "Patient is a 45-year-old female presenting with acute chest pain radiating to left arm. BP 145/92, HR 98. EKG shows ST elevation in leads II, III, aVF.",
            "output": "45yo F with acute chest pain to left arm, BP 145/92, HR 98. EKG: ST elevation in II, III, aVF (inferior STEMI).",
            "task": "summarization"
        },
        {
            "id": "demo-002",
            "input": "28-year-old female with 3 days fever, productive cough, pleuritic chest pain. Temperature 101.8F, SpO2 94% on room air. CXR shows right lower lobe infiltrate.",
            "output": "28yo F with 3 days fever, productive cough, pleuritic chest pain. Temp 101.8F, SpO2 94% RA. CXR: RLL infiltrate (pneumonia).",
            "task": "summarization"
        },
    ]
    
    for ex in examples:
        dataset.add_example(GoldenExample(
            id=ex["id"],
            input_text=ex["input"],
            expected_output=ex["output"],
            task_type=ex["task"]
        ))
    
    return dataset


def simple_model(text: str) -> str:
    """
    Simulated model for demonstration.
    
    Replace this with your actual model function.
    """
    # Simple rule-based summarization for demo
    words = text.split()[:30]  # Take first 30 words
    return " ".join(words) + "..."


def run_builtin_evaluation(dataset):
    """Run fast evaluation with built-in evaluator."""
    print("=" * 70)
    print("BUILT-IN EVALUATOR (Fast, Simple)")
    print("=" * 70)
    print()
    
    evaluator = Evaluator(dataset)
    
    # Evaluate model
    results, summary = evaluator.evaluate_all(
        model_fn=simple_model,
        model_version="demo-v1.0",
        pass_threshold=0.60  # Lower threshold for demo
    )
    
    print(f"Results:")
    print(f"  Total examples: {summary.total_examples}")
    print(f"  Passed: {summary.passed_examples}")
    print(f"  Failed: {summary.failed_examples}")
    print(f"  Pass rate: {summary.pass_rate:.1%}")
    print(f"  Avg score: {summary.avg_score:.3f}")
    print(f"  Avg latency: {summary.avg_latency_ms:.1f}ms")
    print()
    
    # Show individual results
    print("Individual Results:")
    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"  {result.example_id}: {status} (score: {result.score:.3f})")
    print()
    
    return results, summary


def run_helm_evaluation(dataset):
    """Run comprehensive evaluation with HELM."""
    print("=" * 70)
    print("HELM EVALUATION (Comprehensive, Research-Grade)")
    print("=" * 70)
    print()
    
    if not check_helm_availability():
        print("⚠️  HELM not installed")
        print()
        print("To enable HELM evaluation:")
        print('  pip install -U "crfm-helm[summarization,medhelm]"')
        print()
        print("HELM provides:")
        print("  • ROUGE scores for summarization")
        print("  • BLEU scores for generation")
        print("  • BERTScore for semantic similarity")
        print("  • Fairness and bias metrics")
        print("  • Standardized benchmarks")
        print()
        return None
    
    try:
        from helm.benchmark.run import Runner
        from helm.benchmark.metrics.basic_metrics import ExactMatchMetric, F1Metric
        
        # Register our model with HELM
        register_clinical_model()
        
        # Create HELM runner
        print("Running HELM benchmarks...")
        print("(This may take a few minutes)")
        print()
        
        # Note: This is a simplified example
        # Full HELM integration requires more setup
        print("HELM Integration Notes:")
        print("  • See docs/HELM_INTEGRATION.md for full setup")
        print("  • HELM requires configuration files")
        print("  • HELM runs are typically batch operations")
        print("  • Results saved to HELM output directory")
        print()
        
        print("Example HELM metrics available:")
        print("  • ExactMatchMetric: Binary correctness")
        print("  • F1Metric: Token-level F1 score")
        print("  • RougeMetric: Summarization quality (ROUGE-L)")
        print("  • BERTScoreMetric: Semantic similarity")
        print("  • BiasMetric: Demographic fairness")
        print()
        
        return {"status": "helm_example_complete"}
        
    except Exception as e:
        print(f"⚠️  HELM evaluation error: {e}")
        print("See docs/HELM_INTEGRATION.md for troubleshooting")
        return None


def main():
    """Run hybrid evaluation demonstration."""
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Hybrid Evaluation Demo" + " " * 31 + "║")
    print("║" + " " * 15 + "Built-in + HELM" + " " * 37 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Create sample dataset
    print("Creating sample dataset...")
    dataset = create_sample_dataset()
    print(f"✓ Created {len(dataset)} examples")
    print()
    
    # Always run built-in evaluation (fast)
    builtin_results, builtin_summary = run_builtin_evaluation(dataset)
    
    # Run HELM if requested
    run_helm = os.getenv("RUN_HELM", "false").lower() == "true"
    
    if run_helm:
        helm_results = run_helm_evaluation(dataset)
    else:
        print("=" * 70)
        print("HELM EVALUATION (Skipped)")
        print("=" * 70)
        print()
        print("To run HELM evaluation:")
        print("  RUN_HELM=true python examples/helm_evaluation_example.py")
        print()
        print("Why use HELM?")
        print("  • Standardized benchmarks")
        print("  • Research-grade metrics (ROUGE, BLEU, BERTScore)")
        print("  • Fairness and bias evaluation")
        print("  • Compare against published baselines")
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Built-in Evaluator:")
    print(f"  ✓ Fast: {builtin_summary.avg_latency_ms:.1f}ms total")
    print(f"  ✓ Simple: Jaccard similarity metric")
    print(f"  ✓ Custom: Healthcare-specific thresholds")
    print(f"  ✓ CI/CD: Perfect for every commit")
    print()
    
    if run_helm:
        print("HELM Evaluator:")
        print(f"  ✓ Comprehensive: Multiple metrics")
        print(f"  ✓ Standardized: Research-grade")
        print(f"  ✓ Expensive: Use weekly/on-demand")
        print()
    
    print("Recommendation:")
    print("  • Use Built-in for every PR/commit (fast, cheap)")
    print("  • Use HELM weekly or before major releases (comprehensive)")
    print("  • Both systems share the same golden dataset")
    print()
    print("See docs/HELM_INTEGRATION.md for complete guide")
    print()


if __name__ == "__main__":
    main()
