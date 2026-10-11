"use client";

import Link from "next/link";
import {
  DashboardError,
  DashboardFrame,
  DashboardLoading,
  DashboardPanel,
  EmptyState,
  StatCard,
} from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import {
  aptitudeHistory,
  aptitudeSessionConfig,
  candidateDashboard,
  type AptitudeHistoryItem,
  type CandidateDashboard,
  type AptitudeSessionConfig,
} from "@/lib/auth";

async function loadDashboardData() {
  const [dashboard, history, config] = await Promise.all([
    candidateDashboard(),
    aptitudeHistory(),
    aptitudeSessionConfig(),
  ]);
  return { dashboard, history, config };
}

function formatDate(seconds: number): string {
  return new Date(seconds * 1000).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDuration(seconds: number): string {
  const minutes = Math.ceil(seconds / 60);
  return `${minutes} min`;
}

function PracticePath() {
  const rounds = [
    { number: "01", title: "Aptitude & reasoning", label: "Available now", current: true },
    { number: "02", title: "Technical concepts", label: "Coming soon", current: false },
    { number: "03", title: "Coding challenge", label: "Coming soon", current: false },
    { number: "04", title: "Behavioral interview", label: "Coming soon", current: false },
  ];

  return (
    <ol className="mt-5 grid gap-3 sm:grid-cols-2">
      {rounds.map((round) => (
        <li
          className={`flex items-center gap-3 rounded-xl border p-3.5 ${
            round.current
              ? "border-indigo-100 bg-indigo-50/70"
              : "border-slate-100 bg-slate-50/70"
          }`}
          key={round.number}
        >
          <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl text-xs font-bold ${
            round.current ? "bg-indigo-600 text-white" : "bg-white text-slate-400 ring-1 ring-slate-200"
          }`}>
            {round.number}
          </span>
          <div className="min-w-0">
            <p className={`truncate text-xs font-bold ${round.current ? "text-indigo-950" : "text-slate-600"}`}>
              {round.title}
            </p>
            <p className={`mt-1 text-[10px] font-semibold ${round.current ? "text-indigo-600" : "text-slate-400"}`}>
              {round.label}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}

export default function CandidateDashboardPage() {
  const { data, error, loading } = useRoleResource<{
    dashboard: CandidateDashboard;
    history: AptitudeHistoryItem[];
    config: AptitudeSessionConfig;
  }>("CANDIDATE", loadDashboardData);

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load your dashboard."} />;

  const { dashboard, history, config } = data;
  const completed = history.filter((item) => item.status === "COMPLETED");
  const averageAccuracy = completed.length
    ? Math.round(completed.reduce((sum, item) => sum + (item.accuracy ?? 0), 0) / completed.length)
    : null;
  const activeSession = history.find((item) => item.status === "IN_PROGRESS");
  const recentHistory = history.slice(0, 4);
  const firstName = dashboard.user.name.trim().split(/\s+/)[0] || dashboard.user.name;

  return (
    <DashboardFrame role="CANDIDATE" user={dashboard.user}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.19em] text-indigo-600">Your candidate workspace</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-950 sm:text-[30px]">
            Welcome back, {firstName}
          </h1>
          <p className="mt-1.5 text-sm text-slate-500">A little practice today can make a big difference tomorrow.</p>
        </div>
        <div className="rounded-full border border-slate-200 bg-white px-3.5 py-2 text-[11px] font-semibold text-slate-600">
          Target role <span className="ml-1 text-slate-900">{dashboard.profile.targetRole || "Not set"}</span>
        </div>
      </div>

      <section className="relative mt-7 overflow-hidden rounded-[26px] bg-[#171b3b] p-6 text-white shadow-[0_18px_48px_rgba(27,31,72,0.18)] sm:p-9">
        <div aria-hidden="true" className="pointer-events-none absolute -right-12 -top-32 h-80 w-80 rounded-full border border-white/10" />
        <div aria-hidden="true" className="pointer-events-none absolute -right-1 -top-20 h-64 w-64 rounded-full border border-white/10" />
        <div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-center">
          <div className="max-w-2xl">
            <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.16em] text-indigo-100">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
              Your interview prep starts here
            </span>
            <h2 className="mt-5 max-w-xl text-[26px] font-bold leading-tight tracking-tight sm:text-[34px]">
              Turn your preparation into confidence.
            </h2>
            <p className="mt-3 max-w-lg text-sm leading-6 text-indigo-100/75">
              Start with a focused placement-style aptitude round, then use your results to decide what to practice next.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-3 text-xs font-bold text-indigo-950 shadow-sm transition hover:bg-indigo-50"
                href={activeSession
                  ? `/candidate/practice/aptitude/test?sessionId=${encodeURIComponent(activeSession.sessionId)}`
                  : "/candidate/practice"}
              >
                {activeSession ? "Continue your test" : "Start practicing"}
                <span aria-hidden="true">→</span>
              </Link>
              <Link className="rounded-xl border border-white/20 px-4 py-3 text-xs font-semibold text-white/90 transition hover:bg-white/10" href="/candidate/practice">
                Explore practice
              </Link>
            </div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.07] p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-indigo-100/65">Round 1</p>
                <p className="mt-1 text-sm font-bold">Aptitude &amp; reasoning</p>
              </div>
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-400/20 text-lg">✦</span>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-2.5">
              {[[String(config.questionCount), "questions"], [formatDuration(config.estimatedDurationSeconds), "assessment"]].map(([value, label]) => (
                <div className="rounded-xl bg-black/15 px-3 py-3" key={label}>
                  <p className="text-base font-bold">{value}</p>
                  <p className="mt-1 text-[10px] text-indigo-100/65">{label}</p>
                </div>
              ))}
            </div>
            <p className="mt-4 flex items-center gap-2 text-[10px] font-medium text-indigo-100/70">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
              Your progress is saved as you go
            </p>
          </div>
        </div>
      </section>

      <section aria-label="Practice statistics" className="mt-5 grid gap-3 sm:grid-cols-3">
        <StatCard label="Completed practice tests" value={completed.length} detail="Aptitude sessions finished" />
        <StatCard label="Average accuracy" value={averageAccuracy === null ? "—" : `${averageAccuracy}%`} detail={completed.length ? "Across completed aptitude tests" : "Your score will appear after a test"} />
        <StatCard label="Practice status" value={activeSession ? "In progress" : "Ready"} detail={activeSession ? "Pick up where you left off" : "Your first round is ready"} />
      </section>

      <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(300px,0.85fr)]">
        <DashboardPanel title="Your interview preparation path" description="A clear path from practice to interview readiness.">
          <PracticePath />
        </DashboardPanel>
        <DashboardPanel title="Your focus" description="Personalize practice to your goals.">
          <div className="rounded-xl border border-slate-100 bg-slate-50/80 p-4">
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">Target role</p>
            <p className="mt-2 text-sm font-bold text-slate-900">{dashboard.profile.targetRole || "Choose a role to get started"}</p>
            <p className="mt-1.5 text-xs leading-5 text-slate-500">
              We use your selected role to tailor the aptitude practice experience.
            </p>
          </div>
          <Link className="mt-4 inline-flex items-center gap-2 text-xs font-bold text-indigo-700 hover:text-indigo-900" href="/candidate/practice">
            Set up a practice session <span aria-hidden="true">→</span>
          </Link>
        </DashboardPanel>
      </div>

      <div className="mt-5">
        <DashboardPanel title="Recent practice" description="Pick up an unfinished test or review a completed result.">
          {recentHistory.length ? (
            <ul className="divide-y divide-slate-100">
              {recentHistory.map((item) => (
                <li className="flex flex-wrap items-center justify-between gap-3 py-3 first:pt-0 last:pb-0" key={item.sessionId}>
                  <div className="flex min-w-0 items-center gap-3">
                    <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl text-xs font-bold ${
                      item.status === "COMPLETED" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                    }`}>
                      {item.status === "COMPLETED" ? "✓" : "…"}
                    </span>
                    <div className="min-w-0">
                      <p className="truncate text-xs font-bold text-slate-800">{item.targetRole} · Aptitude</p>
                      <p className="mt-1 text-[10px] text-slate-500">{formatDate(item.startedAt)} · {item.totalQuestions} questions</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <p className="text-xs font-bold text-slate-700">
                      {item.status === "COMPLETED" ? `${item.accuracy ?? 0}% accuracy` : "In progress"}
                    </p>
                    <Link
                      className="rounded-lg border border-slate-200 px-3 py-2 text-[10px] font-bold text-slate-700 transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
                      href={item.status === "IN_PROGRESS"
                        ? `/candidate/practice/aptitude/test?sessionId=${encodeURIComponent(item.sessionId)}`
                        : `/candidate/practice/aptitude/result?sessionId=${encodeURIComponent(item.sessionId)}`}
                    >
                      {item.status === "IN_PROGRESS" ? "Resume" : "Review result"}
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState>Your practice history will appear here after your first aptitude session.</EmptyState>
          )}
          <Link
            className="mt-4 inline-flex text-xs font-bold text-indigo-700 hover:text-indigo-900"
            href="/candidate/practice/history"
          >
            View full practice history <span className="ml-1" aria-hidden="true">→</span>
          </Link>
        </DashboardPanel>
      </div>
    </DashboardFrame>
  );
}
