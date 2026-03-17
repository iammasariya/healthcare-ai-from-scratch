"""
Post 6 shadow mode demonstration with HAPI FHIR-style data.

This example shows how to:
1. Convert a HAPI FHIR Bundle into a readable clinical note
2. Run production and candidate paths side by side
3. Measure divergence before promoting the candidate
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.shadow import ShadowModeRunner


SAMPLE_HAPI_FHIR_BUNDLE = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": "patient-101",
                "name": [{"given": ["James"], "family": "Carter"}],
                "gender": "male",
                "birthDate": "1959-07-18",
            }
        },
        {
            "resource": {
                "resourceType": "Encounter",
                "class": {"display": "outpatient"},
                "type": [{"text": "Cardiology follow-up"}],
            }
        },
        {
            "resource": {
                "resourceType": "Condition",
                "code": {"text": "Congestive heart failure"},
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "code": {"text": "NT-proBNP"},
                "valueQuantity": {"value": 1840, "unit": "pg/mL"},
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "code": {"text": "Weight"},
                "valueQuantity": {"value": 98.4, "unit": "kg"},
            }
        },
        {
            "resource": {
                "resourceType": "MedicationRequest",
                "medicationCodeableConcept": {"text": "Furosemide 40 MG Oral Tablet"},
                "dosageInstruction": [{"text": "40 mg daily"}],
            }
        },
    ],
}


def production_summarizer(note_text: str) -> str:
    """Stable production summary."""
    return (
        "James Carter follow-up for congestive heart failure. "
        "NT-proBNP remains elevated at 1840 pg/mL. "
        "Current medication includes furosemide 40 mg daily."
    )


def shadow_summarizer(note_text: str) -> str:
    """Candidate summary with slightly different emphasis."""
    return (
        "Cardiology follow-up for heart failure. "
        "NT-proBNP 1840 pg/mL and weight 98.4 kg were reviewed. "
        "Furosemide 40 mg daily remains active."
    )


def main():
    runner = ShadowModeRunner(min_similarity=0.35)
    result = runner.run_compare_only(
        production_fn=production_summarizer,
        shadow_fn=shadow_summarizer,
        patient_id="patient-101",
        fhir_bundle=SAMPLE_HAPI_FHIR_BUNDLE,
        source_system="hapi-fhir-r4",
    )

    print("=" * 72)
    print("Post 6: Shadow Mode Demonstration")
    print("=" * 72)
    print()
    print(f"Source system: {result.source_system}")
    print(f"Source format: {result.source_format}")
    print()
    print("Generated note from HAPI FHIR bundle:")
    print(result.note_text)
    print()
    print("Production output:")
    print(result.production_response.content if result.production_response else result.production_error)
    print()
    print("Shadow output:")
    print(result.shadow_response.content if result.shadow_response else result.shadow_error)
    print()
    print(f"Similarity score: {result.similarity_score:.3f}")
    print(f"Review required: {result.review_required}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Alert: {result.alert_severity} | {result.alert_message}")
    print(
        f"Rollout recommendation: {result.rollout_recommendation.decision} "
        f"at {result.rollout_recommendation.recommended_traffic_percentage}% traffic"
    )


if __name__ == "__main__":
    main()
