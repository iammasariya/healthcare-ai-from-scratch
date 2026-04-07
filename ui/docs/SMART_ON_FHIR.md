# SMART on FHIR + EHR Embed Guide

This UI supports SMART launch and iframe embedding for EHR-integrated deployments.

## Launch Route

Use:

- `https://your-ui-domain/launch?embed=1`

Expected SMART params:

- `iss` - FHIR base URL
- `launch` - launch context token

OAuth callback params (automatically handled by `fhirclient`):

- `code`
- `state`

## Required Frontend Config

```bash
VITE_AUTH_MODE=smart
VITE_SMART_CLIENT_ID=your-smart-client-id
VITE_SMART_ISS=https://your-fhir-base-url
VITE_SMART_REDIRECT_URI=https://your-ui-domain/launch
```

## Runtime Behavior

- `src/smart/auth.ts`
  - Preserves `embed=1` across SMART redirect
  - Passes `launch` token to SMART authorize call when present
- `src/pages/SmartLaunchPage.tsx`
  - Auto-switches to SMART mode on launch/callback params
  - Supports explicit context hydration after callback
- `src/layouts/AppShell.tsx`
  - `embed=1` hides sidebar chrome for iframe-friendly operator experience

## Container CSP / Frame-Ancestors

The UI container uses nginx template variables:

- `API_UPSTREAM` (default `http://api:8000`)
- `FRAME_ANCESTORS` (default `'self'`)

Example for trusted embed origins:

```bash
FRAME_ANCESTORS='self' https://ehr.example.org https://*.epic.com
```

Set this in deployment config (`docker-compose`, Helm values, or Kubernetes env).

## Production Hardening Checklist

1. Restrict `FRAME_ANCESTORS` to explicit trusted EHR origins.
2. Validate trusted `iss` servers in your gateway/backend policy.
3. Use HTTPS for UI, API, and FHIR endpoints.
4. Avoid persisting PHI in browser storage.
5. Add organization-level RBAC for operator routes.
