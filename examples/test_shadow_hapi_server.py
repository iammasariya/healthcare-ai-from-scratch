"""
Post 6 shadow mode demonstration using a live HAPI FHIR server.

Usage:
    export HAPI_FHIR_BASE_URL=https://hapi.fhir.org/baseR4
    export HAPI_FHIR_PATIENT_ID=<patient-id>
    python examples/test_shadow_hapi_server.py

This example fetches patient context from HAPI FHIR, converts it into note-like
clinical context, and runs a production vs candidate comparison without needing
the LLM API.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.shadow import HAPIFHIRClient, ShadowModeRunner


def production_summarizer(note_text: str) -> str:
    """Simple deterministic stand-in for the production path."""
    return " ".join(note_text.split()[:24]) + " ..."


def candidate_summarizer(note_text: str) -> str:
    """Simple deterministic stand-in for the candidate path."""
    words = note_text.split()
    selected = words[:12] + words[-12:] if len(words) > 24 else words
    return " ".join(selected) + " ..."


def main():
    base_url = os.getenv("HAPI_FHIR_BASE_URL")
    patient_id = os.getenv("HAPI_FHIR_PATIENT_ID")

    if not base_url or not patient_id:
        raise SystemExit(
            "Set HAPI_FHIR_BASE_URL and HAPI_FHIR_PATIENT_ID before running this example."
        )

    client = HAPIFHIRClient(base_url=base_url)
    bundle = client.fetch_patient_context_bundle(patient_id)

    runner = ShadowModeRunner(min_similarity=0.20)
    result = runner.run_compare_only(
        production_fn=production_summarizer,
        shadow_fn=candidate_summarizer,
        patient_id=patient_id,
        fhir_bundle=bundle,
        source_system="hapi-fhir-r4-live",
    )

    print("=" * 72)
    print("Post 6: Live HAPI FHIR Shadow Mode")
    print("=" * 72)
    print()
    print(f"HAPI server: {base_url}")
    print(f"Patient ID: {patient_id}")
    print()
    print("Rendered clinical context:")
    print(result.note_text)
    print()
    print("Production output:")
    print(result.production_response.content if result.production_response else result.production_error)
    print()
    print("Shadow output:")
    print(result.shadow_response.content if result.shadow_response else result.shadow_error)
    print()
    print(f"Similarity score: {result.similarity_score:.3f}")
    print(f"Recommendation: {result.recommendation}")
    print(
        f"Rollout recommendation: {result.rollout_recommendation.decision} "
        f"at {result.rollout_recommendation.recommended_traffic_percentage}% traffic"
    )


if __name__ == "__main__":
    main()
