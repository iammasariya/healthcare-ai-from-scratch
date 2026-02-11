"""
Variability Measurement and Determinism Controls (Post 4)

This module provides tools to measure and control model output variability,
a critical concern in healthcare AI where inconsistency erodes clinical trust.

Key capabilities:
- Repeated inference for measuring output divergence
- Semantic similarity comparison between outputs
- Temperature experimentation framework
- Deterministic mode enforcement
- Variability metrics calculation
"""

import hashlib
import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

# For semantic similarity - we'll use simple metrics for now
# In production, you might use sentence-transformers or similar
import difflib


@dataclass
class VariabilityMetrics:
    """
    Metrics capturing model output variability.
    
    Attributes:
        run_count: Number of times the same prompt was run
        unique_outputs: Number of distinct outputs generated
        output_lengths: List of output lengths (character count)
        avg_length: Average output length
        length_std_dev: Standard deviation of output lengths
        exact_match_rate: Proportion of outputs matching the first output
        pairwise_similarity_avg: Average similarity score between all pairs
        pairwise_similarity_min: Minimum similarity between any pair
        pairwise_similarity_max: Maximum similarity between any pair
        temperature: Temperature used for generation
        seed: Random seed used (if any)
        measured_at: Timestamp of measurement
    """
    run_count: int
    unique_outputs: int
    output_lengths: List[int]
    avg_length: float
    length_std_dev: float
    exact_match_rate: float
    pairwise_similarity_avg: float
    pairwise_similarity_min: float
    pairwise_similarity_max: float
    temperature: float
    seed: Optional[int]
    measured_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for logging/storage."""
        return {
            "run_count": self.run_count,
            "unique_outputs": self.unique_outputs,
            "avg_length": round(self.avg_length, 2),
            "length_std_dev": round(self.length_std_dev, 2),
            "exact_match_rate": round(self.exact_match_rate, 3),
            "pairwise_similarity_avg": round(self.pairwise_similarity_avg, 3),
            "pairwise_similarity_min": round(self.pairwise_similarity_min, 3),
            "pairwise_similarity_max": round(self.pairwise_similarity_max, 3),
            "temperature": self.temperature,
            "seed": self.seed,
            "measured_at": self.measured_at
        }


@dataclass
class InferenceRun:
    """
    Single inference run result for variability measurement.
    
    Attributes:
        output: The generated text output
        run_number: Which run this was (1, 2, 3, ...)
        latency_ms: Time taken for this inference
        tokens_used: Number of tokens consumed
        audit_id: Unique identifier for tracing
        timestamp: When this inference completed
    """
    output: str
    run_number: int
    latency_ms: float
    tokens_used: int
    audit_id: UUID
    timestamp: str


class VariabilityMeasurer:
    """
    Measures output variability across multiple inference runs.
    
    This class helps answer questions like:
    - "How much do outputs vary at temperature 0.3 vs 0.7?"
    - "What's the semantic similarity between runs?"
    - "Are we seeing acceptable consistency?"
    """
    
    def __init__(self):
        """Initialize the variability measurer."""
        pass
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Uses sequence matching for now. In production, you might use:
        - Sentence transformers with cosine similarity
        - BERT score
        - Rouge scores
        - Custom clinical similarity metrics
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            
        Returns:
            Similarity score between 0.0 (completely different) and 1.0 (identical)
        """
        if not text1 or not text2:
            return 0.0
        
        # Use SequenceMatcher for character-level similarity
        # This is simple but effective for detecting major differences
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def calculate_pairwise_similarities(self, outputs: List[str]) -> List[float]:
        """
        Calculate similarity for all pairs of outputs.
        
        Args:
            outputs: List of output strings to compare
            
        Returns:
            List of similarity scores for all unique pairs
        """
        if len(outputs) < 2:
            return [1.0]  # Single output is perfectly similar to itself
        
        similarities = []
        for i in range(len(outputs)):
            for j in range(i + 1, len(outputs)):
                sim = self.calculate_similarity(outputs[i], outputs[j])
                similarities.append(sim)
        
        return similarities
    
    def measure_variability(
        self,
        runs: List[InferenceRun],
        temperature: float,
        seed: Optional[int] = None
    ) -> VariabilityMetrics:
        """
        Calculate comprehensive variability metrics from inference runs.
        
        Args:
            runs: List of inference run results
            temperature: Temperature parameter used
            seed: Random seed used (if any)
            
        Returns:
            VariabilityMetrics with all calculated metrics
        """
        if not runs:
            raise ValueError("Cannot measure variability with no runs")
        
        # Extract outputs
        outputs = [run.output for run in runs]
        
        # Count unique outputs
        unique_outputs = len(set(outputs))
        
        # Calculate length statistics
        lengths = [len(output) for output in outputs]
        avg_length = statistics.mean(lengths)
        length_std_dev = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
        
        # Calculate exact match rate (proportion matching first output)
        first_output = outputs[0]
        exact_matches = sum(1 for output in outputs if output == first_output)
        exact_match_rate = exact_matches / len(outputs)
        
        # Calculate pairwise similarities
        similarities = self.calculate_pairwise_similarities(outputs)
        similarity_avg = statistics.mean(similarities)
        similarity_min = min(similarities)
        similarity_max = max(similarities)
        
        return VariabilityMetrics(
            run_count=len(runs),
            unique_outputs=unique_outputs,
            output_lengths=lengths,
            avg_length=avg_length,
            length_std_dev=length_std_dev,
            exact_match_rate=exact_match_rate,
            pairwise_similarity_avg=similarity_avg,
            pairwise_similarity_min=similarity_min,
            pairwise_similarity_max=similarity_max,
            temperature=temperature,
            seed=seed,
            measured_at=datetime.utcnow().isoformat() + "Z"
        )
    
    def is_acceptable_variability(
        self,
        metrics: VariabilityMetrics,
        min_similarity: float = 0.85,
        max_unique_ratio: float = 0.3
    ) -> Tuple[bool, str]:
        """
        Determine if variability is within acceptable bounds for clinical use.
        
        "Acceptable" depends on context:
        - Clinical summaries: High consistency required (>0.90 similarity)
        - Treatment suggestions: Moderate consistency (>0.85 similarity)
        - Research questions: Lower consistency acceptable (>0.70 similarity)
        
        Args:
            metrics: Calculated variability metrics
            min_similarity: Minimum acceptable average similarity (default 0.85)
            max_unique_ratio: Maximum acceptable ratio of unique/total outputs (default 0.3)
            
        Returns:
            Tuple of (is_acceptable: bool, reason: str)
        """
        # Check similarity threshold
        if metrics.pairwise_similarity_avg < min_similarity:
            return False, f"Average similarity {metrics.pairwise_similarity_avg:.3f} below threshold {min_similarity}"
        
        # Check uniqueness ratio
        unique_ratio = metrics.unique_outputs / metrics.run_count
        if unique_ratio > max_unique_ratio:
            return False, f"Too many unique outputs: {metrics.unique_outputs}/{metrics.run_count} (ratio {unique_ratio:.3f})"
        
        # Check for extreme outliers in pairwise similarity
        if metrics.pairwise_similarity_min < 0.70:
            return False, f"Found highly divergent outputs (min similarity {metrics.pairwise_similarity_min:.3f})"
        
        return True, "Variability within acceptable bounds"


class DeterminismController:
    """
    Controls determinism in model inference.
    
    In healthcare AI, we often need to choose between:
    - High determinism: Same input → same output (reproducibility)
    - Controlled variability: Some variation acceptable (creativity)
    
    This class helps manage that tradeoff.
    """
    
    @staticmethod
    def get_deterministic_seed(
        patient_id: str,
        prompt_version: str,
        date: str
    ) -> int:
        """
        Generate a deterministic seed from context.
        
        This allows:
        - Reproducibility: Same inputs → same seed → same output
        - Variation: Different contexts → different seeds
        
        Args:
            patient_id: Patient identifier
            prompt_version: Version of prompt being used
            date: Date string (e.g., "2026-02-06")
            
        Returns:
            Integer seed derived from inputs
        """
        # Combine inputs and hash
        combined = f"{patient_id}|{prompt_version}|{date}"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        
        # Convert first 4 bytes to integer
        seed = int.from_bytes(hash_bytes[:4], byteorder='big')
        
        return seed
    
    @staticmethod
    def recommend_temperature(
        task_type: str,
        risk_level: str = "high"
    ) -> float:
        """
        Recommend temperature based on task and risk level.
        
        Guidelines:
        - Extraction/Classification: 0.0-0.1 (deterministic)
        - Clinical summaries: 0.2-0.3 (mostly deterministic)
        - Treatment suggestions: 0.3-0.5 (balanced)
        - Research queries: 0.5-0.7 (creative)
        
        Args:
            task_type: Type of task ('extraction', 'summary', 'generation', 'research')
            risk_level: Risk level ('low', 'medium', 'high')
            
        Returns:
            Recommended temperature value
        """
        # Temperature matrix: task_type -> risk_level -> temperature
        recommendations = {
            "extraction": {"low": 0.1, "medium": 0.05, "high": 0.0},
            "summary": {"low": 0.4, "medium": 0.3, "high": 0.2},
            "generation": {"low": 0.6, "medium": 0.5, "high": 0.3},
            "research": {"low": 0.8, "medium": 0.7, "high": 0.5}
        }
        
        task = task_type.lower()
        risk = risk_level.lower()
        
        if task not in recommendations:
            # Default to conservative (summary-like)
            task = "summary"
        
        if risk not in recommendations[task]:
            risk = "high"  # Default to conservative
        
        return recommendations[task][risk]


def calculate_output_hash(output: str) -> str:
    """
    Calculate a hash of an output for quick comparison.
    
    Useful for:
    - Detecting exact duplicates
    - Grouping similar outputs
    - Tracking output history
    
    Args:
        output: Text output to hash
        
    Returns:
        SHA256 hash (first 16 characters)
    """
    hash_full = hashlib.sha256(output.encode()).hexdigest()
    return hash_full[:16]


def detect_variability_alert(
    metrics: VariabilityMetrics,
    alert_threshold: float = 0.80
) -> Optional[str]:
    """
    Detect if variability metrics warrant an alert.
    
    This is used for monitoring: if variability suddenly increases,
    it might indicate:
    - Prompt changed unintentionally
    - Model behavior shifted
    - API parameters changed
    - Production issue
    
    Args:
        metrics: Variability metrics to check
        alert_threshold: Similarity threshold below which to alert
        
    Returns:
        Alert message if metrics are concerning, None otherwise
    """
    if metrics.pairwise_similarity_avg < alert_threshold:
        return (
            f"VARIABILITY ALERT: Average output similarity ({metrics.pairwise_similarity_avg:.3f}) "
            f"below threshold ({alert_threshold}). Outputs are diverging more than expected."
        )
    
    if metrics.unique_outputs == metrics.run_count:
        return (
            f"VARIABILITY ALERT: All {metrics.run_count} outputs were unique. "
            f"Model may be exhibiting excessive randomness."
        )
    
    return None