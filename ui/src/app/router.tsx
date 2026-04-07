import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "../layouts/AppShell";
import { OverviewPage } from "../pages/OverviewPage";
import { CommandCenterPage } from "../pages/CommandCenterPage";
import { PatientWorkspacePage } from "../pages/PatientWorkspacePage";
import { QualityEvaluationPage } from "../pages/QualityEvaluationPage";
import { RolloutMonitoringPage } from "../pages/RolloutMonitoringPage";
import { FeedbackReviewPage } from "../pages/FeedbackReviewPage";
import { ReleaseGatePage } from "../pages/ReleaseGatePage";
import { AuditExplorerPage } from "../pages/AuditExplorerPage";
import { IncidentWorkspacePage } from "../pages/IncidentWorkspacePage";
import { Post1FoundationPage } from "../pages/Post1FoundationPage";
import { Post2LLMPage } from "../pages/Post2LLMPage";
import { Post3PromptPage } from "../pages/Post3PromptPage";
import { Post4VariabilityPage } from "../pages/Post4VariabilityPage";
import { Post5EvaluationPage } from "../pages/Post5EvaluationPage";
import { Post6ShadowPage } from "../pages/Post6ShadowPage";
import { Post7MonitoringPage } from "../pages/Post7MonitoringPage";
import { Post8FeedbackPage } from "../pages/Post8FeedbackPage";
import { FuturePostsPage } from "../pages/FuturePostsPage";
import { PlatformVisionPage } from "../pages/PlatformVisionPage";
import { GovernancePage } from "../pages/GovernancePage";
import { PlatformAdminPage } from "../pages/PlatformAdminPage";
import { SmartLaunchPage } from "../pages/SmartLaunchPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: "command-center", element: <CommandCenterPage /> },
      { path: "patient-workspace", element: <PatientWorkspacePage /> },
      { path: "quality-evaluation", element: <QualityEvaluationPage /> },
      { path: "rollout-monitoring", element: <RolloutMonitoringPage /> },
      { path: "feedback-review", element: <FeedbackReviewPage /> },
      { path: "release-gate", element: <ReleaseGatePage /> },
      { path: "audit-explorer", element: <AuditExplorerPage /> },
      { path: "incidents", element: <IncidentWorkspacePage /> },
      { path: "post-1", element: <Post1FoundationPage /> },
      { path: "post-2", element: <Post2LLMPage /> },
      { path: "post-3", element: <Post3PromptPage /> },
      { path: "post-4", element: <Post4VariabilityPage /> },
      { path: "post-5", element: <Post5EvaluationPage /> },
      { path: "post-6", element: <Post6ShadowPage /> },
      { path: "post-7", element: <Post7MonitoringPage /> },
      { path: "post-8", element: <Post8FeedbackPage /> },
      { path: "future", element: <FuturePostsPage /> },
      { path: "platform", element: <PlatformVisionPage /> },
      { path: "governance", element: <GovernancePage /> },
      { path: "platform-admin", element: <PlatformAdminPage /> },
      { path: "launch", element: <SmartLaunchPage /> }
    ]
  }
]);
