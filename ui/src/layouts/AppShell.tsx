import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAppContext } from "../app/AppContext";

function LinkItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink to={to} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
      {label}
    </NavLink>
  );
}

export function AppShell() {
  const location = useLocation();
  const {
    authMode,
    setAuthMode,
    patientContext,
    setPatientContext,
    login,
    logout,
    authMessage,
    hydrateSmartContext
  } = useAppContext();

  const query = new URLSearchParams(location.search);
  const embedMode = query.get("embed") === "1";

  return (
    <div className={`app-shell ${embedMode ? "embed" : ""}`}>
      {!embedMode && (
        <aside className="sidebar">
          <h1>Healthcare AI Workbench</h1>
          <div className="subtitle">Production operations UI for Posts 1-8 and platform workflows.</div>

          <div className="nav-group">
            <div className="nav-group-title">Operations</div>
            <LinkItem to="/" label="Overview" />
            <LinkItem to="/command-center" label="Command Center" />
            <LinkItem to="/patient-workspace" label="Patient Workspace" />
            <LinkItem to="/quality-evaluation" label="Quality & Evaluation" />
            <LinkItem to="/rollout-monitoring" label="Rollout & Monitoring" />
            <LinkItem to="/feedback-review" label="Feedback & Review" />
          </div>

          <div className="nav-group">
            <div className="nav-group-title">Control Plane</div>
            <LinkItem to="/release-gate" label="Release Gate" />
            <LinkItem to="/audit-explorer" label="Audit Explorer" />
            <LinkItem to="/incidents" label="Incident Workspace" />
            <LinkItem to="/launch" label="SMART Launch" />
          </div>

          <div className="nav-group">
            <div className="nav-group-title">Labs (Post Series)</div>
            <LinkItem to="/post-1" label="Post 1: Foundation" />
            <LinkItem to="/post-2" label="Post 2: LLM" />
            <LinkItem to="/post-3" label="Post 3: Prompting" />
            <LinkItem to="/post-4" label="Post 4: Variability" />
            <LinkItem to="/post-5" label="Post 5: Evaluation" />
            <LinkItem to="/post-6" label="Post 6: Shadow" />
            <LinkItem to="/post-7" label="Post 7: Monitoring" />
            <LinkItem to="/post-8" label="Post 8: Feedback" />
          </div>

          <div className="nav-group">
            <div className="nav-group-title">Future</div>
            <LinkItem to="/future" label="Posts 9-12 Placeholder" />
            <LinkItem to="/governance" label="Governance (P10)" />
            <LinkItem to="/platform-admin" label="Platform Admin (P11)" />
            <LinkItem to="/platform" label="Final Product Vision" />
          </div>

          <div className="sidebar-foot">
            Core principle: monitor to control. This interface keeps release safety, audits, and clinical feedback in one operator surface.
          </div>
        </aside>
      )}

      <main className="main">
        <div className="topbar">
          <div className="row">
            {!embedMode && (
              <label>
                Auth mode
                <select
                  value={authMode}
                  onChange={(e) => setAuthMode(e.target.value as "local" | "smart")}
                >
                  <option value="local">Local</option>
                  <option value="smart">SMART on FHIR</option>
                </select>
              </label>
            )}
            <button className="secondary" onClick={() => void login()}>
              Login
            </button>
            <button className="secondary" onClick={() => void logout()}>
              Logout
            </button>
            {authMode === "smart" && (
              <button className="secondary" onClick={() => void hydrateSmartContext()}>
                Load SMART Context
              </button>
            )}
          </div>

          <div className="row">
            <label>
              Patient ID
              <input
                value={patientContext.patientId}
                onChange={(e) => setPatientContext({ ...patientContext, patientId: e.target.value })}
              />
            </label>
            <span className="badge ok">{authMessage}</span>
            {embedMode && <span className="badge warn">Embed Mode</span>}
          </div>
        </div>

        <Outlet />
      </main>
    </div>
  );
}
