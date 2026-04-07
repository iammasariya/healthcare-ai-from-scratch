import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import { FeedbackAnalytics, MonitoringStatus } from "../types";

export function ReleaseGatePage() {
  const [result, setResult] = useState<{
    go: boolean;
    checks: string[];
    monitoring?: MonitoringStatus;
    analytics?: FeedbackAnalytics;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function evaluate() {
    setLoading(true);
    setError("");
    try {
      const [monitoring, analytics] = await Promise.all([
        api.monitoringEvaluate(),
        api.feedbackAnalytics(7)
      ]);

      const checks: string[] = [];
      let go = true;

      const activeActions = monitoring.actions.filter((item) => item.active);
      if (activeActions.length > 0) {
        go = false;
        checks.push(`Blocked: ${activeActions.length} active monitoring action(s)`);
      } else {
        checks.push("Pass: no active monitoring actions");
      }

      if (analytics.negative_feedback_rate > 0.5 && analytics.feedback_event_count >= 5) {
        go = false;
        checks.push("Blocked: negative feedback rate too high in last 7 days");
      } else {
        checks.push("Pass: feedback sentiment within policy threshold");
      }

      if (analytics.feedback_coverage_rate < 0.05 && analytics.issued_response_count >= 20) {
        checks.push("Warn: low feedback coverage may hide quality issues");
      } else {
        checks.push("Pass: sufficient feedback coverage for current volume");
      }

      setResult({ go, checks, monitoring, analytics });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Release Gate Wizard"
        subtitle="Go/No-Go checks across monitoring and feedback signals before rollout changes."
      />

      <section className="card stack">
        <div className="row">
          <button onClick={() => void evaluate()} disabled={loading}>{loading ? "Evaluating..." : "Run Gate Checks"}</button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>

      {result && (
        <section className="card stack">
          <span className={`badge ${result.go ? "ok" : "danger"}`}>{result.go ? "GO" : "NO-GO"}</span>
          {result.checks.map((check) => (
            <small key={check} className="hint">- {check}</small>
          ))}
        </section>
      )}
    </div>
  );
}
