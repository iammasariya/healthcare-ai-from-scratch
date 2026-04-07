"""
Post 8 feedback loop services.

Implements low-friction clinician feedback capture and lightweight analytics
without introducing external infrastructure dependencies.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.config import settings


@dataclass
class ServedResponseEvent:
    """Track responses shown to clinicians to measure feedback coverage."""

    audit_id: str
    endpoint: str
    status: str
    served_at: str


@dataclass
class FeedbackEvent:
    """Persisted clinician feedback event."""

    feedback_id: str
    audit_id: str
    signal: str
    categories: list[str]
    correction_text: Optional[str]
    comment: Optional[str]
    clinician_role: Optional[str]
    seconds_to_submit: Optional[int]
    source_endpoint: str
    reference_found: bool
    priority: str
    created_at: str


@dataclass
class FeedbackQueueItem:
    """Item for high-priority manual review queue."""

    feedback_id: str
    audit_id: str
    reason: str
    categories: list[str]
    created_at: str


@dataclass
class FeedbackAnalyticsSnapshot:
    """Aggregated analytics for feedback quality and engagement."""

    window_days: int
    issued_response_count: int
    feedback_event_count: int
    feedback_coverage_rate: float
    positive_feedback_count: int
    negative_feedback_count: int
    negative_feedback_rate: float
    category_breakdown: dict[str, int]
    avg_seconds_to_submit: float
    high_priority_queue_count: int


class FeedbackStore:
    """Append-only JSONL storage for served responses and feedback events."""

    def __init__(self, directory: Optional[str] = None):
        self.directory = Path(directory or settings.feedback_store_dir)
        self.served_path = self.directory / "served_responses.jsonl"
        self.feedback_path = self.directory / "feedback_events.jsonl"

    def _append(self, path: Path, payload: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(payload) + "\n")

    def append_served(self, event: ServedResponseEvent) -> None:
        self._append(self.served_path, asdict(event))

    def append_feedback(self, event: FeedbackEvent) -> None:
        self._append(self.feedback_path, asdict(event))

    def _load_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []

        rows: list[dict] = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows

    def load_served(self) -> list[ServedResponseEvent]:
        return [ServedResponseEvent(**row) for row in self._load_jsonl(self.served_path)]

    def load_feedback(self) -> list[FeedbackEvent]:
        return [FeedbackEvent(**row) for row in self._load_jsonl(self.feedback_path)]


class FeedbackService:
    """Capture clinician feedback and compute Post 8 engagement analytics."""

    def __init__(self, store: Optional[FeedbackStore] = None):
        self.store = store or FeedbackStore()

    def record_served_response(self, audit_id: str, endpoint: str, status: str) -> None:
        self.store.append_served(
            ServedResponseEvent(
                audit_id=audit_id,
                endpoint=endpoint,
                status=status,
                served_at=datetime.utcnow().isoformat(),
            )
        )

    def _is_known_audit_id(self, audit_id: str) -> bool:
        return any(item.audit_id == audit_id for item in self.store.load_served())

    def _priority_for_feedback(self, signal: str, categories: list[str], correction_text: Optional[str]) -> str:
        if signal == "up":
            return "low"

        high_priority_categories = set(settings.feedback_high_priority_categories)
        if correction_text and correction_text.strip():
            return "high"
        if any(category in high_priority_categories for category in categories):
            return "high"
        return "medium"

    def submit_feedback(
        self,
        audit_id: str,
        signal: str,
        categories: Optional[list[str]] = None,
        correction_text: Optional[str] = None,
        comment: Optional[str] = None,
        clinician_role: Optional[str] = None,
        seconds_to_submit: Optional[int] = None,
        source_endpoint: str = "summarize",
    ) -> FeedbackEvent:
        normalized_categories = categories or []
        reference_found = self._is_known_audit_id(audit_id)
        priority = self._priority_for_feedback(signal, normalized_categories, correction_text)

        event = FeedbackEvent(
            feedback_id=str(uuid.uuid4()),
            audit_id=audit_id,
            signal=signal,
            categories=normalized_categories,
            correction_text=correction_text,
            comment=comment,
            clinician_role=clinician_role,
            seconds_to_submit=seconds_to_submit,
            source_endpoint=source_endpoint,
            reference_found=reference_found,
            priority=priority,
            created_at=datetime.utcnow().isoformat(),
        )
        self.store.append_feedback(event)
        return event

    def _window_bounds(self, window_days: int) -> datetime:
        return datetime.utcnow() - timedelta(days=window_days)

    def _parse_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value)

    def _in_window(self, timestamp: str, lower_bound: datetime) -> bool:
        return self._parse_datetime(timestamp) >= lower_bound

    def analytics(self, window_days: Optional[int] = None) -> FeedbackAnalyticsSnapshot:
        days = window_days or settings.feedback_default_analytics_days
        lower_bound = self._window_bounds(days)

        served = [
            item for item in self.store.load_served() if self._in_window(item.served_at, lower_bound)
        ]
        feedback = [
            item for item in self.store.load_feedback() if self._in_window(item.created_at, lower_bound)
        ]

        issued_audit_ids = {item.audit_id for item in served}
        feedback_audit_ids = {item.audit_id for item in feedback}

        positive_count = sum(1 for item in feedback if item.signal == "up")
        negative_count = sum(1 for item in feedback if item.signal == "down")
        seconds_values = [
            float(item.seconds_to_submit) for item in feedback if item.seconds_to_submit is not None
        ]
        avg_seconds = sum(seconds_values) / len(seconds_values) if seconds_values else 0.0

        category_breakdown: dict[str, int] = {}
        for item in feedback:
            for category in item.categories:
                category_breakdown[category] = category_breakdown.get(category, 0) + 1

        coverage = (
            len(feedback_audit_ids.intersection(issued_audit_ids)) / len(issued_audit_ids)
            if issued_audit_ids
            else 0.0
        )
        negative_rate = negative_count / len(feedback) if feedback else 0.0

        high_priority_count = sum(1 for item in feedback if item.priority == "high")

        return FeedbackAnalyticsSnapshot(
            window_days=days,
            issued_response_count=len(issued_audit_ids),
            feedback_event_count=len(feedback),
            feedback_coverage_rate=coverage,
            positive_feedback_count=positive_count,
            negative_feedback_count=negative_count,
            negative_feedback_rate=negative_rate,
            category_breakdown=category_breakdown,
            avg_seconds_to_submit=avg_seconds,
            high_priority_queue_count=high_priority_count,
        )

    def high_priority_queue(self, limit: Optional[int] = None) -> list[FeedbackQueueItem]:
        item_limit = limit or settings.feedback_max_queue_items
        feedback = [item for item in self.store.load_feedback() if item.priority == "high"]
        feedback = sorted(feedback, key=lambda item: item.created_at, reverse=True)

        queue: list[FeedbackQueueItem] = []
        for item in feedback[:item_limit]:
            categories = item.categories or ["uncategorized"]
            queue.append(
                FeedbackQueueItem(
                    feedback_id=item.feedback_id,
                    audit_id=item.audit_id,
                    reason=f"Negative feedback marked {item.priority} priority",
                    categories=categories,
                    created_at=item.created_at,
                )
            )
        return queue
