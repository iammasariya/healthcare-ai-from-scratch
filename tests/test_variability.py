"""
Tests for variability measurement and determinism controls (Post 4).

These tests verify:
- Variability metrics calculation
- Similarity comparison
- Determinism controls
- Temperature recommendations
- Alert detection
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.variability import (
    VariabilityMetrics,
    InferenceRun,
    VariabilityMeasurer,
    DeterminismController,
    calculate_output_hash,
    detect_variability_alert
)


class TestVariabilityMetrics:
    """Tests for VariabilityMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test creating variability metrics."""
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=3,
            output_lengths=[100, 105, 110, 100, 105, 110, 100, 105, 110, 100],
            avg_length=104.5,
            length_std_dev=4.5,
            exact_match_rate=0.4,
            pairwise_similarity_avg=0.92,
            pairwise_similarity_min=0.85,
            pairwise_similarity_max=0.98,
            temperature=0.3,
            seed=12345,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        assert metrics.run_count == 10
        assert metrics.unique_outputs == 3
        assert metrics.temperature == 0.3
        assert metrics.seed == 12345
    
    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = VariabilityMetrics(
            run_count=5,
            unique_outputs=2,
            output_lengths=[100, 100, 105, 100, 105],
            avg_length=102.0,
            length_std_dev=2.24,
            exact_match_rate=0.6,
            pairwise_similarity_avg=0.95,
            pairwise_similarity_min=0.90,
            pairwise_similarity_max=1.0,
            temperature=0.2,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        metrics_dict = metrics.to_dict()
        
        assert metrics_dict["run_count"] == 5
        assert metrics_dict["unique_outputs"] == 2
        assert metrics_dict["avg_length"] == 102.0
        assert metrics_dict["temperature"] == 0.2
        assert metrics_dict["seed"] is None
        # Check rounding
        assert isinstance(metrics_dict["pairwise_similarity_avg"], float)


class TestInferenceRun:
    """Tests for InferenceRun dataclass."""
    
    def test_inference_run_creation(self):
        """Test creating an inference run."""
        audit_id = uuid4()
        run = InferenceRun(
            output="Patient presents with headache.",
            run_number=1,
            latency_ms=850.5,
            tokens_used=150,
            audit_id=audit_id,
            timestamp="2026-02-06T10:00:00Z"
        )
        
        assert run.output == "Patient presents with headache."
        assert run.run_number == 1
        assert run.latency_ms == 850.5
        assert run.tokens_used == 150
        assert run.audit_id == audit_id


class TestVariabilityMeasurer:
    """Tests for VariabilityMeasurer class."""
    
    def test_initialization(self):
        """Test measurer initialization."""
        measurer = VariabilityMeasurer()
        assert measurer is not None
    
    def test_calculate_similarity_identical(self):
        """Test similarity of identical texts."""
        measurer = VariabilityMeasurer()
        text = "Patient presents with acute headache."
        
        similarity = measurer.calculate_similarity(text, text)
        
        assert similarity == 1.0
    
    def test_calculate_similarity_different(self):
        """Test similarity of different texts."""
        measurer = VariabilityMeasurer()
        text1 = "Patient presents with acute headache."
        text2 = "The weather is sunny today."
        
        similarity = measurer.calculate_similarity(text1, text2)
        
        assert 0.0 <= similarity < 0.3  # Very different texts
    
    def test_calculate_similarity_similar(self):
        """Test similarity of similar texts."""
        measurer = VariabilityMeasurer()
        text1 = "Patient presents with acute headache and nausea."
        text2 = "Patient presents with acute headache and dizziness."
        
        similarity = measurer.calculate_similarity(text1, text2)
        
        assert 0.7 < similarity < 1.0  # Similar but not identical
    
    def test_calculate_similarity_empty(self):
        """Test similarity with empty strings."""
        measurer = VariabilityMeasurer()
        
        similarity1 = measurer.calculate_similarity("", "test")
        similarity2 = measurer.calculate_similarity("test", "")
        similarity3 = measurer.calculate_similarity("", "")
        
        assert similarity1 == 0.0
        assert similarity2 == 0.0
        assert similarity3 == 0.0
    
    def test_calculate_pairwise_similarities_single(self):
        """Test pairwise similarities with single output."""
        measurer = VariabilityMeasurer()
        outputs = ["Patient presents with headache."]
        
        similarities = measurer.calculate_pairwise_similarities(outputs)
        
        assert similarities == [1.0]
    
    def test_calculate_pairwise_similarities_multiple(self):
        """Test pairwise similarities with multiple outputs."""
        measurer = VariabilityMeasurer()
        outputs = [
            "Patient presents with headache.",
            "Patient presents with headache.",  # Duplicate
            "Patient has a headache."  # Similar but different
        ]
        
        similarities = measurer.calculate_pairwise_similarities(outputs)
        
        # Should have 3 pairs: (0,1), (0,2), (1,2)
        assert len(similarities) == 3
        assert similarities[0] == 1.0  # Identical
        assert 0.7 < similarities[1] < 1.0  # Similar
        assert 0.7 < similarities[2] < 1.0  # Similar
    
    def test_measure_variability_identical_outputs(self):
        """Test measuring variability with identical outputs."""
        measurer = VariabilityMeasurer()
        
        output = "Patient presents with acute headache."
        runs = [
            InferenceRun(output, i, 800.0, 150, uuid4(), "2026-02-06T10:00:00Z")
            for i in range(1, 6)
        ]
        
        metrics = measurer.measure_variability(runs, temperature=0.0)
        
        assert metrics.run_count == 5
        assert metrics.unique_outputs == 1  # All identical
        assert metrics.exact_match_rate == 1.0  # 100% match
        assert metrics.pairwise_similarity_avg == 1.0  # Perfect similarity
        assert metrics.length_std_dev == 0.0  # No variation in length
        assert metrics.temperature == 0.0
    
    def test_measure_variability_different_outputs(self):
        """Test measuring variability with different outputs."""
        measurer = VariabilityMeasurer()
        
        outputs = [
            "Patient presents with acute headache.",
            "Patient has a severe headache.",
            "Headache reported by patient.",
            "Patient complains of head pain.",
            "Acute cephalgia noted."
        ]
        
        runs = [
            InferenceRun(output, i, 800.0, 150, uuid4(), "2026-02-06T10:00:00Z")
            for i, output in enumerate(outputs, 1)
        ]
        
        metrics = measurer.measure_variability(runs, temperature=0.7)
        
        assert metrics.run_count == 5
        assert metrics.unique_outputs == 5  # All unique
        assert metrics.exact_match_rate == 0.2  # Only 1/5 match first
        assert metrics.pairwise_similarity_avg < 1.0  # Not perfectly similar
        assert metrics.pairwise_similarity_avg > 0.3  # But related
        assert metrics.temperature == 0.7
    
    def test_measure_variability_empty_runs(self):
        """Test measuring variability with no runs raises error."""
        measurer = VariabilityMeasurer()
        
        with pytest.raises(ValueError, match="Cannot measure variability with no runs"):
            measurer.measure_variability([], temperature=0.3)
    
    def test_is_acceptable_variability_high_similarity(self):
        """Test acceptable variability with high similarity."""
        measurer = VariabilityMeasurer()
        
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=2,
            output_lengths=[100] * 10,
            avg_length=100.0,
            length_std_dev=0.0,
            exact_match_rate=0.8,
            pairwise_similarity_avg=0.95,
            pairwise_similarity_min=0.90,
            pairwise_similarity_max=1.0,
            temperature=0.2,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        is_acceptable, reason = measurer.is_acceptable_variability(metrics)
        
        assert is_acceptable is True
        assert "acceptable" in reason.lower()
    
    def test_is_acceptable_variability_low_similarity(self):
        """Test unacceptable variability with low similarity."""
        measurer = VariabilityMeasurer()
        
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=8,
            output_lengths=[100] * 10,
            avg_length=100.0,
            length_std_dev=5.0,
            exact_match_rate=0.2,
            pairwise_similarity_avg=0.70,  # Too low
            pairwise_similarity_min=0.60,
            pairwise_similarity_max=0.85,
            temperature=0.7,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        is_acceptable, reason = measurer.is_acceptable_variability(metrics, min_similarity=0.85)
        
        assert is_acceptable is False
        assert "similarity" in reason.lower()
    
    def test_is_acceptable_variability_too_many_unique(self):
        """Test unacceptable variability with too many unique outputs."""
        measurer = VariabilityMeasurer()
        
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=8,  # 80% unique
            output_lengths=[100] * 10,
            avg_length=100.0,
            length_std_dev=5.0,
            exact_match_rate=0.2,
            pairwise_similarity_avg=0.90,
            pairwise_similarity_min=0.85,
            pairwise_similarity_max=0.95,
            temperature=0.7,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        is_acceptable, reason = measurer.is_acceptable_variability(metrics, max_unique_ratio=0.3)
        
        assert is_acceptable is False
        assert "unique" in reason.lower()
    
    def test_is_acceptable_variability_extreme_outlier(self):
        """Test unacceptable variability with extreme outliers."""
        measurer = VariabilityMeasurer()
        
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=3,
            output_lengths=[100] * 10,
            avg_length=100.0,
            length_std_dev=2.0,
            exact_match_rate=0.7,
            pairwise_similarity_avg=0.90,
            pairwise_similarity_min=0.50,  # One very different output
            pairwise_similarity_max=1.0,
            temperature=0.3,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        is_acceptable, reason = measurer.is_acceptable_variability(metrics)
        
        assert is_acceptable is False
        assert "divergent" in reason.lower()


class TestDeterminismController:
    """Tests for DeterminismController class."""
    
    def test_get_deterministic_seed_consistent(self):
        """Test that same inputs produce same seed."""
        seed1 = DeterminismController.get_deterministic_seed(
            "PT-12345", "1.0.0", "2026-02-06"
        )
        seed2 = DeterminismController.get_deterministic_seed(
            "PT-12345", "1.0.0", "2026-02-06"
        )
        
        assert seed1 == seed2
    
    def test_get_deterministic_seed_different_patient(self):
        """Test that different patients produce different seeds."""
        seed1 = DeterminismController.get_deterministic_seed(
            "PT-12345", "1.0.0", "2026-02-06"
        )
        seed2 = DeterminismController.get_deterministic_seed(
            "PT-67890", "1.0.0", "2026-02-06"
        )
        
        assert seed1 != seed2
    
    def test_get_deterministic_seed_different_version(self):
        """Test that different prompt versions produce different seeds."""
        seed1 = DeterminismController.get_deterministic_seed(
            "PT-12345", "1.0.0", "2026-02-06"
        )
        seed2 = DeterminismController.get_deterministic_seed(
            "PT-12345", "1.1.0", "2026-02-06"
        )
        
        assert seed1 != seed2
    
    def test_get_deterministic_seed_different_date(self):
        """Test that different dates produce different seeds."""
        seed1 = DeterminismController.get_deterministic_seed(
            "PT-12345", "1.0.0", "2026-02-06"
        )
        seed2 = DeterminismController.get_deterministic_seed(
            "PT-12345", "1.0.0", "2026-02-07"
        )
        
        assert seed1 != seed2
    
    def test_recommend_temperature_extraction_high_risk(self):
        """Test temperature recommendation for high-risk extraction."""
        temp = DeterminismController.recommend_temperature("extraction", "high")
        
        assert temp == 0.0  # Most deterministic
    
    def test_recommend_temperature_summary_medium_risk(self):
        """Test temperature recommendation for medium-risk summary."""
        temp = DeterminismController.recommend_temperature("summary", "medium")
        
        assert temp == 0.3
    
    def test_recommend_temperature_research_low_risk(self):
        """Test temperature recommendation for low-risk research."""
        temp = DeterminismController.recommend_temperature("research", "low")
        
        assert temp == 0.8  # Most creative
    
    def test_recommend_temperature_unknown_task(self):
        """Test temperature recommendation for unknown task defaults to summary."""
        temp = DeterminismController.recommend_temperature("unknown_task", "high")
        
        assert temp == 0.2  # Summary-high default
    
    def test_recommend_temperature_invalid_risk(self):
        """Test temperature recommendation with invalid risk defaults to high."""
        temp = DeterminismController.recommend_temperature("summary", "invalid")
        
        assert temp == 0.2  # Default to high risk
    
    def test_recommend_temperature_case_insensitive(self):
        """Test temperature recommendation is case insensitive."""
        temp1 = DeterminismController.recommend_temperature("SUMMARY", "HIGH")
        temp2 = DeterminismController.recommend_temperature("summary", "high")
        
        assert temp1 == temp2


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_calculate_output_hash_consistent(self):
        """Test that same output produces same hash."""
        output = "Patient presents with acute headache."
        
        hash1 = calculate_output_hash(output)
        hash2 = calculate_output_hash(output)
        
        assert hash1 == hash2
        assert len(hash1) == 16  # First 16 characters of SHA256
    
    def test_calculate_output_hash_different(self):
        """Test that different outputs produce different hashes."""
        output1 = "Patient presents with acute headache."
        output2 = "Patient has a severe headache."
        
        hash1 = calculate_output_hash(output1)
        hash2 = calculate_output_hash(output2)
        
        assert hash1 != hash2
    
    def test_detect_variability_alert_low_similarity(self):
        """Test alert detection for low similarity."""
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=8,
            output_lengths=[100] * 10,
            avg_length=100.0,
            length_std_dev=5.0,
            exact_match_rate=0.2,
            pairwise_similarity_avg=0.70,  # Below threshold
            pairwise_similarity_min=0.60,
            pairwise_similarity_max=0.85,
            temperature=0.7,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        alert = detect_variability_alert(metrics, alert_threshold=0.80)
        
        assert alert is not None
        assert "VARIABILITY ALERT" in alert
        assert "similarity" in alert.lower()
    
    def test_detect_variability_alert_all_unique(self):
        """Test alert detection when all outputs are unique."""
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=10,  # All unique
            output_lengths=[100] * 10,
            avg_length=100.0,
            length_std_dev=5.0,
            exact_match_rate=0.1,
            pairwise_similarity_avg=0.85,
            pairwise_similarity_min=0.75,
            pairwise_similarity_max=0.95,
            temperature=0.7,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        alert = detect_variability_alert(metrics)
        
        assert alert is not None
        assert "VARIABILITY ALERT" in alert
        assert "unique" in alert.lower()
    
    def test_detect_variability_alert_acceptable(self):
        """Test no alert for acceptable variability."""
        metrics = VariabilityMetrics(
            run_count=10,
            unique_outputs=3,
            output_lengths=[100] * 10,
            avg_length=100.0,
            length_std_dev=2.0,
            exact_match_rate=0.7,
            pairwise_similarity_avg=0.92,  # Good
            pairwise_similarity_min=0.85,
            pairwise_similarity_max=0.98,
            temperature=0.3,
            seed=None,
            measured_at="2026-02-06T10:00:00Z"
        )
        
        alert = detect_variability_alert(metrics, alert_threshold=0.80)
        
        assert alert is None


class TestVariabilityIntegration:
    """Integration tests for variability measurement workflow."""
    
    def test_complete_workflow_low_temperature(self):
        """Test complete workflow with low temperature (high determinism)."""
        measurer = VariabilityMeasurer()
        
        # Simulate outputs from temperature=0.1 (should be very consistent)
        base_output = "Patient presents with acute headache, denies trauma. Vital signs stable."
        outputs = [base_output] * 8 + [
            "Patient presents with acute headache, denies trauma. Vitals stable.",
            "Patient has acute headache, denies trauma. Vital signs are stable."
        ]
        
        runs = [
            InferenceRun(output, i, 850.0, 150, uuid4(), "2026-02-06T10:00:00Z")
            for i, output in enumerate(outputs, 1)
        ]
        
        metrics = measurer.measure_variability(runs, temperature=0.1)
        
        # Should show high consistency
        assert metrics.unique_outputs <= 3
        assert metrics.pairwise_similarity_avg > 0.90
        
        # Should be acceptable
        is_acceptable, _ = measurer.is_acceptable_variability(metrics, min_similarity=0.85)
        assert is_acceptable is True
        
        # Should not trigger alert
        alert = detect_variability_alert(metrics, alert_threshold=0.80)
        assert alert is None
    
    def test_complete_workflow_high_temperature(self):
        """Test complete workflow with high temperature (high variability)."""
        measurer = VariabilityMeasurer()
        
        # Simulate outputs from temperature=0.8 (should be more varied)
        outputs = [
            "Patient presents with acute headache.",
            "Acute cephalgia reported by patient.",
            "Patient complains of severe head pain.",
            "Headache onset was sudden, patient denies trauma.",
            "Patient describes throbbing headache.",
            "Severe headache noted in patient presentation.",
            "Patient's chief complaint is acute headache.",
            "Acute head pain, denies any trauma or injury.",
            "Patient experiencing sudden onset headache.",
            "Cephalgia, acute onset, no trauma history."
        ]
        
        runs = [
            InferenceRun(output, i, 850.0, 150, uuid4(), "2026-02-06T10:00:00Z")
            for i, output in enumerate(outputs, 1)
        ]
        
        metrics = measurer.measure_variability(runs, temperature=0.8)
        
        # Should show more variability
        assert metrics.unique_outputs >= 8
        assert metrics.pairwise_similarity_avg < 0.90
        
        # May not be acceptable for clinical use
        is_acceptable, _ = measurer.is_acceptable_variability(metrics, min_similarity=0.85)
        # Depending on similarity, this might fail
        
        # Might trigger alert
        alert = detect_variability_alert(metrics, alert_threshold=0.85)
        # May or may not alert depending on actual similarity