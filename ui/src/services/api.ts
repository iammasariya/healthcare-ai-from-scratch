import {
  AuditSearchHit,
  FeedbackAnalytics,
  FeedbackQueueItem,
  FeedbackResponse,
  HealthResponse,
  IncidentCreateRequest,
  IncidentRecord,
  IngestResponse,
  MonitoringStatus,
  ShadowResponse,
  SummarizeResponse
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    },
    ...init
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data?.detail || data?.message || `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return data as T;
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  ingest: (payload: { patient_id: string; note_text: string }) =>
    request<IngestResponse>("/ingest", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  summarize: (payload: { patient_id: string; note_text: string }) =>
    request<SummarizeResponse>("/summarize", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  shadowSummarize: (payload: {
    patient_id: string;
    note_text?: string;
    source_system?: string;
    candidate_prompt_version?: string;
  }) =>
    request<ShadowResponse>("/shadow/summarize", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  monitoringStatus: () => request<MonitoringStatus>("/monitoring/status"),
  monitoringEvaluate: () =>
    request<MonitoringStatus>("/monitoring/evaluate", {
      method: "POST",
      body: JSON.stringify({})
    }),
  monitoringReset: () =>
    request<MonitoringStatus>("/monitoring/actions/reset", {
      method: "POST",
      body: JSON.stringify({})
    }),
  submitFeedback: (payload: {
    audit_id: string;
    signal: "up" | "down";
    categories: string[];
    correction_text?: string;
    comment?: string;
    clinician_role?: string;
    seconds_to_submit?: number;
    source_endpoint?: string;
  }) =>
    request<FeedbackResponse>("/feedback", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  feedbackAnalytics: (windowDays = 7) =>
    request<FeedbackAnalytics>(`/feedback/analytics?window_days=${windowDays}`),
  feedbackQueue: (limit = 20) =>
    request<FeedbackQueueItem[]>(`/feedback/queue?limit=${limit}`),
  auditSearch: (query = "", days = 14, limit = 100) =>
    request<AuditSearchHit[]>(
      `/audits/search?query=${encodeURIComponent(query)}&days=${days}&limit=${limit}`
    ),
  listIncidents: () => request<IncidentRecord[]>("/incidents"),
  createIncident: (payload: IncidentCreateRequest) =>
    request<IncidentRecord>("/incidents", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  syncIncidents: () =>
    request<IncidentRecord[]>("/incidents/sync-monitoring", {
      method: "POST",
      body: JSON.stringify({})
    }),
  resolveIncident: (incidentId: string, owner?: string) =>
    request<IncidentRecord>(
      `/incidents/${encodeURIComponent(incidentId)}/resolve${owner ? `?owner=${encodeURIComponent(owner)}` : ""}`,
      {
        method: "POST",
        body: JSON.stringify({})
      }
    )
};
