"""
Tests for Post 8 feedback services.
"""

from pathlib import Path

from app.feedback import FeedbackService, FeedbackStore


class TestFeedbackService:
    def test_submit_feedback_marks_reference_found(self, tmp_path: Path):
        store = FeedbackStore(directory=str(tmp_path / "feedback_data"))
        service = FeedbackService(store=store)

        service.record_served_response("audit-1", endpoint="summarize", status="completed")
        event = service.submit_feedback(
            audit_id="audit-1",
            signal="down",
            categories=["clinical_accuracy"],
            correction_text="Patient denies chest pain, not confirms it.",
            seconds_to_submit=12,
        )

        assert event.reference_found is True
        assert event.priority == "high"

    def test_submit_feedback_handles_unknown_audit_id(self, tmp_path: Path):
        store = FeedbackStore(directory=str(tmp_path / "feedback_data"))
        service = FeedbackService(store=store)

        event = service.submit_feedback(
            audit_id="unknown-audit",
            signal="up",
            categories=["helpful"],
        )

        assert event.reference_found is False
        assert event.priority == "low"

    def test_feedback_analytics_counts_coverage_and_negativity(self, tmp_path: Path):
        store = FeedbackStore(directory=str(tmp_path / "feedback_data"))
        service = FeedbackService(store=store)

        service.record_served_response("audit-1", endpoint="summarize", status="completed")
        service.record_served_response("audit-2", endpoint="summarize", status="completed")
        service.submit_feedback(audit_id="audit-1", signal="up", categories=["helpful"], seconds_to_submit=10)
        service.submit_feedback(audit_id="audit-2", signal="down", categories=["tone"], seconds_to_submit=20)

        snapshot = service.analytics(window_days=7)
        assert snapshot.issued_response_count == 2
        assert snapshot.feedback_event_count == 2
        assert snapshot.feedback_coverage_rate == 1.0
        assert snapshot.negative_feedback_count == 1
        assert snapshot.negative_feedback_rate == 0.5
        assert snapshot.avg_seconds_to_submit == 15.0

    def test_high_priority_queue_returns_recent_items(self, tmp_path: Path):
        store = FeedbackStore(directory=str(tmp_path / "feedback_data"))
        service = FeedbackService(store=store)

        service.submit_feedback(
            audit_id="audit-1",
            signal="down",
            categories=["hallucination"],
            correction_text="Medication was fabricated.",
        )
        service.submit_feedback(
            audit_id="audit-2",
            signal="up",
            categories=["helpful"],
        )

        queue = service.high_priority_queue(limit=10)
        assert len(queue) == 1
        assert queue[0].audit_id == "audit-1"
