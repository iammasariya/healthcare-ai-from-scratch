#!/usr/bin/env python3
"""
Example: Measuring and Controlling Variability (Post 4)

This script demonstrates:
1. Running repeated inference to measure variability
2. Comparing outputs at different temperatures
3. Calculating semantic similarity
4. Using deterministic seeds
5. Temperature recommendations by use case
6. Detecting concerning variability
"""

import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.variability import (
    VariabilityMeasurer,
    DeterminismController,
    InferenceRun,
    calculate_output_hash,
    detect_variability_alert
)


def simulate_inference_runs(note_text: str, temperature: float, num_runs: int = 10):
    """
    Simulate multiple inference runs at a given temperature.
    
    In production, you would actually call your LLM here multiple times.
    For this demo, we simulate different levels of variability based on temperature.
    """
    print(f"\nSimulating {num_runs} inference runs at temperature={temperature}...")
    
    # Base outputs that we'll vary based on temperature
    base_outputs = [
        "Patient presents with acute headache, denies trauma. Vital signs stable.",
        "Patient reports acute headache onset. No trauma history. Vitals are stable.",
        "Acute headache noted in patient. Denies any trauma. Vital signs within normal limits.",
        "Patient's chief complaint is acute headache. No traumatic injury. Stable vital signs.",
        "Headache reported as acute onset. Patient denies trauma. Vitals stable.",
    ]
    
    runs = []
    
    for i in range(num_runs):
        # At low temp, use mostly the same output
        # At high temp, use more varied outputs
        if temperature < 0.2:
            output = base_outputs[0]  # Always same
        elif temperature < 0.4:
            output = base_outputs[i % 2]  # Alternate between 2
        elif temperature < 0.6:
            output = base_outputs[i % 3]  # Rotate through 3
        else:
            output = base_outputs[i % 5]  # Use all 5
        
        run = InferenceRun(
            output=output,
            run_number=i + 1,
            latency_ms=850.0 + (i * 10),  # Slight variation
            tokens_used=150,
            audit_id=uuid4(),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        runs.append(run)
    
    return runs


def demonstrate_variability_measurement():
    """Demonstrate measuring variability at different temperatures."""
    print("=" * 70)
    print("DEMO 1: Measuring Variability at Different Temperatures")
    print("=" * 70)
    
    note_text = "Patient presents with acute headache. Denies trauma. Vital signs stable."
    measurer = VariabilityMeasurer()
    
    # Test different temperatures
    temperatures = [0.0, 0.3, 0.7]
    
    for temp in temperatures:
        print(f"\n{'─' * 70}")
        print(f"Temperature: {temp}")
        print(f"{'─' * 70}")
        
        # Simulate runs
        runs = simulate_inference_runs(note_text, temp, num_runs=10)
        
        # Measure variability
        metrics = measurer.measure_variability(runs, temperature=temp)
        
        # Display results
        print(f"\nVariability Metrics:")
        print(f"  Run count: {metrics.run_count}")
        print(f"  Unique outputs: {metrics.unique_outputs}")
        print(f"  Exact match rate: {metrics.exact_match_rate:.1%}")
        print(f"  Avg similarity: {metrics.pairwise_similarity_avg:.3f}")
        print(f"  Min similarity: {metrics.pairwise_similarity_min:.3f}")
        print(f"  Max similarity: {metrics.pairwise_similarity_max:.3f}")
        print(f"  Avg length: {metrics.avg_length:.0f} chars")
        print(f"  Length std dev: {metrics.length_std_dev:.1f}")
        
        # Check if acceptable
        is_acceptable, reason = measurer.is_acceptable_variability(metrics)
        if is_acceptable:
            print(f"\n  ✓ ACCEPTABLE: {reason}")
        else:
            print(f"\n  ✗ NOT ACCEPTABLE: {reason}")
        
        # Check for alerts
        alert = detect_variability_alert(metrics)
        if alert:
            print(f"\n  ⚠️  {alert}")


def demonstrate_similarity_comparison():
    """Demonstrate semantic similarity comparison."""
    print("\n\n" + "=" * 70)
    print("DEMO 2: Semantic Similarity Comparison")
    print("=" * 70)
    
    measurer = VariabilityMeasurer()
    
    # Example text pairs
    pairs = [
        (
            "Patient presents with acute headache.",
            "Patient presents with acute headache."
        ),
        (
            "Patient presents with acute headache.",
            "Patient has an acute headache."
        ),
        (
            "Patient presents with acute headache.",
            "Headache reported by patient."
        ),
        (
            "Patient presents with acute headache.",
            "The weather is sunny today."
        )
    ]
    
    for i, (text1, text2) in enumerate(pairs, 1):
        similarity = measurer.calculate_similarity(text1, text2)
        
        print(f"\nPair {i}:")
        print(f"  Text 1: \"{text1}\"")
        print(f"  Text 2: \"{text2}\"")
        print(f"  Similarity: {similarity:.3f}")
        
        if similarity == 1.0:
            print(f"  → Identical")
        elif similarity > 0.9:
            print(f"  → Nearly identical")
        elif similarity > 0.7:
            print(f"  → Very similar")
        elif similarity > 0.5:
            print(f"  → Somewhat similar")
        else:
            print(f"  → Different")


def demonstrate_deterministic_seeds():
    """Demonstrate deterministic seed generation."""
    print("\n\n" + "=" * 70)
    print("DEMO 3: Deterministic Seed Generation")
    print("=" * 70)
    
    print("\nSeeds for different contexts (should be different):")
    print()
    
    # Same patient, different dates
    seed1 = DeterminismController.get_deterministic_seed("PT-12345", "1.0.0", "2026-02-06")
    seed2 = DeterminismController.get_deterministic_seed("PT-12345", "1.0.0", "2026-02-07")
    print(f"  PT-12345, v1.0.0, 2026-02-06: {seed1}")
    print(f"  PT-12345, v1.0.0, 2026-02-07: {seed2}")
    print(f"  → Different dates = different seeds: {seed1 != seed2}")
    
    # Same date, different patients
    seed3 = DeterminismController.get_deterministic_seed("PT-67890", "1.0.0", "2026-02-06")
    print(f"\n  PT-12345, v1.0.0, 2026-02-06: {seed1}")
    print(f"  PT-67890, v1.0.0, 2026-02-06: {seed3}")
    print(f"  → Different patients = different seeds: {seed1 != seed3}")
    
    # Same patient/date, different versions
    seed4 = DeterminismController.get_deterministic_seed("PT-12345", "2.0.0", "2026-02-06")
    print(f"\n  PT-12345, v1.0.0, 2026-02-06: {seed1}")
    print(f"  PT-12345, v2.0.0, 2026-02-06: {seed4}")
    print(f"  → Different versions = different seeds: {seed1 != seed4}")
    
    # Consistency test
    seed5 = DeterminismController.get_deterministic_seed("PT-12345", "1.0.0", "2026-02-06")
    print(f"\n  PT-12345, v1.0.0, 2026-02-06 (1st call): {seed1}")
    print(f"  PT-12345, v1.0.0, 2026-02-06 (2nd call): {seed5}")
    print(f"  → Same inputs = same seed: {seed1 == seed5} ✓")


def demonstrate_temperature_recommendations():
    """Demonstrate temperature recommendations."""
    print("\n\n" + "=" * 70)
    print("DEMO 4: Temperature Recommendations by Use Case")
    print("=" * 70)
    
    # Different task types and risk levels
    scenarios = [
        ("extraction", "high", "Extracting ICD codes"),
        ("extraction", "medium", "Extracting medication names"),
        ("summary", "high", "Clinical note summarization"),
        ("summary", "medium", "Patient education materials"),
        ("generation", "high", "Treatment plan suggestions"),
        ("generation", "low", "General wellness advice"),
        ("research", "medium", "Literature search queries"),
        ("research", "low", "Educational content generation"),
    ]
    
    print("\nTask Type        Risk Level    Recommended Temp    Rationale")
    print("─" * 70)
    
    for task, risk, description in scenarios:
        temp = DeterminismController.recommend_temperature(task, risk)
        
        # Determine determinism level
        if temp <= 0.1:
            determinism = "Maximum (nearly deterministic)"
        elif temp <= 0.3:
            determinism = "High (mostly consistent)"
        elif temp <= 0.5:
            determinism = "Moderate (balanced)"
        elif temp <= 0.7:
            determinism = "Low (more creative)"
        else:
            determinism = "Minimal (high creativity)"
        
        print(f"{task:15s}  {risk:10s}    {temp:4.1f}                {determinism}")
    
    print("\nUse Case Examples:")
    print("─" * 70)
    for task, risk, description in scenarios:
        temp = DeterminismController.recommend_temperature(task, risk)
        print(f"\n  {description}")
        print(f"  → Task: {task}, Risk: {risk}, Temperature: {temp}")


def demonstrate_output_hashing():
    """Demonstrate output hashing for comparison."""
    print("\n\n" + "=" * 70)
    print("DEMO 5: Output Hashing for Quick Comparison")
    print("=" * 70)
    
    outputs = [
        "Patient presents with acute headache.",
        "Patient presents with acute headache.",  # Duplicate
        "Patient has an acute headache.",  # Similar but different
        "The weather is sunny today."  # Completely different
    ]
    
    print("\nOutput hashes for quick duplicate detection:")
    print()
    
    hashes = []
    for i, output in enumerate(outputs, 1):
        hash_val = calculate_output_hash(output)
        hashes.append((output, hash_val))
        print(f"{i}. \"{output}\"")
        print(f"   Hash: {hash_val}")
        
        # Check for duplicates
        duplicates = [j for j, (_, h) in enumerate(hashes[:-1], 1) if h == hash_val]
        if duplicates:
            print(f"   → Exact duplicate of output {duplicates[0]}")
        print()


def demonstrate_clinical_scenarios():
    """Demonstrate real clinical scenarios."""
    print("\n" + "=" * 70)
    print("DEMO 6: Clinical Scenarios - When Variability Matters")
    print("=" * 70)
    
    scenarios = [
        {
            "scenario": "ICD Code Extraction",
            "temperature": 0.0,
            "why": "Must be 100% deterministic - same note should always produce same codes",
            "acceptable_variability": "0% - any variation is unacceptable"
        },
        {
            "scenario": "Clinical Summary",
            "temperature": 0.2,
            "why": "Should be highly consistent - clinicians notice changes",
            "acceptable_variability": "<10% - minor wording variations acceptable"
        },
        {
            "scenario": "Differential Diagnosis",
            "temperature": 0.5,
            "why": "Balanced - need consistency but also comprehensive coverage",
            "acceptable_variability": "<30% - different but related suggestions acceptable"
        },
        {
            "scenario": "Patient Education",
            "temperature": 0.7,
            "why": "More flexibility - can adapt phrasing for readability",
            "acceptable_variability": "<50% - varied explanations can be helpful"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario['scenario']}")
        print(f"{'─' * 70}")
        print(f"  Recommended Temperature: {scenario['temperature']}")
        print(f"  Why: {scenario['why']}")
        print(f"  Acceptable Variability: {scenario['acceptable_variability']}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("=" * 70)
    print("Post 4: Determinism, Variability, and Why Clinicians Notice")
    print("=" * 70)
    print("\nThis demo shows how to measure and control model variability")
    print("in healthcare AI systems where consistency affects clinical trust.")
    print()
    
    try:
        # Run demonstrations
        demonstrate_variability_measurement()
        demonstrate_similarity_comparison()
        demonstrate_deterministic_seeds()
        demonstrate_temperature_recommendations()
        demonstrate_output_hashing()
        demonstrate_clinical_scenarios()
        
        # Summary
        print("\n\n" + "=" * 70)
        print("KEY TAKEAWAYS")
        print("=" * 70)
        print("""
1. Temperature Controls Variability
   - Lower temperature (0.0-0.2) → More deterministic
   - Higher temperature (0.5-0.8) → More creative/varied

2. Measure Before You Deploy
   - Run same prompt 10-100 times
   - Calculate similarity metrics
   - Set acceptable thresholds

3. Context Matters
   - Extraction: Need determinism (temp ~0.0)
   - Summaries: Need consistency (temp ~0.2-0.3)
   - Generation: Can vary more (temp ~0.5-0.7)

4. Clinicians Notice Inconsistency
   - Same note → different summary = lost trust
   - Measure and control variability proactively
   - Set alerts for unexpected divergence

5. Use Deterministic Seeds When Needed
   - Reproducibility for debugging
   - Consistency for repeated tasks
   - Different context → different seed (patient, date, version)

For more details, see:
  - docs/POST_4_LINKEDIN_ARTICLE.md
  - docs/POST_4_SUMMARY.md
  - app/variability.py (implementation)
  - tests/test_variability.py (comprehensive tests)
        """)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()