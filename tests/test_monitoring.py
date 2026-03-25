"""
Tests for Post 7 actionable monitoring.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.monitoring import MonitoringService, MonitoringStateStore
from app.shadow import ShadowModeRunRecord, ShadowResultStore


def _record(
    audit_id: str,
    *,
    divergent: bool,
    alert_severity: str,
    error: Optional[str],
    latency: float,
    cost: float,
):
    return ShadowModeRunRecord(
        audit_id=audit_id,
        patient_id="PT-1",
        source_system="internal",
        source_format="clinical_note",
        production_model="prod",
        shadow_model="shadow",
        similarity_score=0.2 if divergent else 0.9,
        divergent=divergent,
        review_required=divergent,
        recommendation="test",
        production_latency_ms=100.0,
        shadow_latency_ms=latency,
        production_cost_usd=0.01,
        shadow_cost_usd=cost,
        alert_triggered=alert_severity != "none",
        alert_severity=alert_severity,
        error=error,
    )


class TestMonitoringService:
    def test_empty_snapshot(self, tmp_path: Path):
        result_store = ShadowResultStore(directory=str(tmp_path / "shadow_results"))
        state_store = MonitoringStateStore(state_file=str(tmp_path / "monitoring_state.json"))
        service = MonitoringService(result_store=result_store, state_store=state_store)

        snapshot = service.build_snapshot()
        assert snapshot.total_runs == 0
        assert snapshot.divergence_rate == 0.0
        assert snapshot.critical_alert_rate == 0.0

    def test_evaluate_triggers_pause_for_quality_breach(self, tmp_path: Path, monkeypatch):
        result_store = ShadowResultStore(directory=str(tmp_path / "shadow_results"))
        state_store = MonitoringStateStore(state_file=str(tmp_path / "monitoring_state.json"))
        service = MonitoringService(result_store=result_store, state_store=state_store)

        monkeypatch.setattr("app.monitoring.settings.monitoring_window_size", 5)
        monkeypatch.setattr("app.monitoring.settings.monitoring_min_runs_for_actions", 3)
        monkeypatch.setattr("app.monitoring.settings.monitoring_max_divergence_rate", 0.30)
        monkeypatch.setattr("app.monitoring.settings.monitoring_max_critical_alert_rate", 0.20)

        result_store.save("a1", _record("a1", divergent=True, alert_severity="critical", error=None, latency=110.0, cost=0.01))
        result_store.save("a2", _record("a2", divergent=True, alert_severity="critical", error=None, latency=115.0, cost=0.01))
        result_store.save("a3", _record("a3", divergent=False, alert_severity="none", error=None, latency=120.0, cost=0.01))

        state = service.evaluate()
        assert state.pause_shadow_mode.active is True
        assert "Quality guardrail breached" in (state.pause_shadow_mode.reason or "")

    def test_evaluate_triggers_rollout_freeze_for_budget_breach(self, tmp_path: Path, monkeypatch):
        result_store = ShadowResultStore(directory=str(tmp_path / "shadow_results"))
        state_store = MonitoringStateStore(state_file=str(tmp_path / "monitoring_state.json"))
        service = MonitoringService(result_store=result_store, state_store=state_store)

        monkeypatch.setattr("app.monitoring.settings.monitoring_window_size", 5)
        monkeypatch.setattr("app.monitoring.settings.monitoring_min_runs_for_actions", 3)
        monkeypatch.setattr("app.monitoring.settings.monitoring_max_avg_shadow_latency_ms", 1000.0)
        monkeypatch.setattr("app.monitoring.settings.monitoring_max_avg_shadow_cost_usd", 0.01)

        result_store.save("a1", _record("a1", divergent=False, alert_severity="none", error=None, latency=2000.0, cost=0.02))
        result_store.save("a2", _record("a2", divergent=False, alert_severity="none", error=None, latency=2100.0, cost=0.02))
        result_store.save("a3", _record("a3", divergent=False, alert_severity="none", error=None, latency=1900.0, cost=0.02))

        state = service.evaluate()
        assert state.freeze_candidate_rollout.active is True
        assert "Performance budget breached" in (state.freeze_candidate_rollout.reason or "")

    def test_expired_actions_auto_clear_on_read(self, tmp_path: Path):
        result_store = ShadowResultStore(directory=str(tmp_path / "shadow_results"))
        state_store = MonitoringStateStore(state_file=str(tmp_path / "monitoring_state.json"))
        service = MonitoringService(result_store=result_store, state_store=state_store)

        state = state_store.reset()
        state.pause_shadow_mode.active = True
        state.pause_shadow_mode.reason = "test"
        state.pause_shadow_mode.triggered_at = datetime.utcnow().isoformat()
        state.pause_shadow_mode.expires_at = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
        state_store.save(state)

        loaded = service.get_state()
        assert loaded.pause_shadow_mode.active is False
        assert loaded.pause_shadow_mode.reason is None
