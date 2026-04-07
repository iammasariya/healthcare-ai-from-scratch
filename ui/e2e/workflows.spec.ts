import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/api/health", async (route) => {
    await route.fulfill({ json: { status: "healthy", timestamp: new Date().toISOString(), version: "0.8.0" } });
  });

  await page.route("**/api/monitoring/status", async (route) => {
    await route.fulfill({
      json: {
        monitoring_enabled: true,
        actions: [
          { action: "pause_shadow_mode", active: false },
          { action: "freeze_candidate_rollout", active: false }
        ],
        snapshot: {
          total_runs: 10,
          divergence_rate: 0.1,
          critical_alert_rate: 0.0,
          avg_shadow_latency_ms: 900,
          avg_shadow_cost_usd: 0.004
        }
      }
    });
  });

  await page.route("**/api/feedback/analytics?window_days=7", async (route) => {
    await route.fulfill({
      json: {
        window_days: 7,
        issued_response_count: 40,
        feedback_event_count: 8,
        feedback_coverage_rate: 0.2,
        positive_feedback_count: 6,
        negative_feedback_count: 2,
        negative_feedback_rate: 0.25,
        category_breakdown: { clinical_accuracy: 2 },
        avg_seconds_to_submit: 11,
        high_priority_queue_count: 1
      }
    });
  });

  await page.route("**/api/incidents", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ json: [] });
      return;
    }

    await route.fulfill({
      json: {
        incident_id: "11111111-1111-1111-1111-111111111111",
        title: "Manual incident",
        status: "open",
        severity: "warning",
        source: "operator",
        summary: "created from e2e",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    });
  });

  await page.route("**/api/incidents/sync-monitoring", async (route) => {
    await route.fulfill({ json: [] });
  });

  await page.route("**/api/audits/search**", async (route) => {
    await route.fulfill({ json: [] });
  });
});

test("loads command center with core operational cards", async ({ page }) => {
  await page.goto("/command-center");
  await expect(page.getByRole("heading", { name: "Command Center" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Release Gate" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Incident Workspace" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Audit Explorer" })).toBeVisible();
});

test("release gate executes and renders decision", async ({ page }) => {
  await page.goto("/release-gate");
  await page.getByRole("button", { name: "Run Gate Checks" }).click();
  await expect(page.locator(".badge.ok", { hasText: "GO" })).toBeVisible();
});

test("embed mode hides left navigation chrome", async ({ page }) => {
  await page.goto("/launch?embed=1");
  await expect(page.locator(".sidebar")).toHaveCount(0);
  await expect(page.getByText("Embed Mode")).toBeVisible();
});
