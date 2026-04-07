import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";
import { SAMPLE_NOTE } from "../services/utils";
import { useAppContext } from "../app/AppContext";

export function Post3PromptPage() {
  const { patientContext } = useAppContext();
  const [noteText, setNoteText] = useState(SAMPLE_NOTE);
  const [candidatePromptVersion, setCandidatePromptVersion] = useState("1.1.0");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function comparePromptVersion() {
    setLoading(true);
    setError("");
    try {
      const data = await api.shadowSummarize({
        patient_id: patientContext.patientId,
        note_text: noteText,
        source_system: "internal",
        candidate_prompt_version: candidatePromptVersion
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
        title="Post 3: Prompt Versioning"
        subtitle="Use shadow path with candidate prompt version to validate prompt changes without direct exposure."
      />
      <section className="card stack">
        <label>
          Candidate Prompt Version
          <input value={candidatePromptVersion} onChange={(e) => setCandidatePromptVersion(e.target.value)} />
        </label>
        <label>
          Clinical Note
          <textarea rows={7} value={noteText} onChange={(e) => setNoteText(e.target.value)} />
        </label>
        <div className="row">
          <button onClick={() => void comparePromptVersion()} disabled={loading}>
            {loading ? "Running..." : "Compare Prompt Version"}
          </button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>
      {result && <JsonPanel title="Prompt Comparison (Shadow)" value={result} />}
    </div>
  );
}
