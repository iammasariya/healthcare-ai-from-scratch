import { useMemo, useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import { SAMPLE_NOTE, fuzzyTokenSimilarity } from "../services/utils";
import { useAppContext } from "../app/AppContext";

export function Post5EvaluationPage() {
  const { patientContext } = useAppContext();
  const [noteText, setNoteText] = useState(SAMPLE_NOTE);
  const [expected, setExpected] = useState("Patient with fatigue and dizziness, elevated blood pressure, history of diabetes and hypertension, currently on metformin and lisinopril.");
  const [actual, setActual] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function generateActual() {
    setLoading(true);
    setError("");
    try {
      const response = await api.summarize({ patient_id: patientContext.patientId, note_text: noteText });
      setActual(response.summary || "");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const score = useMemo(() => {
    if (!actual.trim() || !expected.trim()) {
      return 0;
    }
    return fuzzyTokenSimilarity(expected, actual);
  }, [expected, actual]);

  return (
    <div className="page">
      <PageHeader
        title="Post 5: Evaluation Bench"
        subtitle="Compare expected and generated outputs with transparent fuzzy scoring." 
      />
      <section className="card stack">
        <label>
          Clinical Note
          <textarea rows={6} value={noteText} onChange={(e) => setNoteText(e.target.value)} />
        </label>
        <div className="row">
          <button onClick={() => void generateActual()} disabled={loading}>
            {loading ? "Generating..." : "Generate Candidate Output"}
          </button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>

      <section className="card-grid">
        <article className="card stack">
          <strong>Expected Output</strong>
          <textarea rows={8} value={expected} onChange={(e) => setExpected(e.target.value)} />
        </article>
        <article className="card stack">
          <strong>Actual Output</strong>
          <textarea rows={8} value={actual} onChange={(e) => setActual(e.target.value)} />
        </article>
      </section>

      <section className="card">
        <div className="kpi">{score.toFixed(3)}</div>
        <small className="hint">Fuzzy token similarity score (local evaluator)</small>
      </section>
    </div>
  );
}
