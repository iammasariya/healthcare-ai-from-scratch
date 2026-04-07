import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";
import { SAMPLE_NOTE } from "../services/utils";
import { useAppContext } from "../app/AppContext";

export function Post1FoundationPage() {
  const { patientContext } = useAppContext();
  const [noteText, setNoteText] = useState(SAMPLE_NOTE);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      const data = await api.ingest({ patient_id: patientContext.patientId, note_text: noteText });
      setResult(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <PageHeader title="Post 1: Foundation" subtitle="Validate contracts, request tracing, and deterministic ingestion." />
      <section className="card stack">
        <label>
          Clinical Note
          <textarea rows={6} value={noteText} onChange={(e) => setNoteText(e.target.value)} />
        </label>
        <div className="row">
          <button onClick={() => void submit()} disabled={loading}>
            {loading ? "Submitting..." : "Ingest"}
          </button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>
      {result && <JsonPanel title="Ingest Response" value={result} />}
    </div>
  );
}
