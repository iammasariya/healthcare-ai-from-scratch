import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";
import { MonitoringStatus } from "../types";

export function Post7MonitoringPage() {
  const [status, setStatus] = useState<MonitoringStatus | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadStatus() {
    setLoading(true);
    setError("");
    try {
      const data = await api.monitoringStatus();
      setStatus(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function evaluate() {
    setLoading(true);
    setError("");
    try {
      const data = await api.monitoringEvaluate();
      setStatus(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function reset() {
    setLoading(true);
    setError("");
    try {
      const data = await api.monitoringReset();
      setStatus(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Post 7: Monitoring That Triggers Action"
        subtitle="Inspect runtime guardrails, trigger evaluation, and reset actions via explicit operational controls."
      />

      <section className="card stack">
        <div className="row">
          <button onClick={() => void loadStatus()} disabled={loading}>Load Status</button>
          <button className="secondary" onClick={() => void evaluate()} disabled={loading}>Evaluate Now</button>
          <button className="secondary" onClick={() => void reset()} disabled={loading}>Reset Actions</button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>

      {status && (
        <>
          <section className="card-grid">
            {status.actions.map((action) => (
              <article key={action.action} className="card stack">
                <strong>{action.action}</strong>
                <span className={`badge ${action.active ? "danger" : "ok"}`}>
                  {action.active ? "ACTIVE" : "inactive"}
                </span>
                <small className="hint">{action.reason || "No active reason"}</small>
              </article>
            ))}
          </section>
          <JsonPanel title="Monitoring Status" value={status} />
        </>
      )}
    </div>
  );
}
