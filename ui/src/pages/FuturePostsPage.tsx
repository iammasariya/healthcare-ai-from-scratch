import { PageHeader } from "../components/PageHeader";

export function FuturePostsPage() {
  const placeholders = [
    {
      title: "Post 9: Failure Drills",
      detail: "Simulate model failure modes and rehearse rollback + incident protocols."
    },
    {
      title: "Post 10: Governance as Code",
      detail: "Policy enforcement, override approvals, and auditable controls."
    },
    {
      title: "Post 11: Service to Platform",
      detail: "Tenant controls, API versioning, and shared infra governance."
    },
    {
      title: "Post 12: Remaining Limits",
      detail: "Explicit boundaries of what engineering can and cannot solve."
    }
  ];

  return (
    <div className="page">
      <PageHeader title="Posts 9-12 Placeholder" subtitle="Reserved navigation nodes to keep future expansion coherent." />
      <section className="card-grid">
        {placeholders.map((item) => (
          <article key={item.title} className="card stack">
            <strong>{item.title}</strong>
            <small className="hint">{item.detail}</small>
          </article>
        ))}
      </section>
    </div>
  );
}
