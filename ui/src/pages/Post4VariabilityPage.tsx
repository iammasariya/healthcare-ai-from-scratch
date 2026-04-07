import { useMemo, useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import { SAMPLE_NOTE, fuzzyTokenSimilarity } from "../services/utils";
import { useAppContext } from "../app/AppContext";

export function Post4VariabilityPage() {
  const { patientContext } = useAppContext();
  const [noteText, setNoteText] = useState(SAMPLE_NOTE);
  const [runs, setRuns] = useState(3);
  const [outputs, setOutputs] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function runVariability() {
    setLoading(true);
    setError("");
    setOutputs([]);

    const collected: string[] = [];
    try {
      for (let index = 0; index < runs; index += 1) {
        const response = await api.summarize({ patient_id: patientContext.patientId, note_text: noteText });
        if (response.summary) {
          collected.push(response.summary);
        }
      }
      setOutputs(collected);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const metrics = useMemo(() => {
    if (outputs.length < 2) {
      return null;
    }

    const similarities: number[] = [];
    for (let i = 0; i < outputs.length; i += 1) {
      for (let j = i + 1; j < outputs.length; j += 1) {
        similarities.push(fuzzyTokenSimilarity(outputs[i], outputs[j]));
      }
    }

    const avg = similarities.reduce((acc, value) => acc + value, 0) / similarities.length;
    const unique = new Set(outputs).size;
    return { avgSimilarity: avg, uniqueOutputs: unique, totalRuns: outputs.length };
  }, [outputs]);

  return (
    <div className="page">
      <PageHeader
        title="Post 4: Variability Lab"
        subtitle="Run repeated summarization and inspect output similarity to detect consistency drift."
      />
      <section className="card stack">
        <div className="row">
          <label>
            Runs
            <input
              type="number"
              min={2}
              max={6}
              value={runs}
              onChange={(e) => setRuns(Number(e.target.value))}
            />
          </label>
        </div>
        <label>
          Clinical Note
          <textarea rows={6} value={noteText} onChange={(e) => setNoteText(e.target.value)} />
        </label>
        <div className="row">
          <button onClick={() => void runVariability()} disabled={loading}>
            {loading ? "Running..." : "Measure Variability"}
          </button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>

      {metrics && (
        <section className="card-grid">
          <article className="card">
            <div className="kpi">{metrics.avgSimilarity.toFixed(3)}</div>
            <small className="hint">Average token similarity</small>
          </article>
          <article className="card">
            <div className="kpi">{metrics.uniqueOutputs}</div>
            <small className="hint">Unique outputs across runs</small>
          </article>
          <article className="card">
            <div className="kpi">{metrics.totalRuns}</div>
            <small className="hint">Total responses collected</small>
          </article>
        </section>
      )}

      {outputs.length > 0 && (
        <section className="card stack">
          <strong>Collected Outputs</strong>
          {outputs.map((output, idx) => (
            <pre key={`${idx}-${output.slice(0, 8)}`}>Run {idx + 1}: {output}</pre>
          ))}
        </section>
      )}
    </div>
  );
}
