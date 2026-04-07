"""
Lightweight incident workspace for operational response.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import settings
from app.monitoring import MonitoringService


@dataclass
class IncidentRecord:
    incident_id: str
    title: str
    status: str
    severity: str
    source: str
    linked_action: Optional[str]
    linked_audit_id: Optional[str]
    summary: str
    owner: Optional[str]
    created_at: str
    updated_at: str


class IncidentStore:
    def __init__(self, path: Optional[str] = None):
        self.path = Path(path or settings.incident_store_file)

    def _load(self) -> list[IncidentRecord]:
        if not self.path.exists():
            return []
        with open(self.path, "r") as f:
            payload = json.load(f)
        return [IncidentRecord(**item) for item in payload]

    def _save(self, records: list[IncidentRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump([asdict(item) for item in records], f, indent=2)

    def list(self) -> list[IncidentRecord]:
        return sorted(self._load(), key=lambda item: item.updated_at, reverse=True)

    def create(
        self,
        title: str,
        severity: str,
        source: str,
        summary: str,
        owner: Optional[str] = None,
        linked_action: Optional[str] = None,
        linked_audit_id: Optional[str] = None,
    ) -> IncidentRecord:
        records = self._load()
        now = datetime.utcnow().isoformat()
        incident = IncidentRecord(
            incident_id=str(uuid.uuid4()),
            title=title,
            status="open",
            severity=severity,
            source=source,
            linked_action=linked_action,
            linked_audit_id=linked_audit_id,
            summary=summary,
            owner=owner,
            created_at=now,
            updated_at=now,
        )
        records.append(incident)
        self._save(records)
        return incident

    def update_status(self, incident_id: str, status: str, owner: Optional[str] = None) -> IncidentRecord:
        records = self._load()
        for record in records:
            if record.incident_id == incident_id:
                record.status = status
                record.updated_at = datetime.utcnow().isoformat()
                if owner is not None:
                    record.owner = owner
                self._save(records)
                return record
        raise ValueError("Incident not found")


class IncidentService:
    def __init__(self, store: Optional[IncidentStore] = None, monitoring: Optional[MonitoringService] = None):
        self.store = store or IncidentStore()
        self.monitoring = monitoring or MonitoringService()

    def list_incidents(self) -> list[IncidentRecord]:
        return self.store.list()

    def create_incident(
        self,
        title: str,
        severity: str,
        source: str,
        summary: str,
        owner: Optional[str] = None,
        linked_action: Optional[str] = None,
        linked_audit_id: Optional[str] = None,
    ) -> IncidentRecord:
        return self.store.create(
            title=title,
            severity=severity,
            source=source,
            summary=summary,
            owner=owner,
            linked_action=linked_action,
            linked_audit_id=linked_audit_id,
        )

    def resolve_incident(self, incident_id: str, owner: Optional[str] = None) -> IncidentRecord:
        return self.store.update_status(incident_id, status="resolved", owner=owner)

    def sync_from_monitoring_actions(self) -> list[IncidentRecord]:
        state = self.monitoring.get_state()
        active = [
            state.pause_shadow_mode,
            state.freeze_candidate_rollout,
        ]
        existing = self.store.list()
        created: list[IncidentRecord] = []

        for action in active:
            if not action.active:
                continue

            already_open = any(
                item.status == "open" and item.linked_action == action.action
                for item in existing
            )
            if already_open:
                continue

            severity = "critical" if action.action == "pause_shadow_mode" else "warning"
            summary = action.reason or "Monitoring action triggered"
            created.append(
                self.store.create(
                    title=f"Monitoring action: {action.action}",
                    severity=severity,
                    source="monitoring",
                    summary=summary,
                    linked_action=action.action,
                )
            )

        return created
