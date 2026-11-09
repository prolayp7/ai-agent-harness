import type { AgentStep } from "@/lib/api";

interface StepCardProps {
  step: AgentStep;
}

function formatArgs(args: Record<string, unknown>) {
  return JSON.stringify(args, null, 2);
}

export default function StepCard({ step }: StepCardProps) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/[0.03]">
      <header className="mb-4 flex items-center justify-between gap-4">
        <h3 className="text-sm font-semibold text-slate-900">
          Step {step.step_number}
        </h3>
        {step.is_final && (
          <span className="rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-800">
            Final step
          </span>
        )}
      </header>

      <dl className="space-y-4">
        <div>
          <dt className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Thought
          </dt>
          <dd className="whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">
            {step.thought || "No thought provided."}
          </dd>
        </div>

        {step.action && (
          <div>
            <dt className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
              Action
            </dt>
            <dd className="overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
              <div className="border-b border-slate-200 px-3 py-2 font-mono text-xs font-semibold text-slate-800">
                {step.action.tool}
              </div>
              <pre className="overflow-x-auto whitespace-pre-wrap break-all px-3 py-2.5 font-mono text-xs leading-5 text-slate-600">
                {formatArgs(step.action.args)}
              </pre>
            </dd>
          </div>
        )}

        {step.observation !== null && (
          <div>
            <dt className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
              Observation
            </dt>
            <dd className="whitespace-pre-wrap break-words rounded-lg bg-slate-50 px-3 py-2.5 text-sm leading-6 text-slate-700">
              {step.observation}
            </dd>
          </div>
        )}
      </dl>
    </article>
  );
}
