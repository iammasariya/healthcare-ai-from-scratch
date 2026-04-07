import { Link } from "react-router-dom";

export function OverviewPage() {
  return (
    <div className="page">
      <section className="page-header hero">
        <div className="hero-title-row">
          <div>
            <h2 style={{ marginTop: 0, marginBottom: 8 }}>Healthcare AI Platform Console</h2>
            <p style={{ marginTop: 0, marginBottom: 12, color: "var(--text-muted)" }}>
              End-to-end production workflow for clinical AI: patient-facing behavior, quality controls,
              rollout safety, and human feedback in one interface.
            </p>
          </div>
          <span className="muted-chip">Posts 1-8 complete</span>
        </div>

        <div className="kpi-strip">
          <div className="kpi-tile">
            <div className="value">4</div>
            <div className="label">Primary workflows</div>
          </div>
          <div className="kpi-tile">
            <div className="value">3</div>
            <div className="label">Control-plane modules</div>
          </div>
          <div className="kpi-tile">
            <div className="value">SMART</div>
            <div className="label">EHR launch ready</div>
          </div>
        </div>
      </section>

      <section className="card-grid">
        <article className="card stack">
          <strong>Command Center</strong>
          <small className="hint">Single-pane operational status for health, guardrails, and feedback signals.</small>
          <Link className="card-link" to="/command-center">Open Command Center</Link>
        </article>
        <article className="card stack">
          <strong>Patient Workspace</strong>
          <small className="hint">Clinical request lifecycle from ingest to LLM output quality checks.</small>
          <Link className="card-link" to="/patient-workspace">Open Patient Workspace</Link>
        </article>
        <article className="card stack">
          <strong>Rollout & Monitoring</strong>
          <small className="hint">Shadow comparison, guardrail actions, and incident management workflow.</small>
          <Link className="card-link" to="/rollout-monitoring">Open Rollout Workflow</Link>
        </article>
        <article className="card stack">
          <strong>Feedback & Review</strong>
          <small className="hint">Clinician feedback triage with audit-traceable investigations.</small>
          <Link className="card-link" to="/feedback-review">Open Feedback Workflow</Link>
        </article>
      </section>

      <section className="card">
        <strong>Control Plane</strong>
        <p>
          Release decisions and incident handling are first-class surfaces:
          <Link className="card-link" to="/release-gate"> Release Gate</Link>,
          <Link className="card-link" to="/audit-explorer"> Audit Explorer</Link>, and
          <Link className="card-link" to="/incidents"> Incident Workspace</Link>.
        </p>
      </section>

      <section className="card">
        <strong>SMART on FHIR Deployment Path</strong>
        <p>
          Use <code>/launch?iss=...&launch=...&embed=1</code> for EHR iframe launch. Embed mode removes side navigation and keeps only patient-context controls and page content.
        </p>
      </section>
    </div>
  );
}
