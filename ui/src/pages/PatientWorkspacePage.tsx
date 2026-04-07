import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";

export function PatientWorkspacePage() {
  return (
    <div className="page">
      <PageHeader
        title="Patient Workspace"
        subtitle="Clinician-facing flow: ingest, summarize, prompt-safe comparison, and variability checks."
      />

      <section className="card-grid">
        <article className="card stack">
          <strong>Ingest + Audit Trail</strong>
          <small className="hint">Foundation request contract and audit trace.</small>
          <Link className="card-link" to="/post-1">Open Post 1 Lab</Link>
        </article>
        <article className="card stack">
          <strong>Summarize</strong>
          <small className="hint">Generate production summary and inspect metrics.</small>
          <Link className="card-link" to="/post-2">Open Post 2 Lab</Link>
        </article>
        <article className="card stack">
          <strong>Prompt-Safe Comparison</strong>
          <small className="hint">Run candidate prompt in shadow before rollout.</small>
          <Link className="card-link" to="/post-3">Open Post 3 Lab</Link>
        </article>
        <article className="card stack">
          <strong>Variability Lab</strong>
          <small className="hint">Measure consistency drift across repeated runs.</small>
          <Link className="card-link" to="/post-4">Open Post 4 Lab</Link>
        </article>
      </section>
    </div>
  );
}
