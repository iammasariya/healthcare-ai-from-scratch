import { useEffect, useMemo, useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { useAppContext } from "../app/AppContext";

export function SmartLaunchPage() {
  const { authMode, setAuthMode, login, hydrateSmartContext, patientContext, authMessage } = useAppContext();
  const [params, setParams] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [readyAttempted, setReadyAttempted] = useState(false);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const out: Record<string, string> = {};
    searchParams.forEach((value, key) => {
      out[key] = value;
    });
    setParams(out);

    // If launched from EHR, default to SMART mode to avoid manual toggles.
    if (searchParams.get("iss") || searchParams.get("launch") || searchParams.get("code")) {
      setAuthMode("smart");
    }
  }, [setAuthMode]);

  const isLaunchCallback = useMemo(() => Boolean(params.code || params.state), [params.code, params.state]);

  useEffect(() => {
    async function tryReady() {
      if (authMode !== "smart" || !isLaunchCallback || readyAttempted) {
        return;
      }
      try {
        setError("");
        await hydrateSmartContext();
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setReadyAttempted(true);
      }
    }

    void tryReady();
  }, [authMode, hydrateSmartContext, isLaunchCallback, readyAttempted]);

  async function initializeSmartLaunch() {
    setError("");
    try {
      await login();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="SMART on FHIR Launch Adapter"
        subtitle="EHR launch-safe OAuth flow with patient-context hydration and embed-mode support."
      />

      <section className="card stack">
        <div className="row">
          <span className="badge ok">Auth mode: {authMode}</span>
          <span className="badge ok">Patient: {patientContext.patientId}</span>
          {window.self !== window.top && <span className="badge warn">iFrame session</span>}
        </div>

        <div className="row">
          <button onClick={() => void initializeSmartLaunch()} disabled={authMode !== "smart"}>
            Start SMART OAuth
          </button>
          <button className="secondary" onClick={() => void hydrateSmartContext()} disabled={authMode !== "smart"}>
            Hydrate Context
          </button>
        </div>

        {authMode !== "smart" && <small className="hint">Switch auth mode to SMART for EHR launch.</small>}
        {error && <span className="badge danger">{error}</span>}
        <small className="hint">{authMessage}</small>
      </section>

      <section className="card stack">
        <strong>Launch Parameters</strong>
        <pre>{JSON.stringify(params, null, 2)}</pre>
      </section>

      <section className="card stack">
        <strong>Embedding Reference</strong>
        <small className="hint">
          For EHR iframe launch, use <code>/launch?embed=1</code> as the SMART redirect base and include <code>iss</code>/<code>launch</code>. In production, enforce origin allowlists and <code>frame-ancestors</code> CSP at the reverse proxy.
        </small>
      </section>
    </div>
  );
}
