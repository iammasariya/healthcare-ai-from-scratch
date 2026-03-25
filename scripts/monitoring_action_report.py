"""
Print current Post 7 actionable monitoring status.

Usage:
    python scripts/monitoring_action_report.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.monitoring import MonitoringService


def main():
    service = MonitoringService()
    state = service.evaluate()

    print("=" * 72)
    print("Monitoring Action Report")
    print("=" * 72)
    print()
    print(f"Last evaluated: {state.last_evaluated_at}")

    snapshot = state.snapshot
    if snapshot is None:
        print("No monitoring snapshot available yet.")
    else:
        print("Snapshot:")
        print(f"- total runs: {snapshot.total_runs}")
        print(f"- divergence rate: {snapshot.divergence_rate:.1%}")
        print(f"- critical alert rate: {snapshot.critical_alert_rate:.1%}")
        print(f"- error rate: {snapshot.error_rate:.1%}")
        print(f"- avg shadow latency: {snapshot.avg_shadow_latency_ms:.1f}ms")
        print(f"- avg shadow cost: ${snapshot.avg_shadow_cost_usd:.5f}")

    print()
    print("Actions:")
    for action in [state.pause_shadow_mode, state.freeze_candidate_rollout]:
        status = "ACTIVE" if action.active else "inactive"
        print(f"- {action.action}: {status}")
        if action.reason:
            print(f"  reason: {action.reason}")
        if action.expires_at:
            print(f"  expires_at: {action.expires_at}")


if __name__ == "__main__":
    main()
