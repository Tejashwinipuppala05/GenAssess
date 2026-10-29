"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { DashboardError, DashboardFrame, DashboardLoading, DashboardPanel, EmptyState } from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import {
  aptitudeHistory,
  aptitudeSessionConfig,
  candidateDashboard,
  type AptitudeHistoryItem,
  type AptitudeSessionConfig,
} from "@/lib/auth";

async function loadPracticeData() {
  const [dashboard, history, config] = await Promise.all([
    candidateDashboard(),
    aptitudeHistory(),
    aptitudeSessionConfig(),
  ]);
  return { user: dashboard.user, history, config };
}

function formatDuration(seconds: number): string {
  const minutes = Math.ceil(seconds / 60);
  return `${minutes} min`;
}

export default function CandidatePracticePage() {
  const router = useRouter();
  const { data, error, loading } = useRoleResource<{
    user: Awaited<ReturnType<typeof candidateDashboard>>["user"];
    history: AptitudeHistoryItem[];
    config: AptitudeSessionConfig;
  }>("CANDIDATE", loadPracticeData);
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [companyType, setCompanyType] = useState("");
  const [experienceLevel, setExperienceLevel] = useState<"Fresher" | "Experienced">("Fresher");

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load practice."} />;

  return (
    <DashboardFrame role="CANDIDATE" user={data.user}>
      <div className="mb-6">
        <p className="text-[11px] font-bold uppercase tracking-[0.19em] text-indigo-600">Practice studio</p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-950 sm:text-[30px]">Build your interview confidence</h1>
        <p className="mt-1.5 max-w-2xl text-sm leading-6 text-slate-500">
          Choose your goal and we’ll prepare a focused practice round. Your results help guide what comes next.
        </p>
      </div>

      <section className="mb-5 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-indigo-100 bg-gradient-to-r from-indigo-50 via-white to-sky-50 px-5 py-4">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-600 text-sm font-bold text-white shadow-sm shadow-indigo-200">01</span>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-indigo-600">Your current practice round</p>
            <p className="mt-1 text-sm font-bold text-slate-900">Aptitude &amp; reasoning</p>
          </div>
        </div>
        <span className="rounded-full border border-emerald-200 bg-white px-3 py-1.5 text-[10px] font-bold text-emerald-700">Ready to start</span>
      </section>

      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.15fr)_minmax(340px,0.85fr)]">
        <DashboardPanel title="Personalize your practice" description="We’ll use these details to shape the assessment.">
          <div className="space-y-5">
            <label className="block text-xs font-bold text-slate-700">
              What role are you preparing for?
              <input
                className="mt-2.5 w-full rounded-xl border border-slate-200 bg-slate-50/60 px-4 py-3 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-100"
                maxLength={100}
                minLength={2}
                onChange={(event) => setTargetRole(event.target.value)}
                placeholder="e.g. Software Engineer"
                required
                value={targetRole}
              />
              <span className="mt-1.5 block text-[10px] font-medium text-slate-400">Your target role helps personalize question selection.</span>
            </label>
            <label className="block text-xs font-bold text-slate-700">
              Company type <span className="font-medium text-slate-400">(optional)</span>
              <select
                className="mt-2.5 w-full rounded-xl border border-slate-200 bg-slate-50/60 px-4 py-3 text-sm font-medium text-slate-800 outline-none transition hover:border-slate-300 focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-100"
                onChange={(event) => setCompanyType(event.target.value)}
                value={companyType}
              >
                <option value="">Any company type</option>
                <option value="Product company">Product company</option>
                <option value="IT services">IT services</option>
                <option value="Startup">Startup</option>
                <option value="BFSI">Banking &amp; financial services</option>
                <option value="Consulting">Consulting</option>
              </select>
            </label>
            <fieldset>
              <legend className="text-xs font-bold text-slate-700">Your experience level</legend>
              <div className="mt-2.5 grid grid-cols-2 gap-3">
                {(["Fresher", "Experienced"] as const).map((level) => (
                  <button
                    aria-pressed={experienceLevel === level}
                    className={`rounded-xl border px-4 py-3 text-left transition ${
                      experienceLevel === level
                        ? "border-indigo-300 bg-indigo-50/70 ring-2 ring-indigo-100"
                        : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
                    }`}
                    key={level}
                    onClick={() => setExperienceLevel(level)}
                    type="button"
                  >
                    <span className={`block text-xs font-bold ${experienceLevel === level ? "text-indigo-800" : "text-slate-700"}`}>{level}</span>
                    <span className="mt-1 block text-[10px] text-slate-500">{level === "Fresher" ? "Entry-level or campus placement" : "Already have professional experience"}</span>
                  </button>
                ))}
              </div>
            </fieldset>
            <button
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3.5 text-xs font-bold text-white shadow-sm shadow-indigo-200 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={targetRole.trim().length < 2}
              onClick={() => {
                const query = new URLSearchParams({
                  targetRole: targetRole.trim(),
                  experienceLevel,
                });
                if (companyType) query.set("companyType", companyType);
                router.push(`/candidate/practice/aptitude?${query.toString()}`);
              }}
              type="button"
            >
              Continue to assessment <span aria-hidden="true">→</span>
            </button>
          </div>
        </DashboardPanel>

        <div className="space-y-5">
          <DashboardPanel title="What’s in this round?" description="A balanced placement-style assessment.">
            <div className="space-y-2.5">
              {Object.entries(data.config.categoryCounts).map(([category, count], index) => (
                <div className="flex items-center justify-between gap-3 rounded-xl border border-slate-100 bg-slate-50/70 px-3.5 py-3" key={category}>
                  <div className="flex items-center gap-3">
                    <span className={`grid h-8 w-8 place-items-center rounded-lg text-[10px] font-bold ${
                      index === 0 ? "bg-violet-100 text-violet-700" : index === 1 ? "bg-sky-100 text-sky-700" : "bg-amber-100 text-amber-700"
                    }`}>{String(index + 1).padStart(2, "0")}</span>
                    <span className="text-xs font-semibold text-slate-700">{category}</span>
                  </div>
                  <span className="text-[10px] font-bold text-slate-500">{count} questions</span>
                </div>
              ))}
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2.5">
              <div className="rounded-xl bg-[#171b3b] px-3.5 py-3 text-white">
                <p className="text-lg font-bold">{data.config.questionCount}</p>
                <p className="mt-0.5 text-[10px] text-indigo-100/70">Total questions</p>
              </div>
              <div className="rounded-xl bg-[#171b3b] px-3.5 py-3 text-white">
                <p className="text-lg font-bold">{formatDuration(data.config.estimatedDurationSeconds)}</p>
                <p className="mt-0.5 text-[10px] text-indigo-100/70">Estimated time</p>
              </div>
            </div>
          </DashboardPanel>

          <DashboardPanel title="Your recent sessions" description="Resume an attempt or revisit your results.">
            {data.history.length ? (
              <ul className="space-y-2.5">
                {data.history.slice(0, 4).map((item) => (
                  <li className="flex items-center justify-between gap-3 rounded-xl border border-slate-100 px-3.5 py-3" key={item.sessionId}>
                    <div className="min-w-0">
                      <p className="truncate text-xs font-bold text-slate-800">{item.targetRole}</p>
                      <p className="mt-1 text-[10px] text-slate-500">
                        {item.totalQuestions} questions{item.accuracy === null ? "" : ` · ${item.accuracy}% accuracy`}
                      </p>
                    </div>
                    <Link
                      className="shrink-0 rounded-lg bg-slate-100 px-3 py-2 text-[10px] font-bold text-slate-700 transition hover:bg-indigo-50 hover:text-indigo-700"
                      href={item.status === "IN_PROGRESS"
                        ? `/candidate/practice/aptitude/test?sessionId=${encodeURIComponent(item.sessionId)}`
                        : `/candidate/practice/aptitude/result?sessionId=${encodeURIComponent(item.sessionId)}`}
                    >
                      {item.status === "IN_PROGRESS" ? "Resume" : "Result"}
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState>Your first practice session will show up here. Complete a round to start building your history.</EmptyState>
            )}
          </DashboardPanel>
        </div>
      </div>
      <Link
        className="mt-5 inline-flex text-xs font-bold text-indigo-700 hover:text-indigo-900"
        href="/candidate/practice/history"
      >
        View all practice history <span className="ml-1" aria-hidden="true">→</span>
      </Link>
      <div className="mt-4 flex flex-wrap gap-3">
        <Link className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700" href="/candidate/practice/technical">Technical concepts</Link>
        <Link className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700" href="/candidate/practice/coding">Coding challenge</Link>
        <Link className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700" href="/candidate/practice/behavioral">Behavioral interview</Link>
      </div>
    </DashboardFrame>
  );
}
