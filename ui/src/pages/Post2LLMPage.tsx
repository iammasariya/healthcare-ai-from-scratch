import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";
import { SAMPLE_NOTE } from "../services/utils";
import { useAppContext } from "../app/AppContext";

export function Post2LLMPage() {
  const { patientContext } = useAppContext();
  const [noteText, setNoteText] = useState(SAMPLE_NOTE);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function summarize() {
    setLoading(true);
    setError("");
    try {
      const data = await api.summarize({ patient_id: patientContext.patientId, note_text: noteText });
      setResult(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Post 2: LLM Integration"
        subtitle="Run summarization and inspect latency/token/cost metrics tied to audit IDs."
      />
      <section className="card stack">
        <label>
          Clinical Note
          <textarea rows={7} value={noteText} onChange={(e) => setNoteText(e.target.value)} />
        </label>
        <div className="row">
          <button onClick={() => void summarize()} disabled={loading}>
            {loading ? "Summarizing..." : "Summarize"}
          </button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>
      {result && <JsonPanel title="Summarize Response" value={result} />}
    </div>
  );
}
