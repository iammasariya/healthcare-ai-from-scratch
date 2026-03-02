"""
Tests for evaluation harness (Post 5)
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.evaluation import (
    GoldenExample,
    GoldenDataset,
    EvaluationResult,
    EvaluationSummary,
    Evaluator,
    RegressionDetector,
    save_evaluation_results,
    load_evaluation_results
)


class TestGoldenExample:
    """Tests for GoldenExample dataclass."""
    
    def test_example_creation(self):
        """Test creating a golden example."""
        example = GoldenExample(
            id="test-001",
            input_text="Patient presents with headache.",
            expected_output="Headache reported.",
            task_type="summarization",
            metadata={"difficulty": "easy"}
        )
        
        assert example.id == "test-001"
        assert example.task_type == "summarization"
        assert example.metadata["difficulty"] == "easy"
        assert example.created_by == "system"
    
    def test_example_to_dict(self):
        """Test converting example to dictionary."""
        example = GoldenExample(
            id="test-001",
            input_text="Input text",
            expected_output="Expected output",
            task_type="summarization"
        )
        
        data = example.to_dict()
        assert data["id"] == "test-001"
        assert data["task_type"] == "summarization"
        assert "created_at" in data
    
    def test_example_from_dict(self):
        """Test creating example from dictionary."""
        data = {
            "id": "test-001",
            "input_text": "Input",
            "expected_output": "Output",
            "task_type": "extraction",
            "metadata": {"source": "clinic"}
        }
        
        example = GoldenExample.from_dict(data)
        assert example.id == "test-001"
        assert example.task_type == "extraction"
        assert example.metadata["source"] == "clinic"


class TestGoldenDataset:
    """Tests for GoldenDataset class."""
    
    def test_dataset_initialization(self):
        """Test initializing empty dataset."""
        dataset = GoldenDataset()
        assert len(dataset) == 0
    
    def test_add_example(self):
        """Test adding example to dataset."""
        dataset = GoldenDataset()
        example = GoldenExample(
            id="test-001",
            input_text="Input",
            expected_output="Output",
            task_type="summarization"
        )
        
        dataset.add_example(example)
        assert len(dataset) == 1
    
    def test_get_example(self):
        """Test retrieving example by ID."""
        dataset = GoldenDataset()
        example = GoldenExample(
            id="test-001",
            input_text="Input",
            expected_output="Output",
            task_type="summarization"
        )
        dataset.add_example(example)
        
        retrieved = dataset.get_example("test-001")
        assert retrieved is not None
        assert retrieved.id == "test-001"
    
    def test_get_example_not_found(self):
        """Test retrieving nonexistent example."""
        dataset = GoldenDataset()
        result = dataset.get_example("nonexistent")
        assert result is None
    
    def test_get_examples_by_task(self):
        """Test filtering examples by task type."""
        dataset = GoldenDataset()
        dataset.add_example(GoldenExample(
            id="sum-001",
            input_text="Input 1",
            expected_output="Output 1",
            task_type="summarization"
        ))
        dataset.add_example(GoldenExample(
            id="ext-001",
            input_text="Input 2",
            expected_output="Output 2",
            task_type="extraction"
        ))
        dataset.add_example(GoldenExample(
            id="sum-002",
            input_text="Input 3",
            expected_output="Output 3",
            task_type="summarization"
        ))
        
        summaries = dataset.get_examples_by_task("summarization")
        assert len(summaries) == 2
        assert all(ex.task_type == "summarization" for ex in summaries)
    
    def test_save_and_load(self):
        """Test saving and loading dataset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "golden.json"
            
            # Create and save dataset
            dataset = GoldenDataset(path)
            dataset.add_example(GoldenExample(
                id="test-001",
                input_text="Input text",
                expected_output="Expected output",
                task_type="summarization"
            ))
            dataset.save()
            
            # Load dataset
            loaded = GoldenDataset(path)
            assert len(loaded) == 1
            assert loaded.examples[0].id == "test-001"


class TestEvaluator:
    """Tests for Evaluator class."""
    
    def test_exact_match_true(self):
        """Test exact match detection (positive case)."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        assert evaluator.exact_match("Hello World", "Hello World")
        assert evaluator.exact_match("hello world", "HELLO WORLD")  # Case insensitive
        assert evaluator.exact_match("  hello  ", "hello")  # Whitespace normalized
    
    def test_exact_match_false(self):
        """Test exact match detection (negative case)."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        assert not evaluator.exact_match("Hello", "Goodbye")
        assert not evaluator.exact_match("Hello World", "Hello")
    
    def test_fuzzy_match_score_identical(self):
        """Test fuzzy match with identical strings."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        score = evaluator.fuzzy_match_score("patient presents with headache", 
                                            "patient presents with headache")
        assert score == 1.0
    
    def test_fuzzy_match_score_similar(self):
        """Test fuzzy match with similar strings."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        score = evaluator.fuzzy_match_score("patient has headache", 
                                            "patient presents with headache")
        assert 0.3 < score < 0.7  # Jaccard similarity for similar but not identical
    
    def test_fuzzy_match_score_different(self):
        """Test fuzzy match with different strings."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        score = evaluator.fuzzy_match_score("completely different text",
                                            "patient presents with headache")
        assert score < 0.5
    
    def test_fuzzy_match_score_empty(self):
        """Test fuzzy match with empty strings."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        assert evaluator.fuzzy_match_score("", "test") == 0.0
        assert evaluator.fuzzy_match_score("test", "") == 0.0
    
    def test_evaluate_example_exact_match(self):
        """Test evaluating example with exact match."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        example = GoldenExample(
            id="test-001",
            input_text="Input text",
            expected_output="expected output",
            task_type="summarization"
        )
        
        # Model function that returns expected output
        def model_fn(text: str) -> str:
            return "expected output"
        
        result = evaluator.evaluate_example(example, model_fn, model_version="v1.0")
        
        assert result.exact_match is True
        assert result.passed is True
        assert result.score >= 0.99
        assert result.model_version == "v1.0"
        assert result.latency_ms is not None
    
    def test_evaluate_example_fuzzy_match(self):
        """Test evaluating example with fuzzy match."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        example = GoldenExample(
            id="test-001",
            input_text="Input text",
            expected_output="patient has headache",
            task_type="summarization"
        )
        
        # Model function that returns similar but not exact
        def model_fn(text: str) -> str:
            return "patient presents with headache"
        
        result = evaluator.evaluate_example(
            example, model_fn, pass_threshold=0.3, model_version="v1.0"
        )
        
        assert result.exact_match is False
        assert result.passed is True  # Should pass fuzzy threshold
        assert 0.3 < result.score < 0.7  # Jaccard similarity range
    
    def test_evaluate_example_failure(self):
        """Test evaluating example that fails."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        example = GoldenExample(
            id="test-001",
            input_text="Input text",
            expected_output="expected output",
            task_type="summarization"
        )
        
        # Model function that returns wrong output
        def model_fn(text: str) -> str:
            return "completely wrong output"
        
        result = evaluator.evaluate_example(
            example, model_fn, pass_threshold=0.85, model_version="v1.0"
        )
        
        assert result.passed is False
        assert result.failure_reason is not None
        assert "below threshold" in result.failure_reason
    
    def test_evaluate_all(self):
        """Test evaluating all examples."""
        dataset = GoldenDataset()
        dataset.add_example(GoldenExample(
            id="test-001",
            input_text="Input 1",
            expected_output="output 1",
            task_type="summarization"
        ))
        dataset.add_example(GoldenExample(
            id="test-002",
            input_text="Input 2",
            expected_output="output 2",
            task_type="summarization"
        ))
        
        evaluator = Evaluator(dataset)
        
        # Model that returns correct outputs
        def model_fn(text: str) -> str:
            if "Input 1" in text:
                return "output 1"
            return "output 2"
        
        results, summary = evaluator.evaluate_all(model_fn, model_version="v1.0")
        
        assert len(results) == 2
        assert summary.total_examples == 2
        assert summary.passed_examples == 2
        assert summary.pass_rate == 1.0
        assert summary.model_version == "v1.0"
    
    def test_evaluate_all_filtered_by_task(self):
        """Test evaluating filtered by task type."""
        dataset = GoldenDataset()
        dataset.add_example(GoldenExample(
            id="sum-001",
            input_text="Input 1",
            expected_output="output 1",
            task_type="summarization"
        ))
        dataset.add_example(GoldenExample(
            id="ext-001",
            input_text="Input 2",
            expected_output="output 2",
            task_type="extraction"
        ))
        
        evaluator = Evaluator(dataset)
        
        def model_fn(text: str) -> str:
            return "output 1" if "Input 1" in text else "output 2"
        
        # Evaluate only summarization tasks
        results, summary = evaluator.evaluate_all(
            model_fn, task_type="summarization", model_version="v1.0"
        )
        
        assert len(results) == 1
        assert summary.total_examples == 1
    
    def test_evaluate_all_empty_dataset(self):
        """Test evaluating with no examples."""
        dataset = GoldenDataset()
        evaluator = Evaluator(dataset)
        
        def model_fn(text: str) -> str:
            return "output"
        
        with pytest.raises(ValueError, match="No examples found"):
            evaluator.evaluate_all(model_fn)


class TestRegressionDetector:
    """Tests for RegressionDetector class."""
    
    def test_no_regression(self):
        """Test detecting no regression."""
        baseline = EvaluationSummary(
            run_id="baseline",
            model_version="v1.0",
            total_examples=100,
            passed_examples=95,
            failed_examples=5,
            pass_rate=0.95,
            avg_score=0.92,
            avg_latency_ms=500.0,
            metrics_summary={}
        )
        
        current = EvaluationSummary(
            run_id="current",
            model_version="v1.1",
            total_examples=100,
            passed_examples=96,
            failed_examples=4,
            pass_rate=0.96,
            avg_score=0.93,
            avg_latency_ms=480.0,
            metrics_summary={}
        )
        
        is_regression, reason = RegressionDetector.detect_regression(baseline, current)
        assert is_regression is False
        assert "No regression" in reason
    
    def test_pass_rate_regression(self):
        """Test detecting pass rate regression."""
        baseline = EvaluationSummary(
            run_id="baseline",
            model_version="v1.0",
            total_examples=100,
            passed_examples=95,
            failed_examples=5,
            pass_rate=0.95,
            avg_score=0.92,
            avg_latency_ms=500.0,
            metrics_summary={}
        )
        
        current = EvaluationSummary(
            run_id="current",
            model_version="v1.1",
            total_examples=100,
            passed_examples=90,
            failed_examples=10,
            pass_rate=0.90,
            avg_score=0.91,
            avg_latency_ms=480.0,
            metrics_summary={}
        )
        
        is_regression, reason = RegressionDetector.detect_regression(
            baseline, current, pass_rate_threshold=0.02
        )
        assert is_regression is True
        assert "Pass rate dropped" in reason
    
    def test_score_regression(self):
        """Test detecting score regression."""
        baseline = EvaluationSummary(
            run_id="baseline",
            model_version="v1.0",
            total_examples=100,
            passed_examples=95,
            failed_examples=5,
            pass_rate=0.95,
            avg_score=0.92,
            avg_latency_ms=500.0,
            metrics_summary={}
        )
        
        current = EvaluationSummary(
            run_id="current",
            model_version="v1.1",
            total_examples=100,
            passed_examples=95,
            failed_examples=5,
            pass_rate=0.95,
            avg_score=0.85,
            avg_latency_ms=480.0,
            metrics_summary={}
        )
        
        is_regression, reason = RegressionDetector.detect_regression(
            baseline, current, score_threshold=0.05
        )
        assert is_regression is True
        assert "score dropped" in reason
    
    def test_compare_versions(self):
        """Test comparing two versions."""
        baseline = EvaluationSummary(
            run_id="baseline",
            model_version="v1.0",
            total_examples=100,
            passed_examples=95,
            failed_examples=5,
            pass_rate=0.95,
            avg_score=0.92,
            avg_latency_ms=500.0,
            metrics_summary={}
        )
        
        current = EvaluationSummary(
            run_id="current",
            model_version="v1.1",
            total_examples=100,
            passed_examples=96,
            failed_examples=4,
            pass_rate=0.96,
            avg_score=0.94,
            avg_latency_ms=450.0,
            metrics_summary={}
        )
        
        comparison = RegressionDetector.compare_versions(baseline, current)
        
        assert comparison["baseline_version"] == "v1.0"
        assert comparison["current_version"] == "v1.1"
        assert comparison["pass_rate_change"] > 0
        assert comparison["score_change"] > 0
        assert comparison["latency_change_ms"] < 0  # Improved (faster)


class TestSaveLoad:
    """Tests for saving and loading results."""
    
    def test_save_and_load_results(self):
        """Test saving and loading evaluation results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.json"
            
            # Create some results
            results = [
                EvaluationResult(
                    example_id="test-001",
                    predicted_output="prediction 1",
                    expected_output="expected 1",
                    exact_match=True,
                    score=1.0,
                    metrics={"fuzzy_match": 1.0},
                    passed=True,
                    latency_ms=100.0,
                    model_version="v1.0"
                )
            ]
            
            summary = EvaluationSummary(
                run_id="test-run",
                model_version="v1.0",
                total_examples=1,
                passed_examples=1,
                failed_examples=0,
                pass_rate=1.0,
                avg_score=1.0,
                avg_latency_ms=100.0,
                metrics_summary={"fuzzy_match": 1.0}
            )
            
            # Save
            save_evaluation_results(results, summary, output_path)
            
            # Load
            loaded_results, loaded_summary = load_evaluation_results(output_path)
            
            assert len(loaded_results) == 1
            assert loaded_results[0]["example_id"] == "test-001"
            assert loaded_summary["model_version"] == "v1.0"
            assert loaded_summary["pass_rate"] == 1.0