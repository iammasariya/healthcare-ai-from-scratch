export function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <section className="page-header">
      <h2 style={{ margin: 0 }}>{title}</h2>
      <p style={{ marginBottom: 0, color: "var(--text-muted)" }}>{subtitle}</p>
    </section>
  );
}
