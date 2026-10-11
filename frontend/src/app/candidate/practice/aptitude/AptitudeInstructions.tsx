"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { DashboardError, DashboardFrame, DashboardLoading, DashboardPanel } from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import {
  aptitudeSessionConfig,
  candidateDashboard,
  createAptitudeSession,
  type AptitudeSessionConfig,
} from "@/lib/auth";

async function loadPageData() {
  const [dashboard, config] = await Promise.all([candidateDashboard(), aptitudeSessionConfig()]);
  return { user: dashboard.user, config };
}

function formatDuration(seconds: number): string {
  const minutes = Math.ceil(seconds / 60);
  return `${minutes} minute${minutes === 1 ? "" : "s"}`;
}

export default function AptitudeInstructions({
  targetRole,
  companyType,
  experienceLevel,
}: {
  targetRole: string;
  companyType: string;
  experienceLevel: "Fresher" | "Experienced";
}) {
  const router = useRouter();
  const { data, error, loading } = useRoleResource<
    { user: Awaited<ReturnType<typeof candidateDashboard>>["user"]; config: AptitudeSessionConfig }
  >("CANDIDATE", loadPageData);
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState("");

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load aptitude instructions."} />;

  async function startTest() {
    setStarting(true);
    setStartError("");
    try {
      const session = await createAptitudeSession({
        targetRole,
        companyType: companyType || null,
        experienceLevel,
      });
      router.push(`/candidate/practice/aptitude/test?sessionId=${encodeURIComponent(session.id)}`);
    } catch (reason) {
      setStartError(reason instanceof Error ? reason.message : "Unable to start the aptitude test.");
      setStarting(false);
    }
  }

  return (
    <DashboardFrame role="CANDIDATE" user={data.user}>
      <Link className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 transition hover:text-indigo-700" href="/candidate/practice">
        <span aria-hidden="true">←</span> Back to practice setup
      </Link>
      <section className="relative mt-5 overflow-hidden rounded-[26px] bg-[#171b3b] px-6 py-7 text-white shadow-[0_18px_48px_rgba(27,31,72,0.16)] sm:px-9 sm:py-9">
        <div aria-hidden="true" className="pointer-events-none absolute -right-14 -top-28 h-72 w-72 rounded-full border border-white/10" />
        <div className="relative max-w-3xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.16em] text-indigo-100">
            Round 01 <span className="text-white/40">/</span> Aptitude &amp; reasoning
          </span>
          <h1 className="mt-5 text-[26px] font-bold leading-tight tracking-tight sm:text-[34px]">Your placement practice starts here.</h1>
          <p className="mt-2.5 max-w-2xl text-sm leading-6 text-indigo-100/75">
            A focused assessment tailored for <span className="font-semibold text-white">{targetRole}</span>
            {" "}· {experienceLevel}{companyType ? ` · ${companyType}` : ""}
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {[
              `${data.config.questionCount} questions`,
              `About ${formatDuration(data.config.estimatedDurationSeconds)}`,
              "Answers save automatically",
            ].map((item) => (
              <span className="rounded-lg border border-white/10 bg-white/[0.07] px-3 py-2 text-[10px] font-semibold text-indigo-50/90" key={item}>{item}</span>
            ))}
          </div>
        </div>
      </section>

      <div className="mt-5 grid items-start gap-5 lg:grid-cols-[minmax(0,1.05fr)_minmax(340px,0.95fr)]">
        <DashboardPanel title="Assessment blueprint" description="A balanced question set inspired by common placement-test patterns.">
          <div className="space-y-2.5">
            {Object.entries(data.config.categoryCounts).map(([category, count], index) => (
              <div className="flex items-center justify-between gap-3 rounded-xl border border-slate-100 bg-slate-50/70 px-4 py-3.5" key={category}>
                <div className="flex items-center gap-3">
                  <span className={`grid h-9 w-9 place-items-center rounded-xl text-xs font-bold ${
                    index === 0 ? "bg-violet-100 text-violet-700" : index === 1 ? "bg-sky-100 text-sky-700" : "bg-amber-100 text-amber-700"
                  }`}>0{index + 1}</span>
                  <span className="text-xs font-semibold text-slate-700">{category}</span>
                </div>
                <span className="text-xs font-bold text-slate-900">{count} questions</span>
              </div>
            ))}
          </div>
          <div className="mt-5">
            <div className="flex items-center justify-between">
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">Difficulty mix</p>
              <p className="text-[10px] text-slate-400">Balanced for practice</p>
            </div>
            <div className="mt-2.5 flex h-2.5 overflow-hidden rounded-full bg-slate-100">
              {Object.entries(data.config.difficultyDistribution).map(([level, share]) => (
                <div
                  aria-label={`${level}: ${share}%`}
                  className={level === "Easy" ? "bg-emerald-400" : level === "Medium" ? "bg-indigo-500" : "bg-violet-500"}
                  key={level}
                  style={{ width: `${share}%` }}
                  title={`${level} ${share}%`}
                />
              ))}
            </div>
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1.5">
              {Object.entries(data.config.difficultyDistribution).map(([level, share]) => (
                <span className="flex items-center gap-1.5 text-[10px] font-medium text-slate-500" key={level}>
                  <span className={`h-1.5 w-1.5 rounded-full ${level === "Easy" ? "bg-emerald-400" : level === "Medium" ? "bg-indigo-500" : "bg-violet-500"}`} />
                  {level} {share}%
                </span>
              ))}
            </div>
          </div>
        </DashboardPanel>

        <DashboardPanel title="Before you begin" description="A few quick things to know.">
          <ul className="space-y-3">
            {[
              "You can move between questions and mark any question to review.",
              "Your answers are saved as you go, so you can resume if needed.",
              "The timer is enforced by the server and the assessment submits when time runs out.",
              "At the end, review your score, topic performance and answer explanations.",
            ].map((item, index) => (
              <li className="flex gap-3 text-xs leading-5 text-slate-600" key={item}>
                <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-emerald-50 text-[10px] font-bold text-emerald-700">✓</span>
                <span>{item}</span>
                <span className="sr-only">Instruction {index + 1}</span>
              </li>
            ))}
          </ul>
          {startError && <p aria-live="polite" className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">{startError}</p>}
          <button
            className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3.5 text-xs font-bold text-white shadow-sm shadow-indigo-200 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={starting}
            onClick={() => void startTest()}
            type="button"
          >
            {starting ? "Preparing your test..." : "Start aptitude assessment"}
            {!starting && <span aria-hidden="true">→</span>}
          </button>
          <p className="mt-3 text-center text-[10px] text-slate-400">Take a breath and find a quiet place before you start.</p>
        </DashboardPanel>
      </div>
    </DashboardFrame>
  );
}
