import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";

export function QualityEvaluationPage() {
  return (
    <div className="page">
      <PageHeader
        title="Quality & Evaluation"
        subtitle="Evaluate outputs, compare baseline/candidate behavior, and prepare release decisions."
      />
      <section className="card-grid">
        <article className="card stack">
          <strong>Evaluation Bench</strong>
          <small className="hint">Expected vs generated comparisons with transparent scoring.</small>
          <Link className="card-link" to="/post-5">Open Post 5 Lab</Link>
        </article>
        <article className="card stack">
          <strong>Release Gate Wizard</strong>
          <small className="hint">Automated go/no-go checks across live guardrails and feedback.</small>
          <Link className="card-link" to="/release-gate">Open Wizard</Link>
        </article>
      </section>
    </div>
  );
}
