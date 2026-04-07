import { useEffect, useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";
import { IncidentRecord } from "../types";

export function IncidentWorkspacePage() {
  const [incidents, setIncidents] = useState<IncidentRecord[]>([]);
  const [title, setTitle] = useState("Manual incident");
  const [summary, setSummary] = useState("Operator-reported issue requiring review");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      setIncidents(await api.listIncidents());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function syncMonitoring() {
    setLoading(true);
    setError("");
    try {
      await api.syncIncidents();
      setIncidents(await api.listIncidents());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function createManual() {
    setLoading(true);
    setError("");
    try {
      await api.createIncident({
        title,
        severity: "warning",
        source: "operator",
        summary
      });
      setIncidents(await api.listIncidents());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function resolve(incidentId: string) {
    setLoading(true);
    setError("");
    try {
      await api.resolveIncident(incidentId);
      setIncidents(await api.listIncidents());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Incident Workspace"
        subtitle="Track and resolve incidents, including monitoring-triggered operational events."
      />

      <section className="card stack">
        <div className="row">
          <button onClick={() => void refresh()} disabled={loading}>Refresh</button>
          <button className="secondary" onClick={() => void syncMonitoring()} disabled={loading}>Sync Monitoring Actions</button>
        </div>

        <div className="row">
          <label>
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
          </label>
          <label style={{ minWidth: 340 }}>
            Summary
            <input value={summary} onChange={(e) => setSummary(e.target.value)} />
          </label>
          <button className="secondary" onClick={() => void createManual()} disabled={loading}>Create Manual Incident</button>
        </div>

        {error && <span className="badge danger">{error}</span>}
      </section>

      <section className="card stack">
        <strong>Open Incidents</strong>
        {incidents.length === 0 && <small className="hint">No incidents recorded.</small>}
        {incidents.map((item) => (
          <article key={item.incident_id} className="card stack">
            <div className="row" style={{ justifyContent: "space-between" }}>
              <strong>{item.title}</strong>
              <span className={`badge ${item.status === "open" ? "warn" : "ok"}`}>{item.status}</span>
            </div>
            <small className="hint">Severity: {item.severity} | Source: {item.source} | Updated: {item.updated_at}</small>
            <small className="hint">{item.summary}</small>
            {item.status === "open" && (
              <div className="row">
                <button className="secondary" onClick={() => void resolve(item.incident_id)} disabled={loading}>Resolve</button>
              </div>
            )}
          </article>
        ))}
      </section>

      <JsonPanel title="Incident Records" value={incidents} />
    </div>
  );
}
