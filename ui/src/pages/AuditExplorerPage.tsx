import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";
import { AuditSearchHit } from "../types";

export function AuditExplorerPage() {
  const [query, setQuery] = useState("");
  const [days, setDays] = useState(14);
  const [results, setResults] = useState<AuditSearchHit[] | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function search() {
    setLoading(true);
    setError("");
    try {
      const data = await api.auditSearch(query, days, 200);
      setResults(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Audit Explorer"
        subtitle="Search audit-linked events and trace decisions across operational workflows."
      />

      <section className="card stack">
        <div className="row">
          <label>
            Query (audit_id prefix)
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="audit-id or leave blank" />
          </label>
          <label>
            Days
            <input type="number" min={1} max={90} value={days} onChange={(e) => setDays(Number(e.target.value))} />
          </label>
          <button onClick={() => void search()} disabled={loading}>{loading ? "Searching..." : "Search"}</button>
        </div>
        {error && <span className="badge danger">{error}</span>}
      </section>

      {results !== null && <JsonPanel title="Audit Search Results" value={results} />}
    </div>
  );
}
