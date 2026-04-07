export function JsonPanel({ title, value }: { title: string; value: unknown }) {
  return (
    <div className="card">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <strong>{title}</strong>
      </div>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </div>
  );
}
