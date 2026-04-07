# Healthcare AI UI

Production-focused Vite + React + TypeScript console for the healthcare AI platform.

## What This UI Covers

- Post 1-8 capabilities in one coherent product surface
- Workflow-first navigation (not tutorial-only navigation)
- Control-plane modules: release gate, audit explorer, incident workspace
- SMART on FHIR launch route with iframe embed mode for EHR integrations

## Run Locally

```bash
cd ui
npm install
npm run dev
```

Default URL: `http://localhost:5173`

Backend API calls go to `/api/*` and are proxied to `http://localhost:8000` in local dev.

## Environment Variables

Create `ui/.env` (optional):

```bash
VITE_API_BASE_URL=/api
VITE_AUTH_MODE=local

# SMART on FHIR
VITE_SMART_CLIENT_ID=your-smart-client-id
VITE_SMART_ISS=https://your-fhir-base-url
VITE_SMART_REDIRECT_URI=http://localhost:5173/launch
```

## Routes

Primary workflows:
- `/` Overview
- `/command-center`
- `/patient-workspace`
- `/quality-evaluation`
- `/rollout-monitoring`
- `/feedback-review`

Control plane:
- `/release-gate`
- `/audit-explorer`
- `/incidents`
- `/launch`

Labs (series continuity):
- `/post-1` ... `/post-8`

Future placeholders:
- `/future`
- `/governance`
- `/platform-admin`
- `/platform`

## SMART + iFrame

- Use `/launch?embed=1` for iframe-friendly mode.
- SMART launch params: `iss`, `launch`
- Callback params: `code`, `state`

See `ui/docs/SMART_ON_FHIR.md` for hardening and deployment notes.

## E2E Tests

```bash
npm run e2e
```

Playwright tests are in `ui/e2e` and mock API routes for deterministic checks.

## Container Deployment

```bash
# from repository root
docker compose up -d --build
```

- UI: `http://localhost:3000`
- API: `http://localhost:8000`
