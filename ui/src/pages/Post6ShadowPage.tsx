import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";
import { SAMPLE_NOTE } from "../services/utils";
import { useAppContext } from "../app/AppContext";

export function Post6ShadowPage() {
  const { patientContext } = useAppContext();
  const [noteText, setNoteText] = useState(SAMPLE_NOTE);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function runShadow() {
    setLoading(true);
    setError("");
    try {
      const data = await api.shadowSummarize({
        patient_id: patientContext.patientId,
        note_text: noteText,
        source_system: "internal"
      });
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
        title="Post 6: Shadow Mode"
        subtitle="Execute production and candidate paths side-by-side without exposing candidate output to end users."
      />
      <section className="card stack">
        <label>
          Clinical Note
          <textarea rows={7} value={noteText} onChange={(e) => setNoteText(e.target.value)} />
        </label>
        <div className="row">
          <button onClick={() => void runShadow()} disabled={loading}>
            {loading ? "Running shadow..." : "Run Shadow Comparison"}
          </button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>
      {result && <JsonPanel title="Shadow Response" value={result} />}
    </div>
  );
}
