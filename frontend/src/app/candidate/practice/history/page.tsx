"use client";

import Link from "next/link";
import {
  DashboardError,
  DashboardFrame,
  DashboardLoading,
  DashboardPanel,
  EmptyState,
} from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import {
  aptitudeHistory,
  candidateDashboard,
  type AptitudeHistoryItem,
} from "@/lib/auth";

async function loadHistoryPage() {
  const [dashboard, history] = await Promise.all([candidateDashboard(), aptitudeHistory()]);
  return { user: dashboard.user, history };
}

function formatDate(seconds: number): string {
  return new Date(seconds * 1000).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function CandidatePracticeHistoryPage() {
  const { data, error, loading } = useRoleResource<{
    user: Awaited<ReturnType<typeof candidateDashboard>>["user"];
    history: AptitudeHistoryItem[];
  }>("CANDIDATE", loadHistoryPage);

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load practice history."} />;

  return (
    <DashboardFrame role="CANDIDATE" user={data.user}>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">Candidate workspace</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">Practice history</h1>
          <p className="mt-2 text-sm text-slate-600">Resume unfinished attempts or revisit your completed results.</p>
        </div>
        <Link
          className="rounded-lg bg-indigo-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-800"
          href="/candidate/practice"
        >
          Start a practice test
        </Link>
      </div>
      <div className="mt-7">
        <DashboardPanel title="Aptitude & reasoning sessions">
          {data.history.length ? (
            <ul className="divide-y divide-slate-100">
              {data.history.map((item) => (
                <li className="flex flex-wrap items-center justify-between gap-4 py-4 first:pt-0 last:pb-0" key={item.sessionId}>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{item.targetRole} · Aptitude &amp; reasoning</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {formatDate(item.startedAt)} · {item.totalQuestions} questions
                      {item.accuracy === null ? "" : ` · ${item.accuracy}% accuracy`}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ${
                      item.status === "IN_PROGRESS"
                        ? "bg-amber-50 text-amber-800"
                        : "bg-emerald-50 text-emerald-800"
                    }`}>
                      {item.status === "IN_PROGRESS" ? "In progress" : "Completed"}
                    </span>
                    <Link
                      className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
                      href={item.status === "IN_PROGRESS"
                        ? `/candidate/practice/aptitude/test?sessionId=${encodeURIComponent(item.sessionId)}`
                        : `/candidate/practice/aptitude/result?sessionId=${encodeURIComponent(item.sessionId)}`}
                    >
                      {item.status === "IN_PROGRESS" ? "Resume test" : "View result"}
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState>Your practice history is empty. Start an aptitude session to see your progress here.</EmptyState>
          )}
        </DashboardPanel>
      </div>
      <div className="mt-5 flex flex-wrap gap-3">
        <Link className="text-sm font-semibold text-indigo-700 hover:text-indigo-900" href="/candidate/dashboard">
          ← Candidate dashboard
        </Link>
        <Link className="text-sm font-semibold text-slate-600 hover:text-slate-900" href="/candidate/practice">
          Practice setup
        </Link>
      </div>
    </DashboardFrame>
  );
}
