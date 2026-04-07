import React, { createContext, useContext, useMemo, useState } from "react";
import type { AuthMode, PatientContext } from "../types";
import { createAuthProvider } from "../smart/auth";

type AppState = {
  authMode: AuthMode;
  setAuthMode: (mode: AuthMode) => void;
  patientContext: PatientContext;
  setPatientContext: (ctx: PatientContext) => void;
  authMessage: string;
  setAuthMessage: (msg: string) => void;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  hydrateSmartContext: () => Promise<void>;
};

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [authMode, setAuthMode] = useState<AuthMode>(
    (import.meta.env.VITE_AUTH_MODE as AuthMode) || "local"
  );
  const [patientContext, setPatientContext] = useState<PatientContext>({ patientId: "PT-12345" });
  const [authMessage, setAuthMessage] = useState("Local mode active");

  const provider = useMemo(() => createAuthProvider(authMode), [authMode]);

  async function login() {
    await provider.login();
    const ctx = await provider.getPatientContext();
    if (ctx) {
      setPatientContext(ctx);
    }
    setAuthMessage(`${provider.mode.toUpperCase()} login initialized`);
  }

  async function logout() {
    await provider.logout();
    setAuthMessage(`${provider.mode.toUpperCase()} session cleared`);
  }

  async function hydrateSmartContext() {
    const ctx = await provider.getPatientContext();
    if (ctx) {
      setPatientContext(ctx);
      setAuthMessage("SMART patient context loaded");
    }
  }

  return (
    <AppContext.Provider
      value={{
        authMode,
        setAuthMode,
        patientContext,
        setPatientContext,
        authMessage,
        setAuthMessage,
        login,
        logout,
        hydrateSmartContext
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error("useAppContext must be used within AppProvider");
  }
  return ctx;
}
