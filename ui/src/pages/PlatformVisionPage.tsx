import { PageHeader } from "../components/PageHeader";

export function PlatformVisionPage() {
  return (
    <div className="page">
      <PageHeader
        title="Final Product Vision"
        subtitle="Open-source platform package for health system adoption with SMART embed support."
      />

      <section className="card-grid">
        <article className="card stack">
          <strong>Health System Deployability</strong>
          <small className="hint">Containerized backend + Vite UI + configurable auth and org-level settings.</small>
        </article>
        <article className="card stack">
          <strong>EHR Embedding</strong>
          <small className="hint">SMART launch route and iframe-ready UX footprint for Epic/Cerner integration patterns.</small>
        </article>
        <article className="card stack">
          <strong>Operational Controls</strong>
          <small className="hint">Monitoring actions, feedback triage, and future governance modules in one operator surface.</small>
        </article>
      </section>

      <section className="card">
        <strong>Implementation note</strong>
        <p>
          This page is a product blueprint placeholder. As Posts 9-12 ship, this route becomes the release-control dashboard
          for production policy, incidents, and compliance exports.
        </p>
      </section>
    </div>
  );
}
