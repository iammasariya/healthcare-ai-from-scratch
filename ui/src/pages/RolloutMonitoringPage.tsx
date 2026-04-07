import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";

export function RolloutMonitoringPage() {
  return (
    <div className="page">
      <PageHeader
        title="Rollout & Monitoring"
        subtitle="Candidate rollout safety with shadow comparisons, guardrails, and incident response."
      />
      <section className="card-grid">
        <article className="card stack">
          <strong>Shadow Mode</strong>
          <small className="hint">Side-by-side production vs candidate comparison.</small>
          <Link className="card-link" to="/post-6">Open Post 6 Lab</Link>
        </article>
        <article className="card stack">
          <strong>Monitoring Controls</strong>
          <small className="hint">Evaluate/reset guardrail actions.</small>
          <Link className="card-link" to="/post-7">Open Post 7 Lab</Link>
        </article>
        <article className="card stack">
          <strong>Incident Workspace</strong>
          <small className="hint">Manage active incidents and sync from monitoring actions.</small>
          <Link className="card-link" to="/incidents">Open Incident Workspace</Link>
        </article>
      </section>
    </div>
  );
}
