import type { AuthMode, PatientContext } from "../types";

export type AuthProvider = {
  mode: AuthMode;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getPatientContext: () => Promise<PatientContext | null>;
  getAccessToken: () => Promise<string | null>;
};

class LocalAuthProvider implements AuthProvider {
  mode: AuthMode = "local";

  async login(): Promise<void> {
    return;
  }

  async logout(): Promise<void> {
    return;
  }

  async getPatientContext(): Promise<PatientContext | null> {
    return {
      patientId: "PT-12345",
      userId: "local-user"
    };
  }

  async getAccessToken(): Promise<string | null> {
    return null;
  }
}

class SmartAuthProvider implements AuthProvider {
  mode: AuthMode = "smart";

  async login(): Promise<void> {
    const clientId = import.meta.env.VITE_SMART_CLIENT_ID;
    const configuredRedirect = import.meta.env.VITE_SMART_REDIRECT_URI || `${window.location.origin}/launch`;
    const redirect = new URL(configuredRedirect, window.location.origin);
    const embedMode = new URLSearchParams(window.location.search).get("embed");
    if (embedMode === "1") {
      redirect.searchParams.set("embed", "1");
    }
    const redirectUri = redirect.toString();
    const iss = new URLSearchParams(window.location.search).get("iss") || import.meta.env.VITE_SMART_ISS;
    const launch = new URLSearchParams(window.location.search).get("launch") || undefined;

    if (!clientId || !iss) {
      throw new Error("SMART config missing. Set VITE_SMART_CLIENT_ID and VITE_SMART_ISS.");
    }

    const FHIR = await import("fhirclient");
    await FHIR.oauth2.authorize({
      clientId,
      scope: "launch/patient patient/*.read openid fhirUser",
      redirectUri,
      iss,
      launch
    });
  }

  async logout(): Promise<void> {
    sessionStorage.removeItem("smart_patient_id");
    sessionStorage.removeItem("smart_user_id");
  }

  async getPatientContext(): Promise<PatientContext | null> {
    const pid = sessionStorage.getItem("smart_patient_id");
    if (pid) {
      return {
        patientId: pid,
        userId: sessionStorage.getItem("smart_user_id") || undefined
      };
    }

    try {
      const FHIR = await import("fhirclient");
      const client = await FHIR.oauth2.ready();
      const patientId = client.patient.id;
      const fetchedUserId = typeof client.getFhirUser === "function" ? await client.getFhirUser() : undefined;
      const userId = fetchedUserId ?? undefined;
      if (patientId) {
        sessionStorage.setItem("smart_patient_id", patientId);
      }
      if (userId) {
        sessionStorage.setItem("smart_user_id", userId);
      }
      return patientId ? { patientId, userId } : null;
    } catch {
      return null;
    }
  }

  async getAccessToken(): Promise<string | null> {
    try {
      const FHIR = await import("fhirclient");
      const client = await FHIR.oauth2.ready();
      return client.state.tokenResponse?.access_token || null;
    } catch {
      return null;
    }
  }
}

export function createAuthProvider(mode: AuthMode): AuthProvider {
  return mode === "smart" ? new SmartAuthProvider() : new LocalAuthProvider();
}
