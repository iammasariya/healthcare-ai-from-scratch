"""
Post 7 monitoring services that trigger operational actions.

This module turns shadow-mode telemetry into actionable safeguards:
- Pause shadow execution when quality degrades
- Freeze rollout recommendations when performance budgets are exceeded
- Persist action state so behavior is consistent across requests
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.config import settings
from app.shadow import ShadowModeRunRecord, ShadowResultStore


@dataclass
class MonitoringSnapshot:
    """Aggregated metrics over a window of recent shadow runs."""

    total_runs: int
    divergent_runs: int
    divergence_rate: float
    critical_alert_runs: int
    critical_alert_rate: float
    error_runs: int
    error_rate: float
    avg_shadow_latency_ms: float
    avg_shadow_cost_usd: float
    window_size: int


@dataclass
class MonitoringAction:
    """Action status persisted by monitoring."""

    action: str
    active: bool
    reason: Optional[str]
    triggered_at: Optional[str]
    expires_at: Optional[str]


@dataclass
class MonitoringState:
    """Persisted monitoring state."""

    last_evaluated_at: Optional[str]
    pause_shadow_mode: MonitoringAction
    freeze_candidate_rollout: MonitoringAction
    snapshot: Optional[MonitoringSnapshot]


class MonitoringStateStore:
    """File-backed storage for monitoring state."""

    def __init__(self, state_file: Optional[str] = None):
        self.path = Path(state_file or settings.monitoring_state_file)

    def load(self) -> MonitoringState:
        if not self.path.exists():
            return MonitoringState(
                last_evaluated_at=None,
                pause_shadow_mode=MonitoringAction(
                    action="pause_shadow_mode",
                    active=False,
                    reason=None,
                    triggered_at=None,
                    expires_at=None,
                ),
                freeze_candidate_rollout=MonitoringAction(
                    action="freeze_candidate_rollout",
                    active=False,
                    reason=None,
                    triggered_at=None,
                    expires_at=None,
                ),
                snapshot=None,
            )

        with open(self.path, "r") as f:
            payload = json.load(f)

        snapshot_payload = payload.get("snapshot")
        snapshot = MonitoringSnapshot(**snapshot_payload) if snapshot_payload else None

        return MonitoringState(
            last_evaluated_at=payload.get("last_evaluated_at"),
            pause_shadow_mode=MonitoringAction(**payload["pause_shadow_mode"]),
            freeze_candidate_rollout=MonitoringAction(**payload["freeze_candidate_rollout"]),
            snapshot=snapshot,
        )

    def save(self, state: MonitoringState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(asdict(state), f, indent=2)

    def reset(self) -> MonitoringState:
        state = MonitoringState(
            last_evaluated_at=datetime.utcnow().isoformat(),
            pause_shadow_mode=MonitoringAction(
                action="pause_shadow_mode",
                active=False,
                reason=None,
                triggered_at=None,
                expires_at=None,
            ),
            freeze_candidate_rollout=MonitoringAction(
                action="freeze_candidate_rollout",
                active=False,
                reason=None,
                triggered_at=None,
                expires_at=None,
            ),
            snapshot=None,
        )
        self.save(state)
        return state


class MonitoringService:
    """Evaluate shadow telemetry and apply Post 7 monitoring actions."""

    def __init__(
        self,
        result_store: Optional[ShadowResultStore] = None,
        state_store: Optional[MonitoringStateStore] = None,
    ):
        self.result_store = result_store or ShadowResultStore()
        self.state_store = state_store or MonitoringStateStore()

    def _is_action_active(self, action: MonitoringAction) -> bool:
        if not action.active:
            return False
        if not action.expires_at:
            return True
        try:
            expires_at = datetime.fromisoformat(action.expires_at)
        except ValueError:
            return False
        return datetime.utcnow() < expires_at

    def get_state(self) -> MonitoringState:
        state = self.state_store.load()
        changed = False

        if state.pause_shadow_mode.active and not self._is_action_active(state.pause_shadow_mode):
            state.pause_shadow_mode.active = False
            state.pause_shadow_mode.reason = None
            state.pause_shadow_mode.triggered_at = None
            state.pause_shadow_mode.expires_at = None
            changed = True

        if (
            state.freeze_candidate_rollout.active
            and not self._is_action_active(state.freeze_candidate_rollout)
        ):
            state.freeze_candidate_rollout.active = False
            state.freeze_candidate_rollout.reason = None
            state.freeze_candidate_rollout.triggered_at = None
            state.freeze_candidate_rollout.expires_at = None
            changed = True

        if changed:
            self.state_store.save(state)

        return state

    def _window_records(self) -> list[ShadowModeRunRecord]:
        records = self.result_store.load_all()
        window = max(settings.monitoring_window_size, 1)
        return records[-window:]

    def _avg(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def build_snapshot(self) -> MonitoringSnapshot:
        records = self._window_records()
        total = len(records)

        if total == 0:
            return MonitoringSnapshot(
                total_runs=0,
                divergent_runs=0,
                divergence_rate=0.0,
                critical_alert_runs=0,
                critical_alert_rate=0.0,
                error_runs=0,
                error_rate=0.0,
                avg_shadow_latency_ms=0.0,
                avg_shadow_cost_usd=0.0,
                window_size=max(settings.monitoring_window_size, 1),
            )

        divergent_runs = sum(1 for record in records if record.divergent)
        critical_alert_runs = sum(1 for record in records if record.alert_severity == "critical")
        error_runs = sum(1 for record in records if record.error)
        shadow_latency_values = [
            record.shadow_latency_ms for record in records if record.shadow_latency_ms is not None
        ]
        shadow_cost_values = [
            record.shadow_cost_usd for record in records if record.shadow_cost_usd is not None
        ]

        return MonitoringSnapshot(
            total_runs=total,
            divergent_runs=divergent_runs,
            divergence_rate=divergent_runs / total,
            critical_alert_runs=critical_alert_runs,
            critical_alert_rate=critical_alert_runs / total,
            error_runs=error_runs,
            error_rate=error_runs / total,
            avg_shadow_latency_ms=self._avg(shadow_latency_values),
            avg_shadow_cost_usd=self._avg(shadow_cost_values),
            window_size=max(settings.monitoring_window_size, 1),
        )

    def _activate_action(self, action: MonitoringAction, reason: str) -> None:
        now = datetime.utcnow()
        action.active = True
        action.reason = reason
        action.triggered_at = now.isoformat()
        action.expires_at = (now + timedelta(minutes=settings.monitoring_action_ttl_minutes)).isoformat()

    def evaluate(self) -> MonitoringState:
        state = self.get_state()
        snapshot = self.build_snapshot()
        state.snapshot = snapshot
        state.last_evaluated_at = datetime.utcnow().isoformat()

        # Require enough evidence before hard actions.
        if snapshot.total_runs < settings.monitoring_min_runs_for_actions:
            self.state_store.save(state)
            return state

        if (
            snapshot.divergence_rate > settings.monitoring_max_divergence_rate
            or snapshot.critical_alert_rate > settings.monitoring_max_critical_alert_rate
        ):
            self._activate_action(
                state.pause_shadow_mode,
                reason=(
                    "Quality guardrail breached: divergence or critical alert rate too high "
                    f"(divergence={snapshot.divergence_rate:.1%}, "
                    f"critical_alerts={snapshot.critical_alert_rate:.1%})"
                ),
            )

        if (
            snapshot.avg_shadow_latency_ms > settings.monitoring_max_avg_shadow_latency_ms
            or snapshot.avg_shadow_cost_usd > settings.monitoring_max_avg_shadow_cost_usd
        ):
            self._activate_action(
                state.freeze_candidate_rollout,
                reason=(
                    "Performance budget breached: average shadow latency or cost too high "
                    f"(latency={snapshot.avg_shadow_latency_ms:.1f}ms, "
                    f"cost=${snapshot.avg_shadow_cost_usd:.5f})"
                ),
            )

        self.state_store.save(state)
        return state

    def reset_actions(self) -> MonitoringState:
        return self.state_store.reset()

    def is_shadow_paused(self) -> tuple[bool, Optional[str]]:
        state = self.get_state()
        action = state.pause_shadow_mode
        return self._is_action_active(action), action.reason

    def is_rollout_frozen(self) -> tuple[bool, Optional[str]]:
        state = self.get_state()
        action = state.freeze_candidate_rollout
        return self._is_action_active(action), action.reason
