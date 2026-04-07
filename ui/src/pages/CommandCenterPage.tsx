import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import { FeedbackAnalytics, MonitoringStatus } from "../types";

export function CommandCenterPage() {
  const [health, setHealth] = useState<string>("unknown");
  const [monitoring, setMonitoring] = useState<MonitoringStatus | null>(null);
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [h, m, a] = await Promise.all([
          api.health(),
          api.monitoringStatus(),
          api.feedbackAnalytics(7)
        ]);
        setHealth(h.status);
        setMonitoring(m);
        setAnalytics(a);
      } catch (e) {
        setError((e as Error).message);
      }
    }
    void load();
  }, []);

  const activeActions = useMemo(
    () => monitoring?.actions.filter((item) => item.active).length || 0,
    [monitoring]
  );

  return (
    <div className="page">
      <PageHeader
        title="Command Center"
        subtitle="Operational confidence view: service health, guardrails, and feedback quality in one panel."
      />

      {error && <section className="card"><span className="badge danger">{error}</span></section>}

      <section className="card-grid">
        <article className="card stack">
          <div className="kpi">{health}</div>
          <small className="hint">Service health</small>
        </article>
        <article className="card stack">
          <div className="kpi">{monitoring?.snapshot?.divergence_rate?.toFixed(2) || "0.00"}</div>
          <small className="hint">Shadow divergence rate</small>
        </article>
        <article className="card stack">
          <div className="kpi">{activeActions}</div>
          <small className="hint">Active guardrail actions</small>
        </article>
        <article className="card stack">
          <div className="kpi">{analytics?.feedback_coverage_rate ? `${(analytics.feedback_coverage_rate * 100).toFixed(1)}%` : "0%"}</div>
          <small className="hint">Feedback coverage (7d)</small>
        </article>
      </section>

      <section className="card-grid">
        <article className="card stack">
          <strong>Release Gate</strong>
          <small className="hint">Run go/no-go checks before shipping candidate changes.</small>
          <Link className="card-link" to="/release-gate">Open Release Gate</Link>
        </article>
        <article className="card stack">
          <strong>Incident Workspace</strong>
          <small className="hint">Track open incidents and sync monitoring-triggered records.</small>
          <Link className="card-link" to="/incidents">Open Incident Workspace</Link>
        </article>
        <article className="card stack">
          <strong>Audit Explorer</strong>
          <small className="hint">Search audit-linked events across served responses, feedback, and shadow runs.</small>
          <Link className="card-link" to="/audit-explorer">Open Audit Explorer</Link>
        </article>
      </section>
    </div>
  );
}
