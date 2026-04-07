"""
Print Post 8 feedback analytics and high-priority queue.

Usage:
    python scripts/feedback_analytics_report.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.feedback import FeedbackService
from app.config import settings


def main():
    service = FeedbackService()
    snapshot = service.analytics(window_days=settings.feedback_default_analytics_days)
    queue = service.high_priority_queue(limit=settings.feedback_max_queue_items)

    print("=" * 72)
    print("Feedback Analytics Report")
    print("=" * 72)
    print()
    print(f"Window: {snapshot.window_days} days")
    print(f"- issued responses: {snapshot.issued_response_count}")
    print(f"- feedback events: {snapshot.feedback_event_count}")
    print(f"- coverage rate: {snapshot.feedback_coverage_rate:.1%}")
    print(f"- negative rate: {snapshot.negative_feedback_rate:.1%}")
    print(f"- avg seconds to submit: {snapshot.avg_seconds_to_submit:.1f}")
    print(f"- high-priority queue count: {snapshot.high_priority_queue_count}")

    if snapshot.category_breakdown:
        print()
        print("Categories:")
        for category, count in sorted(snapshot.category_breakdown.items(), key=lambda item: item[1], reverse=True):
            print(f"- {category}: {count}")

    if queue:
        print()
        print("High-priority queue:")
        for item in queue:
            print(
                f"- {item.feedback_id} | audit={item.audit_id} | "
                f"categories={','.join(item.categories)} | created_at={item.created_at}"
            )


if __name__ == "__main__":
    main()
