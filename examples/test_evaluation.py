"""
Example demonstrating evaluation harness (Post 5)

This shows how to:
1. Create a golden dataset
2. Evaluate model performance
3. Compare model versions
4. Detect regressions
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.evaluation import (
    GoldenExample,
    GoldenDataset,
    Evaluator,
    RegressionDetector,
    save_evaluation_results
)

SAMPLE_EXAMPLES = [
    {
        "id": "sum-001",
        "input": "Patient presents with acute onset headache, denies trauma. Vital signs stable. Neurological exam normal.",
        "output": "Patient with acute headache, no trauma, stable vitals, normal neuro exam.",
        "task": "summarization"
    },
    {
        "id": "sum-002",
        "input": "72-year-old male with history of hypertension presents with chest pain radiating to left arm. EKG shows ST elevation.",
        "output": "72yo male with HTN, chest pain to left arm, ST elevation on EKG.",
        "task": "summarization"
    },
    {
        "id": "sum-003",
        "input": "Patient reports shortness of breath on exertion. No cough. Lung sounds clear bilaterally.",
        "output": "SOB on exertion, no cough, clear lungs bilaterally.",
        "task": "summarization"
    },
    {
        "id": "sum-004",
        "input": "45-year-old female with fever, productive cough, and chills for 3 days. Temperature 101.2F.",
        "output": "45yo female with fever (101.2F), productive cough, chills x3 days.",
        "task": "summarization"
    },
    {
        "id": "sum-005",
        "input": "Patient with type 2 diabetes, last A1C 8.2%. Reports good medication compliance.",
        "output": "Type 2 diabetes, A1C 8.2%, compliant with meds.",
        "task": "summarization"
    }
]

BASELINE_OUTPUTS = {example["input"]: example["output"] for example in SAMPLE_EXAMPLES}
REGRESSION_OUTPUTS = {
    SAMPLE_EXAMPLES[0]["input"]: "Headache.",
    SAMPLE_EXAMPLES[1]["input"]: "72-year-old male with chest pain.",
    SAMPLE_EXAMPLES[2]["input"]: "Shortness of breath on exertion.",
    SAMPLE_EXAMPLES[3]["input"]: "45-year-old female with fever and cough.",
    SAMPLE_EXAMPLES[4]["input"]: "Type 2 diabetes."
}


def create_sample_dataset() -> GoldenDataset:
    """Create a sample golden dataset for demonstration."""
    dataset = GoldenDataset()

    for ex in SAMPLE_EXAMPLES:
        dataset.add_example(GoldenExample(
            id=ex["id"],
            input_text=ex["input"],
            expected_output=ex["output"],
            task_type=ex["task"],
            metadata={"source": "example"}
        ))
    
    return dataset


def simulate_model_v1(text: str) -> str:
    """Simulate model v1.0 as a strong baseline."""
    return BASELINE_OUTPUTS.get(text, text)


def simulate_model_v2(text: str) -> str:
    """Simulate model v2.0 with a clear quality regression."""
    return REGRESSION_OUTPUTS.get(text, text.split(".")[0].strip() + ".")


def main():
    """Run evaluation demonstration."""
    print("=" * 70)
    print("Post 5: Evaluation Harness Demonstration")
    print("=" * 70)
    print()
    
    # Create golden dataset
    print("Step 1: Creating golden dataset...")
    dataset = create_sample_dataset()
    print(f"✓ Created dataset with {len(dataset)} examples")
    print()
    
    # Evaluate model v1.0
    print("Step 2: Evaluating model v1.0 baseline...")
    evaluator = Evaluator(dataset)
    results_v1, summary_v1 = evaluator.evaluate_all(
        model_fn=simulate_model_v1,
        model_version="v1.0",
        pass_threshold=0.60
    )
    
    print(f"Model v1.0 Results:")
    print(f"  Total examples: {summary_v1.total_examples}")
    print(f"  Passed: {summary_v1.passed_examples}")
    print(f"  Failed: {summary_v1.failed_examples}")
    print(f"  Pass rate: {summary_v1.pass_rate:.1%}")
    print(f"  Avg score: {summary_v1.avg_score:.3f}")
    print(f"  Avg latency: {summary_v1.avg_latency_ms:.1f}ms")
    print()
    
    # Show some individual results
    print("Sample predictions (v1.0):")
    for result in results_v1[:2]:
        print(f"\n  Example: {result.example_id}")
        print(f"  Expected: {result.expected_output[:60]}...")
        print(f"  Predicted: {result.predicted_output[:60]}...")
        print(f"  Score: {result.score:.3f}")
        print(f"  Passed: {'✓' if result.passed else '✗'}")
    print()
    
    # Evaluate model v2.0
    print("Step 3: Evaluating model v2.0 candidate...")
    results_v2, summary_v2 = evaluator.evaluate_all(
        model_fn=simulate_model_v2,
        model_version="v2.0",
        pass_threshold=0.60
    )
    
    print(f"Model v2.0 Results:")
    print(f"  Total examples: {summary_v2.total_examples}")
    print(f"  Passed: {summary_v2.passed_examples}")
    print(f"  Failed: {summary_v2.failed_examples}")
    print(f"  Pass rate: {summary_v2.pass_rate:.1%}")
    print(f"  Avg score: {summary_v2.avg_score:.3f}")
    print(f"  Avg latency: {summary_v2.avg_latency_ms:.1f}ms")
    print()
    
    # Compare versions
    print("Step 4: Comparing versions...")
    comparison = RegressionDetector.compare_versions(summary_v1, summary_v2)
    
    print(f"Version Comparison:")
    print(f"  Baseline: {comparison['baseline_version']}")
    print(f"  Current: {comparison['current_version']}")
    print(f"  Pass rate change: {comparison['pass_rate_change']:+.1%}")
    print(f"  Score change: {comparison['score_change']:+.3f}")
    print(f"  Latency change: {comparison['latency_change_ms']:+.1f}ms")
    print()
    
    # Detect regression
    print("Step 5: Detecting regression...")
    is_regression, reason = RegressionDetector.detect_regression(
        baseline_summary=summary_v1,
        current_summary=summary_v2,
        pass_rate_threshold=0.05,
        score_threshold=0.10
    )
    
    if is_regression:
        print(f"  REGRESSION DETECTED: {reason}")
    else:
        print(f"  No regression detected: {reason}")
    print()
    
    # Save results
    print("Step 6: Saving evaluation results...")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    
    save_evaluation_results(
        results_v1, 
        summary_v1, 
        output_dir / "v1.0_results.json"
    )
    save_evaluation_results(
        results_v2,
        summary_v2,
        output_dir / "v2.0_results.json"
    )
    print(f"  ✓ Results saved to {output_dir}/")
    print()
    
    # Summary
    print("=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print()
    print("1. Golden datasets enable systematic evaluation")
    print("2. Evaluation metrics provide objective model comparison")
    print("3. Regression detection catches quality degradation")
    print("4. Evaluation as code (not notebooks) enables CI/CD")
    print()
    print("This evaluation harness answers:")
    print("  - Is model v2 better than v1?")
    print("  - Did this prompt change improve quality?")
    print("  - Should we deploy the new model?")
    print()


if __name__ == "__main__":
    main()
