export type HealthResponse = {
  status: string;
  timestamp: string;
  version?: string;
};

export type IngestResponse = {
  audit_id: string;
  received_at: string;
  status: string;
  patient_id?: string;
};

export type SummarizeResponse = {
  audit_id: string;
  received_at: string;
  status: string;
  patient_id?: string;
  summary?: string | null;
  llm_metrics?: {
    model: string;
    tokens_used: number;
    latency_ms: number;
    cost_usd: number;
    prompt_version?: string | null;
    prompt_hash?: string | null;
  } | null;
  error?: string | null;
};

export type ShadowResponse = {
  audit_id: string;
  status: string;
  source_format: string;
  production_summary?: string | null;
  shadow_summary?: string | null;
  similarity_score?: number | null;
  divergent: boolean;
  recommendation: string;
  alert: {
    severity: string;
    message: string;
  };
  rollout_decision: {
    decision: string;
    recommended_traffic_percentage: number;
    reason: string;
  };
  error?: string | null;
};

export type MonitoringStatus = {
  monitoring_enabled: boolean;
  last_evaluated_at?: string | null;
  snapshot?: {
    total_runs: number;
    divergence_rate: number;
    critical_alert_rate: number;
    avg_shadow_latency_ms: number;
    avg_shadow_cost_usd: number;
    feedback_event_count?: number;
  } | null;
  actions: {
    action: string;
    active: boolean;
    reason?: string | null;
    expires_at?: string | null;
  }[];
};

export type FeedbackResponse = {
  feedback_id: string;
  audit_id: string;
  status: string;
  signal: "up" | "down";
  priority: string;
  reference_found: boolean;
  created_at: string;
};

export type FeedbackAnalytics = {
  window_days: number;
  issued_response_count: number;
  feedback_event_count: number;
  feedback_coverage_rate: number;
  positive_feedback_count: number;
  negative_feedback_count: number;
  negative_feedback_rate: number;
  category_breakdown: Record<string, number>;
  avg_seconds_to_submit: number;
  high_priority_queue_count: number;
};

export type FeedbackQueueItem = {
  feedback_id: string;
  audit_id: string;
  reason: string;
  categories: string[];
  created_at: string;
};

export type AuditSearchHit = {
  audit_id: string;
  source: string;
  event_type: string;
  timestamp: string;
  details: Record<string, unknown>;
};

export type IncidentRecord = {
  incident_id: string;
  title: string;
  status: "open" | "resolved";
  severity: "warning" | "critical" | string;
  source: string;
  linked_action?: string | null;
  linked_audit_id?: string | null;
  summary: string;
  owner?: string | null;
  created_at: string;
  updated_at: string;
};

export type IncidentCreateRequest = {
  title: string;
  severity: "warning" | "critical" | string;
  source: string;
  summary: string;
  owner?: string;
  linked_action?: string;
  linked_audit_id?: string;
};

export type AuthMode = "local" | "smart";

export type PatientContext = {
  patientId: string;
  userId?: string;
  encounterId?: string;
};
