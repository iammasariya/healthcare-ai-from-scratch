import { useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { JsonPanel } from "../components/JsonPanel";
import { api } from "../services/api";

const CATEGORY_OPTIONS = [
  "clinical_accuracy",
  "missing_critical_detail",
  "hallucination",
  "safety_concern",
  "tone",
  "formatting"
];

export function Post8FeedbackPage() {
  const [auditId, setAuditId] = useState("");
  const [signal, setSignal] = useState<"up" | "down">("down");
  const [categories, setCategories] = useState<string[]>(["clinical_accuracy"]);
  const [correctionText, setCorrectionText] = useState("");
  const [analytics, setAnalytics] = useState<Record<string, unknown> | null>(null);
  const [queue, setQueue] = useState<Record<string, unknown>[] | null>(null);
  const [submitResult, setSubmitResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitFeedback() {
    setLoading(true);
    setError("");
    try {
      const response = await api.submitFeedback({
        audit_id: auditId,
        signal,
        categories,
        correction_text: correctionText || undefined,
        source_endpoint: "summarize"
      });
      setSubmitResult(response);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function loadAnalytics() {
    setLoading(true);
    setError("");
    try {
      setAnalytics(await api.feedbackAnalytics(7));
      setQueue(await api.feedbackQueue(20));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function toggleCategory(category: string) {
    setCategories((current) =>
      current.includes(category)
        ? current.filter((value) => value !== category)
        : [...current, category]
    );
  }

  return (
    <div className="page">
      <PageHeader
        title="Post 8: Human Feedback Without Burning Clinicians"
        subtitle="Capture low-friction feedback, review participation analytics, and triage high-priority items."
      />

      <section className="card stack">
        <label>
          Audit ID of response being reviewed
          <input value={auditId} onChange={(e) => setAuditId(e.target.value)} placeholder="Paste audit_id from summarize/shadow response" />
        </label>

        <label>
          Signal
          <select value={signal} onChange={(e) => setSignal(e.target.value as "up" | "down") }>
            <option value="up">Up</option>
            <option value="down">Down</option>
          </select>
        </label>

        <div className="stack">
          <small className="hint">Categories (max 3 in backend policy)</small>
          <div className="row">
            {CATEGORY_OPTIONS.map((category) => (
              <button
                key={category}
                className="secondary"
                type="button"
                onClick={() => toggleCategory(category)}
              >
                {categories.includes(category) ? `✓ ${category}` : category}
              </button>
            ))}
          </div>
        </div>

        <label>
          Optional correction text
          <textarea rows={4} value={correctionText} onChange={(e) => setCorrectionText(e.target.value)} />
        </label>

        <div className="row">
          <button onClick={() => void submitFeedback()} disabled={loading || !auditId.trim()}>
            Submit Feedback
          </button>
          <button className="secondary" onClick={() => void loadAnalytics()} disabled={loading}>
            Refresh Analytics + Queue
          </button>
          {error && <span className="badge danger">{error}</span>}
        </div>
      </section>

      {submitResult && <JsonPanel title="Feedback Submission Result" value={submitResult} />}
      {analytics && <JsonPanel title="Feedback Analytics (7 days)" value={analytics} />}
      {queue && <JsonPanel title="High Priority Feedback Queue" value={queue} />}
    </div>
  );
}
