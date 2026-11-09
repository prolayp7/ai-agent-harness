"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import ApprovalBanner from "@/components/ApprovalBanner";
import RunHistory from "@/components/RunHistory";
import StepCard from "@/components/StepCard";
import {
  ApiError,
  approveRun,
  getRecentRuns,
  getRun,
  runAgent,
  type AgentRun,
  type RunStatus,
  type RunSummary,
} from "@/lib/api";

const statusStyles: Record<RunStatus, string> = {
  completed: "bg-emerald-50 text-emerald-800 ring-emerald-700/15",
  max_steps_reached: "bg-amber-50 text-amber-900 ring-amber-700/20",
  waiting_approval: "bg-blue-50 text-blue-800 ring-blue-700/15",
  error: "bg-red-50 text-red-800 ring-red-700/15",
  rejected: "bg-slate-100 text-slate-700 ring-slate-500/15",
};

const statusLabels: Record<RunStatus, string> = {
  completed: "Completed",
  max_steps_reached: "Step limit reached",
  waiting_approval: "Waiting for approval",
  error: "Error",
  rejected: "Rejected",
};

function getErrorMessage(error: unknown) {
  return error instanceof ApiError
    ? error.message
    : "Something went wrong. Please try again.";
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value || "Date unavailable";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function AgentRunner() {
  const [goal, setGoal] = useState("");
  const [maxSteps, setMaxSteps] = useState(8);
  const [requireApproval, setRequireApproval] = useState(false);
  const [run, setRun] = useState<AgentRun | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [approvalBusy, setApprovalBusy] = useState(false);
  const [loadingRunId, setLoadingRunId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const refreshHistory = useCallback(async () => {
    setRefreshing(true);
    setHistoryError(null);
    try {
      setRuns(await getRecentRuns());
    } catch (requestError) {
      setHistoryError(getErrorMessage(requestError));
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let active = true;

    getRecentRuns()
      .then((recentRuns) => {
        if (active) setRuns(recentRuns);
      })
      .catch((requestError: unknown) => {
        if (active) setHistoryError(getErrorMessage(requestError));
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedGoal = goal.trim();
    if (!trimmedGoal) {
      setError("Enter a goal before running the agent.");
      return;
    }

    setLoading(true);
    setError(null);
    setRun(null);
    try {
      const result = await runAgent({
        goal: trimmedGoal,
        max_steps: maxSteps,
        require_approval: requireApproval,
      });
      setRun(result);
      await refreshHistory();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  async function handleApproval(approved: boolean, feedback?: string) {
    if (!run) return;

    setApprovalBusy(true);
    setError(null);
    try {
      const result = await approveRun(run.run_id, approved, feedback);
      setRun((current) =>
        current
          ? {
              ...current,
              status: result.status,
              final_answer: result.final_answer,
            }
          : current,
      );
      await refreshHistory();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setApprovalBusy(false);
    }
  }

  async function handleSelectRun(runId: string) {
    setLoadingRunId(runId);
    setError(null);
    try {
      setRun(await getRun(runId));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoadingRunId(null);
    }
  }

  return (
    <div className="min-h-dvh bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link
            href="/"
            className="text-sm font-semibold tracking-tight text-slate-950 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-4"
          >
            Agent Harness
          </Link>
          <span className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600">
            Internal workspace
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <div className="mb-8 max-w-3xl">
          <p className="text-sm font-semibold text-blue-700">Agent control</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
            Run and inspect an agent
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
            Submit a goal, review the agent&apos;s work, and approve runs that
            need human oversight.
          </p>
        </div>

        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1.65fr)_minmax(19rem,0.85fr)]">
          <div className="min-w-0 space-y-6">
            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/[0.04] sm:p-6">
              <div className="mb-5">
                <h2 className="text-lg font-semibold text-slate-950">
                  Start a run
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Describe the task clearly. You can inspect each step after the
                  run completes.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label
                    htmlFor="goal"
                    className="mb-2 block text-sm font-medium text-slate-800"
                  >
                    Goal
                  </label>
                  <textarea
                    id="goal"
                    value={goal}
                    onChange={(event) => setGoal(event.target.value)}
                    rows={5}
                    maxLength={4000}
                    required
                    placeholder="For example: Compare the latest release notes for two libraries and summarize the main differences."
                    className="block w-full resize-y rounded-xl border border-slate-300 bg-white px-3.5 py-3 text-sm leading-6 text-slate-900 placeholder:text-slate-500 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20"
                  />
                </div>

                <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
                  <div className="max-w-48">
                    <label
                      htmlFor="max-steps"
                      className="mb-2 block text-sm font-medium text-slate-800"
                    >
                      Maximum steps
                    </label>
                    <input
                      id="max-steps"
                      type="number"
                      min={1}
                      max={30}
                      value={maxSteps}
                      onChange={(event) => {
                        const value = Number(event.target.value);
                        if (Number.isInteger(value) && value >= 1 && value <= 30) {
                          setMaxSteps(value);
                        }
                      }}
                      className="block h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20"
                    />
                    <p className="mt-1.5 text-xs text-slate-500">
                      Choose a value from 1 to 30.
                    </p>
                  </div>

                  <label className="flex min-h-11 cursor-pointer items-center gap-2.5 rounded-lg sm:pb-5">
                    <input
                      type="checkbox"
                      checked={requireApproval}
                      onChange={(event) => setRequireApproval(event.target.checked)}
                      className="size-4 rounded border-slate-300 text-blue-700 focus:ring-2 focus:ring-blue-600/30"
                    />
                    <span className="text-sm font-medium text-slate-700">
                      Require human approval
                    </span>
                  </label>
                </div>

                {error && (
                  <p
                    role="alert"
                    className="rounded-lg border border-red-200 bg-red-50 px-3.5 py-3 text-sm leading-5 text-red-800"
                  >
                    {error}
                  </p>
                )}

                <button
                  type="submit"
                  disabled={loading || !goal.trim()}
                  className="inline-flex min-h-11 w-full items-center justify-center rounded-lg bg-blue-700 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-800 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-700 focus-visible:ring-offset-2 disabled:cursor-wait disabled:bg-blue-400 sm:w-auto"
                >
                  {loading ? "Running agent..." : "Run Agent"}
                </button>
              </form>
            </section>

            {loading && (
              <section
                aria-label="Agent is running"
                aria-live="polite"
                className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
              >
                <div className="h-5 w-40 animate-pulse rounded bg-slate-200" />
                <div className="mt-4 h-20 animate-pulse rounded-xl bg-slate-100" />
                <p className="mt-4 text-sm text-slate-600">
                  The agent is working. This may take a little while.
                </p>
              </section>
            )}

            {run && !loading && (
              <section aria-labelledby="run-result-heading" className="space-y-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2
                      id="run-result-heading"
                      className="text-xl font-semibold tracking-tight text-slate-950"
                    >
                      Run result
                    </h2>
                    <p className="mt-1 text-xs text-slate-500">
                      Run ID: <span className="font-mono">{run.run_id}</span>
                    </p>
                  </div>
                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1.5 text-xs font-semibold ring-1 ring-inset ${statusStyles[run.status]}`}
                  >
                    {statusLabels[run.status]}
                  </span>
                </div>

                {run.status === "waiting_approval" && (
                  <ApprovalBanner
                    busy={approvalBusy}
                    onDecision={handleApproval}
                  />
                )}

                {run.final_answer && (
                  <section
                    aria-labelledby="final-answer-heading"
                    className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 sm:p-6"
                  >
                    <h3
                      id="final-answer-heading"
                      className="text-xs font-semibold uppercase tracking-wide text-emerald-900"
                    >
                      Final answer
                    </h3>
                    <p className="mt-2 whitespace-pre-wrap break-words text-base leading-7 text-emerald-950">
                      {run.final_answer}
                    </p>
                  </section>
                )}

                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="text-base font-semibold text-slate-900">
                    Execution steps
                  </h3>
                  <time
                    dateTime={run.created_at}
                    className="text-xs text-slate-500"
                  >
                    {formatDate(run.created_at)}
                  </time>
                </div>

                {run.steps.length > 0 ? (
                  <div className="space-y-3">
                    {run.steps.map((step) => (
                      <StepCard key={step.step_number} step={step} />
                    ))}
                  </div>
                ) : (
                  <p className="rounded-xl border border-slate-200 bg-white px-4 py-5 text-sm text-slate-600">
                    This run has no recorded steps.
                  </p>
                )}
              </section>
            )}
          </div>

          <RunHistory
            runs={runs}
            activeRunId={run?.run_id ?? null}
            loadingRunId={loadingRunId}
            error={historyError}
            onSelect={(runId) => void handleSelectRun(runId)}
            onRefresh={() => void refreshHistory()}
            refreshing={refreshing}
          />
        </div>
      </main>
    </div>
  );
}
