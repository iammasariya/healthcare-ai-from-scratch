"""
Tests for Post 6 shadow mode foundations.
"""

from pathlib import Path

import pytest

from app.shadow import (
    HAPIFHIRClient,
    ShadowModeRunRecord,
    ShadowModeRunner,
    ShadowResultStore,
    build_note_from_hapi_fhir_bundle,
)


@pytest.fixture
def sample_hapi_fhir_bundle():
    """Representative HAPI FHIR-style Bundle for shadow-mode tests."""
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-001",
                    "name": [{"given": ["Alicia"], "family": "Lopez"}],
                    "gender": "female",
                    "birthDate": "1981-04-10",
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "class": {"display": "ambulatory"},
                    "type": [{"text": "Primary care follow-up"}],
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "code": {"text": "Type 2 diabetes mellitus"},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "code": {"text": "Hemoglobin A1c"},
                    "valueQuantity": {"value": 8.2, "unit": "%"},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "code": {"text": "Blood pressure"},
                    "valueString": "142/88 mmHg",
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationRequest",
                    "medicationCodeableConcept": {"text": "Metformin 1000 MG Oral Tablet"},
                    "dosageInstruction": [{"text": "1000 mg twice daily with meals"}],
                }
            },
        ],
    }


class TestHapiFHIRShadowMode:
    """Tests for HAPI FHIR bundle conversion and shadow comparison."""

    def test_build_note_from_hapi_fhir_bundle(self, sample_hapi_fhir_bundle):
        note = build_note_from_hapi_fhir_bundle(sample_hapi_fhir_bundle)

        assert "Alicia Lopez" in note
        assert "Type 2 diabetes mellitus" in note
        assert "Hemoglobin A1c 8.2 %" in note
        assert "Metformin 1000 MG Oral Tablet" in note

    def test_build_note_requires_clinical_content(self):
        with pytest.raises(ValueError):
            build_note_from_hapi_fhir_bundle({"resourceType": "Bundle", "entry": []})

    def test_shadow_mode_runner_flags_divergence(self):
        runner = ShadowModeRunner(min_similarity=0.60)

        result = runner.run_compare_only(
            production_fn=lambda note: "Diabetes follow-up with elevated A1c and hypertension.",
            shadow_fn=lambda note: "Acute pneumonia with fever and hypoxia.",
            patient_id="PT-1",
            note_text="Follow-up note.",
        )

        assert result.divergent is True
        assert result.review_required is True
        assert result.rollout_recommendation.decision == "hold"

    def test_shadow_mode_runner_accepts_similar_outputs(self):
        runner = ShadowModeRunner(min_similarity=0.20)

        result = runner.run_compare_only(
            production_fn=lambda note: "Diabetes follow-up with elevated A1c.",
            shadow_fn=lambda note: "Diabetes follow-up, elevated A1c persists.",
            patient_id="PT-1",
            note_text="Follow-up note.",
        )

        assert result.divergent is False
        assert result.alert_triggered is False

    def test_shadow_mode_runner_uses_fhir_bundle(self, sample_hapi_fhir_bundle):
        runner = ShadowModeRunner()

        result = runner.run_compare_only(
            production_fn=lambda note: "Structured summary for " + note.split(".")[0],
            shadow_fn=lambda note: "Structured summary for " + note.split(".")[0],
            patient_id="patient-001",
            fhir_bundle=sample_hapi_fhir_bundle,
            source_system="hapi-fhir-r4",
        )

        assert result.source_format == "hapi_fhir_bundle"
        assert result.source_system == "hapi-fhir-r4"
        assert "Alicia Lopez" in result.note_text


class TestShadowResultStore:
    """Tests for persisted rollout analysis."""

    def test_recommend_rollout_requires_enough_runs(self, tmp_path: Path):
        store = ShadowResultStore(directory=str(tmp_path))
        store.save(
            "audit-1",
            ShadowModeRunRecord(
                audit_id="audit-1",
                patient_id="PT-1",
                source_system="internal",
                source_format="clinical_note",
                production_model="prod",
                shadow_model="shadow",
                similarity_score=0.90,
                divergent=False,
                review_required=False,
                recommendation="ok",
                production_latency_ms=100.0,
                shadow_latency_ms=110.0,
                production_cost_usd=0.01,
                shadow_cost_usd=0.01,
                alert_triggered=False,
                alert_severity="none",
                error=None,
            ),
        )

        recommendation = store.recommend_rollout()
        assert recommendation.decision == "hold"
        assert recommendation.recommended_traffic_percentage == 0

    def test_recommend_rollout_advances_when_runs_are_stable(self, tmp_path: Path):
        store = ShadowResultStore(directory=str(tmp_path))

        for idx in range(5):
            store.save(
                f"audit-{idx}",
                ShadowModeRunRecord(
                    audit_id=f"audit-{idx}",
                    patient_id="PT-1",
                    source_system="internal",
                    source_format="clinical_note",
                    production_model="prod",
                    shadow_model="shadow",
                    similarity_score=0.82,
                    divergent=False,
                    review_required=False,
                    recommendation="ok",
                    production_latency_ms=100.0,
                    shadow_latency_ms=105.0,
                    production_cost_usd=0.01,
                    shadow_cost_usd=0.01,
                    alert_triggered=False,
                    alert_severity="none",
                    error=None,
                ),
            )

        recommendation = store.recommend_rollout()
        assert recommendation.decision == "advance"
        assert recommendation.recommended_traffic_percentage >= 25


class TestHapiFHIRClient:
    """Tests for HAPI FHIR patient context fetching."""

    def test_fetch_patient_context_bundle(self, monkeypatch):
        payloads = [
            {"resourceType": "Patient", "id": "patient-001"},
            {
                "resourceType": "Bundle",
                "entry": [{"resource": {"resourceType": "Observation", "id": "obs-1"}}],
            },
            {"resourceType": "Bundle", "entry": []},
            {"resourceType": "Bundle", "entry": []},
            {"resourceType": "Bundle", "entry": []},
        ]

        client = HAPIFHIRClient(base_url="https://hapi.fhir.org/baseR4")

        def fake_get_json(url):
            return payloads.pop(0)

        monkeypatch.setattr(client, "_get_json", fake_get_json)

        bundle = client.fetch_patient_context_bundle("patient-001")
        assert bundle["resourceType"] == "Bundle"
        assert len(bundle["entry"]) == 2
