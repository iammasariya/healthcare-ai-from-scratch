"""
Audit explorer utilities for control-plane search.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.feedback import FeedbackService
from app.shadow import ShadowResultStore


@dataclass
class AuditSearchHit:
    audit_id: str
    source: str
    event_type: str
    timestamp: str
    details: dict


class AuditExplorerService:
    def __init__(
        self,
        feedback_service: Optional[FeedbackService] = None,
        shadow_store: Optional[ShadowResultStore] = None,
    ):
        self.feedback_service = feedback_service or FeedbackService()
        self.shadow_store = shadow_store or ShadowResultStore()

    def _within_days(self, ts: str, days: int) -> bool:
        lower = datetime.utcnow() - timedelta(days=days)
        return datetime.fromisoformat(ts) >= lower

    def search(self, query: Optional[str] = None, days: int = 14, limit: int = 100) -> list[AuditSearchHit]:
        normalized_query = (query or "").strip().lower()
        hits: list[AuditSearchHit] = []

        for served in self.feedback_service.store.load_served():
            if not self._within_days(served.served_at, days):
                continue
            if normalized_query and normalized_query not in served.audit_id.lower():
                continue
            hits.append(
                AuditSearchHit(
                    audit_id=served.audit_id,
                    source="feedback_store",
                    event_type="served_response",
                    timestamp=served.served_at,
                    details={"endpoint": served.endpoint, "status": served.status},
                )
            )

        for feedback in self.feedback_service.store.load_feedback():
            if not self._within_days(feedback.created_at, days):
                continue
            if normalized_query and normalized_query not in feedback.audit_id.lower():
                continue
            hits.append(
                AuditSearchHit(
                    audit_id=feedback.audit_id,
                    source="feedback_store",
                    event_type="feedback",
                    timestamp=feedback.created_at,
                    details={
                        "signal": feedback.signal,
                        "priority": feedback.priority,
                        "categories": feedback.categories,
                    },
                )
            )

        for path in sorted(Path(self.shadow_store.directory).glob("*.json")):
            ts = datetime.utcfromtimestamp(path.stat().st_mtime).isoformat()
            if not self._within_days(ts, days):
                continue
            shadow = self.shadow_store.load_record(path)
            if normalized_query and normalized_query not in shadow.audit_id.lower():
                continue
            hits.append(
                AuditSearchHit(
                    audit_id=shadow.audit_id,
                    source="shadow_store",
                    event_type="shadow_run",
                    timestamp=ts,
                    details={
                        "divergent": shadow.divergent,
                        "similarity_score": shadow.similarity_score,
                        "alert_severity": shadow.alert_severity,
                    },
                )
            )

        hits.sort(key=lambda item: item.timestamp, reverse=True)
        return hits[:limit]
