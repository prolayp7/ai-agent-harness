export type RunStatus =
  | "completed"
  | "max_steps_reached"
  | "waiting_approval"
  | "error"
  | "rejected";

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
}

export interface AgentStep {
  step_number: number;
  thought: string;
  action: ToolCall | null;
  observation: string | null;
  is_final: boolean;
}

export interface AgentRun {
  run_id: string;
  goal: string;
  steps: AgentStep[];
  final_answer: string | null;
  status: RunStatus;
  created_at: string;
}

export interface RunSummary {
  id: string;
  goal: string;
  status: RunStatus;
  final_answer: string | null;
  created_at: string;
}

export interface RunAgentInput {
  goal: string;
  max_steps?: number;
  require_approval?: boolean;
}

export interface ApprovalResult {
  run_id: string;
  status: RunStatus;
  final_answer: string | null;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      `Could not connect to the API at ${API_BASE_URL}. Check that the backend is running and allows requests from this frontend.`,
    );
  }

  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const message =
      typeof body === "object" && body !== null && "detail" in body
        ? String(body.detail)
        : `The API request failed with status ${response.status}.`;
    throw new ApiError(message, response.status);
  }

  return body as T;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function normalizeStatus(value: unknown): RunStatus {
  switch (value) {
    case "completed":
    case "max_steps_reached":
    case "waiting_approval":
    case "error":
    case "rejected":
      return value;
    default:
      return "error";
  }
}

function normalizeStep(value: unknown): AgentStep {
  const step = isRecord(value) ? value : {};
  const actionValue = step.action;
  let action: ToolCall | null = null;

  if (isRecord(actionValue)) {
    action = {
      tool: String(actionValue.tool ?? "Unknown tool"),
      args: isRecord(actionValue.args) ? actionValue.args : {},
    };
  } else if (typeof step.action_tool === "string") {
    action = {
      tool: step.action_tool,
      args: isRecord(step.action_args) ? step.action_args : {},
    };
  }

  return {
    step_number: Number(step.step_number ?? 0),
    thought: String(step.thought ?? ""),
    action,
    observation:
      typeof step.observation === "string" ? step.observation : null,
    is_final: Boolean(step.is_final),
  };
}

function normalizeRun(value: unknown): AgentRun {
  if (!isRecord(value)) {
    throw new ApiError("The API returned an invalid run response.");
  }

  return {
    run_id: String(value.run_id ?? value.id ?? ""),
    goal: String(value.goal ?? ""),
    steps: Array.isArray(value.steps) ? value.steps.map(normalizeStep) : [],
    final_answer:
      typeof value.final_answer === "string" ? value.final_answer : null,
    status: normalizeStatus(value.status),
    created_at: String(value.created_at ?? ""),
  };
}

export async function runAgent(input: RunAgentInput): Promise<AgentRun> {
  const result = await request<unknown>("/agent/run", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return normalizeRun(result);
}

export async function approveRun(
  runId: string,
  approved: boolean,
  feedback?: string,
): Promise<ApprovalResult> {
  const result = await request<unknown>("/agent/approve", {
    method: "POST",
    body: JSON.stringify({
      run_id: runId,
      approved,
      ...(feedback?.trim() ? { feedback: feedback.trim() } : {}),
    }),
  });

  if (!isRecord(result)) {
    throw new ApiError("The API returned an invalid approval response.");
  }

  return {
    run_id: String(result.run_id ?? runId),
    status: normalizeStatus(result.status),
    final_answer:
      typeof result.final_answer === "string" ? result.final_answer : null,
  };
}

export async function getRecentRuns(): Promise<RunSummary[]> {
  const result = await request<unknown>("/agent/runs");
  if (!Array.isArray(result)) {
    throw new ApiError("The API returned an invalid run history.");
  }

  return result.map((value) => {
    const run = isRecord(value) ? value : {};
    return {
      id: String(run.id ?? run.run_id ?? ""),
      goal: String(run.goal ?? ""),
      status: normalizeStatus(run.status),
      final_answer:
        typeof run.final_answer === "string" ? run.final_answer : null,
      created_at: String(run.created_at ?? ""),
    };
  });
}

export async function getRun(runId: string): Promise<AgentRun> {
  const result = await request<unknown>(
    `/agent/runs/${encodeURIComponent(runId)}`,
  );
  return normalizeRun(result);
}
