"use client";

import { useState } from "react";

interface ApprovalBannerProps {
  busy: boolean;
  onDecision: (approved: boolean, feedback?: string) => Promise<void>;
}

export default function ApprovalBanner({
  busy,
  onDecision,
}: ApprovalBannerProps) {
  const [feedback, setFeedback] = useState("");

  return (
    <section
      aria-labelledby="approval-title"
      className="rounded-xl border border-amber-300 bg-amber-50 p-5"
    >
      <div className="max-w-2xl">
        <h2 id="approval-title" className="text-base font-semibold text-amber-950">
          Human approval required
        </h2>
        <p className="mt-1 text-sm leading-6 text-amber-900">
          Review the result and steps before deciding whether this run should
          be approved.
        </p>
      </div>

      <label
        htmlFor="approval-feedback"
        className="mt-4 block text-sm font-medium text-amber-950"
      >
        Feedback <span className="font-normal text-amber-800">(optional)</span>
      </label>
      <textarea
        id="approval-feedback"
        value={feedback}
        onChange={(event) => setFeedback(event.target.value)}
        rows={2}
        disabled={busy}
        placeholder="Add a note if you reject this run"
        className="mt-2 block w-full resize-y rounded-lg border border-amber-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-500 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20 disabled:cursor-not-allowed disabled:opacity-60"
      />

      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          disabled={busy}
          onClick={() => void onDecision(true)}
          className="inline-flex min-h-10 items-center justify-center rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-800 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-700 focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-60"
        >
          {busy ? "Submitting..." : "Approve"}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => void onDecision(false, feedback)}
          className="inline-flex min-h-10 items-center justify-center rounded-lg border border-amber-400 bg-white px-4 py-2 text-sm font-semibold text-amber-950 transition hover:bg-amber-100 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-700 focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-60"
        >
          Reject
        </button>
      </div>
    </section>
  );
}
