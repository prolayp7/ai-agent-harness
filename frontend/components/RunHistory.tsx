"use client";

import type { RunSummary } from "@/lib/api";

interface RunHistoryProps {
  runs: RunSummary[];
  activeRunId: string | null;
  loadingRunId: string | null;
  error: string | null;
  onSelect: (runId: string) => void;
  onRefresh: () => void;
  refreshing: boolean;
}

const statusLabels: Record<RunSummary["status"], string> = {
  completed: "Completed",
  max_steps_reached: "Step limit",
  waiting_approval: "Needs approval",
  error: "Error",
  rejected: "Rejected",
};

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date unavailable";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function RunHistory({
  runs,
  activeRunId,
  loadingRunId,
  error,
  onSelect,
  onRefresh,
  refreshing,
}: RunHistoryProps) {
  return (
    <section
      aria-labelledby="history-heading"
      className="rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-900/[0.04]"
    >
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
        <div>
          <h2 id="history-heading" className="text-base font-semibold text-slate-900">
            Recent runs
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Select a run to review its details.
          </p>
        </div>
        <button
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
          aria-label="Refresh run history"
          className="inline-flex min-h-9 items-center justify-center rounded-lg border border-slate-300 px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-60"
        >
          {refreshing ? "Loading" : "Refresh"}
        </button>
      </div>

      {error && (
        <p role="alert" className="px-5 py-4 text-sm text-red-700">
          {error}
        </p>
      )}

      {!error && runs.length === 0 && (
        <div className="px-5 py-10 text-center">
          <p className="text-sm font-medium text-slate-700">No runs yet</p>
          <p className="mt-1 text-sm text-slate-500">
            Your recent agent runs will appear here.
          </p>
        </div>
      )}

      {runs.length > 0 && (
        <ul className="max-h-[34rem] divide-y divide-slate-100 overflow-y-auto">
          {runs.map((run) => {
            const selected = run.id === activeRunId;
            return (
              <li key={run.id}>
                <button
                  type="button"
                  onClick={() => onSelect(run.id)}
                  disabled={loadingRunId === run.id}
                  aria-current={selected ? "true" : undefined}
                  className={`block w-full px-5 py-4 text-left transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-600 disabled:cursor-wait ${
                    selected ? "bg-blue-50/70" : "bg-white"
                  }`}
                >
                  <span className="flex items-start justify-between gap-3">
                    <span className="line-clamp-2 text-sm font-medium leading-5 text-slate-900">
                      {run.goal}
                    </span>
                    <span className="shrink-0 rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600">
                      {loadingRunId === run.id
                        ? "Loading"
                        : statusLabels[run.status]}
                    </span>
                  </span>
                  <span className="mt-2 block text-xs text-slate-500">
                    {formatDate(run.created_at)}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
