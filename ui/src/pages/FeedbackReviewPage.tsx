import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";

export function FeedbackReviewPage() {
  return (
    <div className="page">
      <PageHeader
        title="Feedback & Review"
        subtitle="Capture clinician feedback, inspect participation health, and triage high-priority corrections."
      />
      <section className="card-grid">
        <article className="card stack">
          <strong>Feedback Hub</strong>
          <small className="hint">Submit and review structured feedback.</small>
          <Link className="card-link" to="/post-8">Open Post 8 Lab</Link>
        </article>
        <article className="card stack">
          <strong>Audit Explorer</strong>
          <small className="hint">Trace events by audit ID across control-plane stores.</small>
          <Link className="card-link" to="/audit-explorer">Open Audit Explorer</Link>
        </article>
      </section>
    </div>
  );
}
