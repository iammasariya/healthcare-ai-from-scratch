"""
Shadow mode services for safe model rollout.

Post 6 introduces:
- dual-path execution for production and candidate models
- divergence scoring using Post 5 evaluation logic
- promotion recommendations based on recent shadow runs
- HAPI FHIR support for realistic clinical payloads
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Optional
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.config import settings
from app.evaluation import Evaluator, GoldenDataset
from app.llm import LLMConfig, LLMResponse, get_llm_service
from app.logging import log_error


def _first_coding_text(codeable_concept: dict[str, Any]) -> Optional[str]:
    """Extract display or free-text content from a FHIR CodeableConcept."""
    if not codeable_concept:
        return None

    if codeable_concept.get("text"):
        return codeable_concept["text"]

    for coding in codeable_concept.get("coding", []):
        if coding.get("display"):
            return coding["display"]

    return None


def _observation_value_text(resource: dict[str, Any]) -> Optional[str]:
    """Render a compact human-readable Observation value."""
    if "valueQuantity" in resource:
        quantity = resource["valueQuantity"]
        value = quantity.get("value")
        unit = quantity.get("unit", "")
        return f"{value} {unit}".strip()

    if "valueString" in resource:
        return resource["valueString"]

    if "valueCodeableConcept" in resource:
        return _first_coding_text(resource["valueCodeableConcept"])

    return None


def build_note_from_hapi_fhir_bundle(bundle: dict[str, Any]) -> str:
    """
    Convert a HAPI FHIR-style Bundle into concise clinical note context.

    This intentionally focuses on resources that matter for summary generation
    in the codebase examples: Patient, Encounter, Condition, Observation,
    and MedicationRequest.
    """
    entries = bundle.get("entry", [])

    patient_line = None
    encounter_lines: list[str] = []
    condition_lines: list[str] = []
    observation_lines: list[str] = []
    medication_lines: list[str] = []

    for entry in entries:
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            names = resource.get("name", [])
            rendered_name = "Unknown"
            if names:
                given = " ".join(names[0].get("given", []))
                family = names[0].get("family", "")
                rendered_name = " ".join(part for part in [given, family] if part).strip() or "Unknown"
            patient_line = (
                f"Patient: {rendered_name}; gender: {resource.get('gender', 'unknown')}; "
                f"birthDate: {resource.get('birthDate', 'unknown')}."
            )

        elif resource_type == "Encounter":
            encounter_class = resource.get("class", {}).get("display")
            encounter_type = None
            if resource.get("type"):
                encounter_type = _first_coding_text(resource["type"][0])
            details = ", ".join(part for part in [encounter_class, encounter_type] if part)
            if details:
                encounter_lines.append(f"Encounter: {details}.")

        elif resource_type == "Condition":
            label = _first_coding_text(resource.get("code", {}))
            if label:
                condition_lines.append(f"Condition: {label}.")

        elif resource_type == "Observation":
            label = _first_coding_text(resource.get("code", {}))
            value = _observation_value_text(resource)
            if label and value:
                observation_lines.append(f"Observation: {label} {value}.")

        elif resource_type == "MedicationRequest":
            medication = _first_coding_text(resource.get("medicationCodeableConcept", {}))
            dosage_list = resource.get("dosageInstruction", [])
            dosage = dosage_list[0].get("text") if dosage_list else None
            if medication and dosage:
                medication_lines.append(f"Medication: {medication}; dose: {dosage}.")
            elif medication:
                medication_lines.append(f"Medication: {medication}.")

    lines = [
        line
        for line in [patient_line, *encounter_lines, *condition_lines, *observation_lines, *medication_lines]
        if line
    ]

    if not lines:
        raise ValueError("FHIR bundle did not contain enough clinical content to build a note")

    return " ".join(lines)


class HAPIFHIRClient:
    """Minimal client for fetching patient context from an open HAPI FHIR server."""

    def __init__(self, base_url: Optional[str] = None, timeout_seconds: Optional[int] = None):
        self.base_url = (base_url or settings.hapi_fhir_base_url or "").rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.hapi_fhir_timeout_seconds

        if not self.base_url:
            raise ValueError("HAPI FHIR base URL is required")

    def _get_json(self, url: str) -> dict[str, Any]:
        request = Request(url, headers={"Accept": "application/fhir+json"})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def fetch_patient_context_bundle(self, patient_id: str) -> dict[str, Any]:
        """Fetch a compact multi-resource Bundle from a HAPI FHIR server."""
        patient_path = quote(patient_id, safe="")
        resources = [
            f"{self.base_url}/Patient/{patient_path}",
            f"{self.base_url}/Encounter?subject=Patient/{patient_path}&_count=5",
            f"{self.base_url}/Condition?subject=Patient/{patient_path}&_count=10",
            f"{self.base_url}/Observation?subject=Patient/{patient_path}&_count=20",
            f"{self.base_url}/MedicationRequest?subject=Patient/{patient_path}&_count=10",
        ]

        entries: list[dict[str, Any]] = []
        for url in resources:
            payload = self._get_json(url)

            if payload.get("resourceType") == "Bundle":
                for entry in payload.get("entry", []):
                    if entry.get("resource"):
                        entries.append({"resource": entry["resource"]})
            else:
                entries.append({"resource": payload})

        return {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": entries,
        }


@dataclass
class ShadowModeRunRecord:
    """Persisted record for a single shadow-mode execution."""

    audit_id: str
    patient_id: str
    source_system: str
    source_format: str
    production_model: Optional[str]
    shadow_model: Optional[str]
    similarity_score: Optional[float]
    divergent: bool
    review_required: bool
    recommendation: str
    production_latency_ms: Optional[float]
    shadow_latency_ms: Optional[float]
    production_cost_usd: Optional[float]
    shadow_cost_usd: Optional[float]
    alert_triggered: bool
    alert_severity: str
    error: Optional[str]


@dataclass
class RolloutRecommendation:
    """Recommendation for gradual rollout of the candidate path."""

    total_runs_considered: int
    divergent_runs: int
    divergence_rate: float
    avg_similarity: float
    recommended_traffic_percentage: int
    decision: str
    reason: str


@dataclass
class ShadowExecutionResult:
    """Full result for shadow-mode execution."""

    note_text: str
    source_system: str
    source_format: str
    production_response: Optional[LLMResponse]
    production_error: Optional[str]
    shadow_response: Optional[LLMResponse]
    shadow_error: Optional[str]
    similarity_score: Optional[float]
    divergent: bool
    review_required: bool
    recommendation: str
    alert_triggered: bool
    alert_severity: str
    alert_message: str
    rollout_recommendation: RolloutRecommendation


class ShadowResultStore:
    """Persist and analyze shadow-mode results for promotion decisions."""

    def __init__(self, directory: Optional[str] = None):
        self.directory = Path(directory or settings.shadow_results_dir)

    def save(self, audit_id: str, record: ShadowModeRunRecord) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        output_path = self.directory / f"{audit_id}.json"
        with open(output_path, "w") as f:
            json.dump(asdict(record), f, indent=2)

    def load_all(self) -> list[ShadowModeRunRecord]:
        if not self.directory.exists():
            return []

        records: list[ShadowModeRunRecord] = []
        for path in sorted(self.directory.glob("*.json")):
            records.append(self.load_record(path))
        return records

    def load_record(self, path: Path) -> ShadowModeRunRecord:
        with open(path, "r") as f:
            data = json.load(f)
        return ShadowModeRunRecord(**data)

    def recommend_rollout(self) -> RolloutRecommendation:
        records = self.load_all()
        recent = records[-max(settings.shadow_promotion_min_requests, 1):]

        if not recent:
            return RolloutRecommendation(
                total_runs_considered=0,
                divergent_runs=0,
                divergence_rate=0.0,
                avg_similarity=0.0,
                recommended_traffic_percentage=0,
                decision="hold",
                reason="No shadow runs recorded yet",
            )

        divergent_runs = sum(1 for record in recent if record.divergent)
        divergence_rate = divergent_runs / len(recent)
        similarity_values = [
            record.similarity_score for record in recent if record.similarity_score is not None
        ]
        avg_similarity = (
            sum(similarity_values) / len(similarity_values) if similarity_values else 0.0
        )

        if len(recent) < settings.shadow_promotion_min_requests:
            return RolloutRecommendation(
                total_runs_considered=len(recent),
                divergent_runs=divergent_runs,
                divergence_rate=divergence_rate,
                avg_similarity=avg_similarity,
                recommended_traffic_percentage=0,
                decision="hold",
                reason="Not enough shadow runs to make a rollout decision",
            )

        if divergence_rate > settings.shadow_promotion_max_divergence_rate:
            return RolloutRecommendation(
                total_runs_considered=len(recent),
                divergent_runs=divergent_runs,
                divergence_rate=divergence_rate,
                avg_similarity=avg_similarity,
                recommended_traffic_percentage=0,
                decision="hold",
                reason="Divergence rate is too high for promotion",
            )

        if avg_similarity < settings.shadow_promotion_min_avg_similarity:
            return RolloutRecommendation(
                total_runs_considered=len(recent),
                divergent_runs=divergent_runs,
                divergence_rate=divergence_rate,
                avg_similarity=avg_similarity,
                recommended_traffic_percentage=0,
                decision="hold",
                reason="Average similarity is below the promotion threshold",
            )

        if avg_similarity >= settings.shadow_promote_full_threshold and divergence_rate == 0.0:
            percentage = 100
            decision = "promote"
            reason = "Shadow candidate is stable enough for full promotion"
        elif avg_similarity >= settings.shadow_promote_broad_threshold:
            percentage = 50
            decision = "advance"
            reason = "Candidate is ready for a broader staged rollout"
        elif avg_similarity >= settings.shadow_promote_limited_threshold:
            percentage = 25
            decision = "advance"
            reason = "Candidate is ready for limited traffic exposure"
        else:
            percentage = 10
            decision = "advance"
            reason = "Candidate is acceptable for an initial guarded rollout"

        return RolloutRecommendation(
            total_runs_considered=len(recent),
            divergent_runs=divergent_runs,
            divergence_rate=divergence_rate,
            avg_similarity=avg_similarity,
            recommended_traffic_percentage=percentage,
            decision=decision,
            reason=reason,
        )


class ShadowModeRunner:
    """Run production and candidate paths side by side and assess rollout readiness."""

    def __init__(
        self,
        min_similarity: Optional[float] = None,
        alert_similarity_threshold: Optional[float] = None,
        result_store: Optional[ShadowResultStore] = None,
        hapi_client_factory: Optional[Callable[[str], HAPIFHIRClient]] = None,
    ):
        self.min_similarity = (
            settings.shadow_similarity_threshold if min_similarity is None else min_similarity
        )
        self.alert_similarity_threshold = (
            settings.shadow_alert_similarity_threshold
            if alert_similarity_threshold is None
            else alert_similarity_threshold
        )
        # Reuse the fuzzy_match_score metric from Post 5's Evaluator.
        # The empty GoldenDataset is intentional -- we only need the scoring method.
        self._evaluator = Evaluator(GoldenDataset())
        self.result_store = result_store or ShadowResultStore()
        self.hapi_client_factory = hapi_client_factory or (
            lambda base_url: HAPIFHIRClient(base_url=base_url)
        )

    def compare_outputs(self, production_output: str, shadow_output: str) -> tuple[float, bool, str]:
        """Compare production and shadow outputs using the Post 5 overlap metric."""
        similarity = self._evaluator.fuzzy_match_score(production_output, shadow_output)
        divergent = similarity < self.min_similarity

        if divergent:
            recommendation = (
                f"Shadow output diverged from production "
                f"({similarity:.3f} below threshold {self.min_similarity:.3f})"
            )
        else:
            recommendation = f"Shadow output is within acceptable similarity ({similarity:.3f})"

        return similarity, divergent, recommendation

    def evaluate_alert(self, similarity_score: Optional[float], error: Optional[str]) -> tuple[bool, str, str]:
        """Determine whether the shadow run should trigger alerting."""
        if error:
            return True, "critical", f"Shadow mode failed: {error}"

        if similarity_score is None:
            return True, "critical", "Shadow mode did not produce a comparable output"

        if similarity_score < self.alert_similarity_threshold:
            return True, "critical", "Shadow similarity is below the critical alert threshold"

        if similarity_score < self.min_similarity:
            return True, "warning", "Shadow similarity is below the promotion threshold"

        return False, "none", "Shadow output is within configured thresholds"

    def resolve_note_text(
        self,
        patient_id: str,
        note_text: Optional[str] = None,
        fhir_bundle: Optional[dict[str, Any]] = None,
        hapi_fhir_base_url: Optional[str] = None,
    ) -> tuple[str, str]:
        """Resolve clinical context from raw note text, inline FHIR, or HAPI FHIR fetch."""
        if note_text:
            return note_text, "clinical_note"

        if fhir_bundle is not None:
            return build_note_from_hapi_fhir_bundle(fhir_bundle), "hapi_fhir_bundle"

        if hapi_fhir_base_url:
            bundle = self.hapi_client_factory(hapi_fhir_base_url).fetch_patient_context_bundle(patient_id)
            return build_note_from_hapi_fhir_bundle(bundle), "hapi_fhir_bundle"

        raise ValueError("No shadow input source provided")

    def _run_callable(self, fn: Callable[[str], str], note_text: str) -> tuple[str, float]:
        start = perf_counter()
        output = fn(note_text)
        latency_ms = (perf_counter() - start) * 1000
        return output, latency_ms

    def run_compare_only(
        self,
        production_fn: Callable[[str], str],
        shadow_fn: Callable[[str], str],
        patient_id: str,
        note_text: Optional[str] = None,
        fhir_bundle: Optional[dict[str, Any]] = None,
        hapi_fhir_base_url: Optional[str] = None,
        source_system: str = "internal",
    ) -> ShadowExecutionResult:
        """Run shadow mode with plain callables, mainly for examples and tests."""
        rendered_note, source_format = self.resolve_note_text(
            patient_id=patient_id,
            note_text=note_text,
            fhir_bundle=fhir_bundle,
            hapi_fhir_base_url=hapi_fhir_base_url,
        )

        production_output, production_latency = self._run_callable(production_fn, rendered_note)
        shadow_output, shadow_latency = self._run_callable(shadow_fn, rendered_note)

        similarity, divergent, recommendation = self.compare_outputs(
            production_output=production_output,
            shadow_output=shadow_output,
        )
        alert_triggered, alert_severity, alert_message = self.evaluate_alert(similarity, None)
        rollout_recommendation = self.result_store.recommend_rollout()

        return ShadowExecutionResult(
            note_text=rendered_note,
            source_system=source_system,
            source_format=source_format,
            production_response=LLMResponse(
                content=production_output,
                model="production-fn",
                tokens_used=0,
                latency_ms=production_latency,
                cost_usd=0.0,
                stop_reason="end_turn",
            ),
            production_error=None,
            shadow_response=LLMResponse(
                content=shadow_output,
                model="shadow-fn",
                tokens_used=0,
                latency_ms=shadow_latency,
                cost_usd=0.0,
                stop_reason="end_turn",
            ),
            shadow_error=None,
            similarity_score=similarity,
            divergent=divergent,
            review_required=divergent,
            recommendation=recommendation,
            alert_triggered=alert_triggered,
            alert_severity=alert_severity,
            alert_message=alert_message,
            rollout_recommendation=rollout_recommendation,
        )

    def run_llm_shadow(
        self,
        patient_id: str,
        audit_id: str,
        source_system: str = "internal",
        note_text: Optional[str] = None,
        fhir_bundle: Optional[dict[str, Any]] = None,
        hapi_fhir_base_url: Optional[str] = None,
        candidate_prompt_version: Optional[str] = None,
    ) -> ShadowExecutionResult:
        """Execute production and candidate LLM paths for a single request."""
        rendered_note, source_format = self.resolve_note_text(
            patient_id=patient_id,
            note_text=note_text,
            fhir_bundle=fhir_bundle,
            hapi_fhir_base_url=hapi_fhir_base_url,
        )

        production_service = get_llm_service()
        shadow_config = LLMConfig(
            model=settings.shadow_candidate_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.shadow_candidate_temperature,
            timeout=settings.llm_timeout,
            max_retries=settings.llm_max_retries,
        )
        shadow_service = get_llm_service(config=shadow_config, force_new=True)

        production_response, production_error = production_service.summarize_clinical_note(
            note_text=rendered_note,
            audit_id=audit_id,
        )
        shadow_response, shadow_error = shadow_service.summarize_clinical_note(
            note_text=rendered_note,
            audit_id=audit_id,
            prompt_version=candidate_prompt_version or settings.shadow_candidate_prompt_version,
        )

        if production_response and shadow_response:
            similarity, divergent, recommendation = self.compare_outputs(
                production_output=production_response.content,
                shadow_output=shadow_response.content,
            )
            error = None
        else:
            similarity = None
            divergent = True
            recommendation = "Shadow execution could not be compared because one path failed"
            error = production_error or shadow_error

        alert_triggered, alert_severity, alert_message = self.evaluate_alert(similarity, error)

        record = ShadowModeRunRecord(
            audit_id=audit_id,
            patient_id=patient_id,
            source_system=source_system,
            source_format=source_format,
            production_model=production_response.model if production_response else None,
            shadow_model=shadow_response.model if shadow_response else None,
            similarity_score=similarity,
            divergent=divergent,
            review_required=divergent,
            recommendation=recommendation,
            production_latency_ms=production_response.latency_ms if production_response else None,
            shadow_latency_ms=shadow_response.latency_ms if shadow_response else None,
            production_cost_usd=production_response.cost_usd if production_response else None,
            shadow_cost_usd=shadow_response.cost_usd if shadow_response else None,
            alert_triggered=alert_triggered,
            alert_severity=alert_severity,
            error=error,
        )

        if settings.shadow_write_results:
            self.result_store.save(audit_id, record)

        rollout_recommendation = self.result_store.recommend_rollout()

        return ShadowExecutionResult(
            note_text=rendered_note,
            source_system=source_system,
            source_format=source_format,
            production_response=production_response,
            production_error=production_error,
            shadow_response=shadow_response,
            shadow_error=shadow_error,
            similarity_score=similarity,
            divergent=divergent,
            review_required=divergent,
            recommendation=recommendation,
            alert_triggered=alert_triggered,
            alert_severity=alert_severity,
            alert_message=alert_message,
            rollout_recommendation=rollout_recommendation,
        )


def build_llm_metrics(response: Optional[LLMResponse]) -> Optional[dict[str, Any]]:
    """Convert an LLMResponse into the API metrics payload shape."""
    if response is None:
        return None

    return {
        "model": response.model,
        "tokens_used": response.tokens_used,
        "latency_ms": response.latency_ms,
        "cost_usd": response.cost_usd,
        "prompt_version": response.prompt_version,
        "prompt_hash": response.prompt_hash,
    }
