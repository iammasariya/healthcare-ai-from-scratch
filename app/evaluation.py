"""
Evaluation Harness (Post 5)

This module provides tools to systematically evaluate model performance,
enabling data-driven decisions about model changes and catching regressions
before they reach production.

Key capabilities:
- Golden dataset management
- Task-specific evaluation metrics
- Model version comparison
- Regression detection
- Evaluation as code (not notebooks)
"""

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from uuid import UUID, uuid4


@dataclass
class GoldenExample:
    """
    A single example in the golden dataset.
    
    Attributes:
        id: Unique identifier for this example
        input_text: The input text (e.g., clinical note)
        expected_output: The expected/correct output
        task_type: Type of task (e.g., "summarization", "extraction", "classification")
        metadata: Additional context (difficulty, source, clinical specialty, etc.)
        created_at: When this example was created
        created_by: Who created/validated this example
    """
    id: str
    input_text: str
    expected_output: str
    task_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "input_text": self.input_text,
            "expected_output": self.expected_output,
            "task_type": self.task_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoldenExample":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            input_text=data["input_text"],
            expected_output=data["expected_output"],
            task_type=data["task_type"],
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            created_by=data.get("created_by", "system")
        )


@dataclass
class EvaluationResult:
    """
    Result of evaluating a single example.
    
    Attributes:
        example_id: ID of the example evaluated
        predicted_output: What the model actually produced
        expected_output: What the model should have produced
        exact_match: Whether prediction exactly matches expected
        score: Numeric score (0.0 to 1.0)
        metrics: Task-specific metrics
        passed: Whether this example passed evaluation
        failure_reason: Why it failed (if applicable)
        latency_ms: Time taken for inference
        model_version: Which model version was used
    """
    example_id: str
    predicted_output: str
    expected_output: str
    exact_match: bool
    score: float
    metrics: Dict[str, float]
    passed: bool
    failure_reason: Optional[str] = None
    latency_ms: Optional[float] = None
    model_version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "example_id": self.example_id,
            "predicted_output": self.predicted_output,
            "expected_output": self.expected_output,
            "exact_match": self.exact_match,
            "score": round(self.score, 4),
            "metrics": {k: round(v, 4) for k, v in self.metrics.items()},
            "passed": self.passed,
            "failure_reason": self.failure_reason,
            "latency_ms": round(self.latency_ms, 2) if self.latency_ms else None,
            "model_version": self.model_version
        }


@dataclass
class EvaluationSummary:
    """
    Summary of evaluation run across all examples.
    
    Attributes:
        run_id: Unique identifier for this evaluation run
        model_version: Which model version was evaluated
        total_examples: Number of examples evaluated
        passed_examples: Number that passed
        failed_examples: Number that failed
        pass_rate: Percentage that passed
        avg_score: Average score across all examples
        avg_latency_ms: Average inference latency
        metrics_summary: Aggregated metrics
        evaluated_at: When evaluation was run
    """
    run_id: str
    model_version: str
    total_examples: int
    passed_examples: int
    failed_examples: int
    pass_rate: float
    avg_score: float
    avg_latency_ms: float
    metrics_summary: Dict[str, float]
    evaluated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "model_version": self.model_version,
            "total_examples": self.total_examples,
            "passed_examples": self.passed_examples,
            "failed_examples": self.failed_examples,
            "pass_rate": round(self.pass_rate, 4),
            "avg_score": round(self.avg_score, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "metrics_summary": {k: round(v, 4) for k, v in self.metrics_summary.items()},
            "evaluated_at": self.evaluated_at
        }


class GoldenDataset:
    """
    Manages golden evaluation datasets.
    
    A golden dataset is a curated set of examples with known correct outputs.
    These are used to evaluate model performance and detect regressions.
    """
    
    def __init__(self, dataset_path: Optional[Path] = None):
        """
        Initialize dataset manager.
        
        Args:
            dataset_path: Path to JSON file containing golden examples
        """
        self.dataset_path = dataset_path
        self.examples: List[GoldenExample] = []
        
        if dataset_path and dataset_path.exists():
            self.load()
    
    def add_example(self, example: GoldenExample) -> None:
        """Add an example to the dataset."""
        self.examples.append(example)
    
    def get_example(self, example_id: str) -> Optional[GoldenExample]:
        """Get example by ID."""
        for example in self.examples:
            if example.id == example_id:
                return example
        return None
    
    def get_examples_by_task(self, task_type: str) -> List[GoldenExample]:
        """Get all examples for a specific task type."""
        return [ex for ex in self.examples if ex.task_type == task_type]
    
    def load(self) -> None:
        """Load dataset from file."""
        if not self.dataset_path or not self.dataset_path.exists():
            return
        
        with open(self.dataset_path, 'r') as f:
            data = json.load(f)
        
        self.examples = [GoldenExample.from_dict(ex) for ex in data.get("examples", [])]
    
    def save(self) -> None:
        """Save dataset to file."""
        if not self.dataset_path:
            raise ValueError("No dataset_path specified")
        
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "total_examples": len(self.examples),
            "examples": [ex.to_dict() for ex in self.examples]
        }
        
        with open(self.dataset_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def __len__(self) -> int:
        """Return number of examples."""
        return len(self.examples)


class Evaluator:
    """
    Evaluates model performance against golden dataset.
    
    This class runs systematic evaluation, calculates metrics,
    and detects regressions.
    """
    
    def __init__(self, dataset: GoldenDataset):
        """
        Initialize evaluator.
        
        Args:
            dataset: Golden dataset to evaluate against
        """
        self.dataset = dataset
    
    def exact_match(self, predicted: str, expected: str) -> bool:
        """
        Check if prediction exactly matches expected output.
        
        Args:
            predicted: Model's prediction
            expected: Expected output
            
        Returns:
            True if exact match (case-insensitive, whitespace-normalized)
        """
        pred_normalized = predicted.strip().lower()
        exp_normalized = expected.strip().lower()
        return pred_normalized == exp_normalized
    
    def fuzzy_match_score(self, predicted: str, expected: str) -> float:
        """
        Calculate fuzzy match score between prediction and expected.
        
        Uses character-level similarity. For production, consider:
        - ROUGE scores for summarization
        - BLEU scores for generation
        - Semantic similarity for meaning preservation
        
        Args:
            predicted: Model's prediction
            expected: Expected output
            
        Returns:
            Score from 0.0 (no match) to 1.0 (perfect match)
        """
        if not predicted or not expected:
            return 0.0
        
        # Simple token overlap for now
        pred_tokens = set(predicted.lower().split())
        exp_tokens = set(expected.lower().split())
        
        if not exp_tokens:
            return 0.0
        
        intersection = pred_tokens & exp_tokens
        union = pred_tokens | exp_tokens
        
        # Jaccard similarity
        return len(intersection) / len(union) if union else 0.0
    
    def evaluate_example(
        self,
        example: GoldenExample,
        model_fn: Callable[[str], str],
        pass_threshold: float = 0.85,
        model_version: str = "unknown"
    ) -> EvaluationResult:
        """
        Evaluate a single example.
        
        Args:
            example: Golden example to evaluate
            model_fn: Function that takes input text and returns prediction
            pass_threshold: Minimum score to consider passing
            model_version: Identifier for model being evaluated
            
        Returns:
            EvaluationResult with scores and metrics
        """
        import time
        
        # Run inference
        start_time = time.time()
        predicted = model_fn(example.input_text)
        latency_ms = (time.time() - start_time) * 1000
        
        # Calculate metrics
        exact = self.exact_match(predicted, example.expected_output)
        fuzzy_score = self.fuzzy_match_score(predicted, example.expected_output)
        
        # Task-specific metrics
        metrics = {
            "fuzzy_match": fuzzy_score,
            "length_ratio": len(predicted) / len(example.expected_output) if example.expected_output else 0.0
        }
        
        # Determine pass/fail
        passed = exact or fuzzy_score >= pass_threshold
        failure_reason = None
        if not passed:
            if fuzzy_score < pass_threshold:
                failure_reason = f"Score {fuzzy_score:.3f} below threshold {pass_threshold}"
        
        return EvaluationResult(
            example_id=example.id,
            predicted_output=predicted,
            expected_output=example.expected_output,
            exact_match=exact,
            score=fuzzy_score,
            metrics=metrics,
            passed=passed,
            failure_reason=failure_reason,
            latency_ms=latency_ms,
            model_version=model_version
        )
    
    def evaluate_all(
        self,
        model_fn: Callable[[str], str],
        task_type: Optional[str] = None,
        pass_threshold: float = 0.85,
        model_version: str = "unknown"
    ) -> Tuple[List[EvaluationResult], EvaluationSummary]:
        """
        Evaluate all examples (or filtered by task type).
        
        Args:
            model_fn: Function that takes input text and returns prediction
            task_type: Optional filter by task type
            pass_threshold: Minimum score to consider passing
            model_version: Identifier for model being evaluated
            
        Returns:
            Tuple of (individual results, summary)
        """
        # Get examples to evaluate
        if task_type:
            examples = self.dataset.get_examples_by_task(task_type)
        else:
            examples = self.dataset.examples
        
        if not examples:
            raise ValueError(f"No examples found for task_type={task_type}")
        
        # Evaluate each example
        results = []
        for example in examples:
            result = self.evaluate_example(
                example=example,
                model_fn=model_fn,
                pass_threshold=pass_threshold,
                model_version=model_version
            )
            results.append(result)
        
        # Calculate summary statistics
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        avg_score = statistics.mean(r.score for r in results)
        latencies = [r.latency_ms for r in results if r.latency_ms]
        avg_latency = statistics.mean(latencies) if latencies else 0.0
        
        # Aggregate metrics
        all_metrics = {}
        for result in results:
            for key, value in result.metrics.items():
                if key not in all_metrics:
                    all_metrics[key] = []
                all_metrics[key].append(value)
        
        metrics_summary = {
            key: statistics.mean(values)
            for key, values in all_metrics.items()
        }
        
        summary = EvaluationSummary(
            run_id=str(uuid4()),
            model_version=model_version,
            total_examples=len(results),
            passed_examples=passed,
            failed_examples=failed,
            pass_rate=passed / len(results) if results else 0.0,
            avg_score=avg_score,
            avg_latency_ms=avg_latency,
            metrics_summary=metrics_summary
        )
        
        return results, summary


class RegressionDetector:
    """
    Detects performance regressions between model versions.
    
    Compares evaluation results to determine if a new model
    version performs worse than the baseline.
    """
    
    @staticmethod
    def detect_regression(
        baseline_summary: EvaluationSummary,
        current_summary: EvaluationSummary,
        pass_rate_threshold: float = 0.02,  # 2% drop
        score_threshold: float = 0.05  # 5% drop
    ) -> Tuple[bool, str]:
        """
        Detect if current version regressed compared to baseline.
        
        Args:
            baseline_summary: Summary from baseline model
            current_summary: Summary from current model
            pass_rate_threshold: Maximum acceptable drop in pass rate
            score_threshold: Maximum acceptable drop in average score
            
        Returns:
            Tuple of (is_regression, reason)
        """
        pass_rate_drop = baseline_summary.pass_rate - current_summary.pass_rate
        score_drop = baseline_summary.avg_score - current_summary.avg_score
        
        if pass_rate_drop > pass_rate_threshold:
            return True, f"Pass rate dropped by {pass_rate_drop:.1%} (threshold {pass_rate_threshold:.1%})"
        
        if score_drop > score_threshold:
            return True, f"Average score dropped by {score_drop:.1%} (threshold {score_threshold:.1%})"
        
        return False, "No regression detected"
    
    @staticmethod
    def compare_versions(
        baseline_summary: EvaluationSummary,
        current_summary: EvaluationSummary
    ) -> Dict[str, Any]:
        """
        Generate detailed comparison between two versions.
        
        Args:
            baseline_summary: Summary from baseline model
            current_summary: Summary from current model
            
        Returns:
            Dictionary with comparison metrics
        """
        pass_rate_diff = current_summary.pass_rate - baseline_summary.pass_rate
        score_diff = current_summary.avg_score - baseline_summary.avg_score
        latency_diff = current_summary.avg_latency_ms - baseline_summary.avg_latency_ms
        
        return {
            "baseline_version": baseline_summary.model_version,
            "current_version": current_summary.model_version,
            "pass_rate_change": pass_rate_diff,
            "pass_rate_change_pct": (pass_rate_diff / baseline_summary.pass_rate * 100) if baseline_summary.pass_rate > 0 else 0,
            "score_change": score_diff,
            "score_change_pct": (score_diff / baseline_summary.avg_score * 100) if baseline_summary.avg_score > 0 else 0,
            "latency_change_ms": latency_diff,
            "latency_change_pct": (latency_diff / baseline_summary.avg_latency_ms * 100) if baseline_summary.avg_latency_ms > 0 else 0,
            "baseline_passed": baseline_summary.passed_examples,
            "current_passed": current_summary.passed_examples,
            "baseline_failed": baseline_summary.failed_examples,
            "current_failed": current_summary.failed_examples
        }


def save_evaluation_results(
    results: List[EvaluationResult],
    summary: EvaluationSummary,
    output_path: Path
) -> None:
    """
    Save evaluation results to JSON file.
    
    Args:
        results: Individual evaluation results
        summary: Evaluation summary
        output_path: Path to save results
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "summary": summary.to_dict(),
        "results": [r.to_dict() for r in results]
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_evaluation_results(input_path: Path) -> Tuple[List[Dict], Dict]:
    """
    Load evaluation results from JSON file.
    
    Args:
        input_path: Path to results file
        
    Returns:
        Tuple of (results list, summary dict)
    """
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    return data.get("results", []), data.get("summary", {})