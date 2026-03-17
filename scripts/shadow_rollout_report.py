"""
Summarize saved Post 6 shadow-mode results.

Usage:
    python scripts/shadow_rollout_report.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.shadow import ShadowResultStore


def main():
    store = ShadowResultStore()
    records = store.load_all()
    recommendation = store.recommend_rollout()

    print("=" * 72)
    print("Shadow Rollout Report")
    print("=" * 72)
    print()
    print(f"Saved shadow runs: {len(records)}")

    if not records:
        print("No shadow runs recorded yet.")
        return

    recent = records[-max(settings.shadow_promotion_min_requests, 1):]
    print()
    print("Most recent runs:")
    for record in recent:
        similarity = (
            f"{record.similarity_score:.3f}"
            if record.similarity_score is not None else "n/a"
        )
        print(
            f"- {record.audit_id}: source={record.source_system}, "
            f"similarity={similarity}, divergent={record.divergent}, "
            f"alert={record.alert_severity}"
        )

    print()
    print("Rollout recommendation:")
    print(f"- decision: {recommendation.decision}")
    print(f"- recommended traffic: {recommendation.recommended_traffic_percentage}%")
    print(f"- avg similarity: {recommendation.avg_similarity:.3f}")
    print(f"- divergence rate: {recommendation.divergence_rate:.1%}")
    print(f"- reason: {recommendation.reason}")


if __name__ == "__main__":
    main()
