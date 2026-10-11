"use client";

import Link from "next/link";
import { useCallback } from "react";
import {
  DashboardError,
  DashboardFrame,
  DashboardLoading,
  DashboardPanel,
  EmptyState,
  StatCard,
} from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import { candidateDashboard, getAptitudeResult, type AptitudeResult } from "@/lib/auth";

async function loadResult(sessionId: string) {
  const [dashboard, result] = await Promise.all([
    candidateDashboard(),
    getAptitudeResult(sessionId),
  ]);
  return { user: dashboard.user, result };
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return `${minutes}m ${String(remaining).padStart(2, "0")}s`;
}

function formatAnswer(options: string[], selected: number | null): string {
  return selected === null ? "Not answered" : `${String.fromCharCode(65 + selected)}. ${options[selected]}`;
}

export default function AptitudeResultPage({ sessionId }: { sessionId: string }) {
  const loadData = useCallback(() => loadResult(sessionId), [sessionId]);
  const { data, error, loading } = useRoleResource<
    { user: Awaited<ReturnType<typeof candidateDashboard>>["user"]; result: AptitudeResult }
  >("CANDIDATE", loadData);

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load your aptitude result."} />;

  const { result } = data;

  return (
    <DashboardFrame role="CANDIDATE" user={data.user}>
      <section className="relative overflow-hidden rounded-[26px] bg-[#171b3b] px-6 py-7 text-white shadow-[0_18px_48px_rgba(27,31,72,0.16)] sm:px-9 sm:py-8">
        <div aria-hidden="true" className="pointer-events-none absolute -right-16 -top-28 h-72 w-72 rounded-full border border-white/10" />
        <div className="relative flex flex-wrap items-end justify-between gap-5">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.16em] text-indigo-100">
              Assessment complete <span className="text-emerald-300">✓</span>
            </span>
            <h1 className="mt-4 text-[26px] font-bold tracking-tight sm:text-[32px]">Your practice result</h1>
            <p className="mt-1.5 text-xs text-indigo-100/70">
              {result.targetRole} · {result.experienceLevel}{result.companyType ? ` · ${result.companyType}` : ""}
            </p>
          </div>
          <div className="flex items-end gap-5">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-indigo-100/60">Your score</p>
              <p className="mt-1 text-3xl font-bold tracking-tight">{result.score}<span className="text-lg text-indigo-100/50">/{result.totalQuestions}</span></p>
            </div>
            <div className="mb-1 h-10 w-px bg-white/15" />
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-indigo-100/60">Accuracy</p>
              <p className="mt-1 text-2xl font-bold">{result.accuracy}%</p>
            </div>
          </div>
        </div>
        <div className="relative mt-6 flex flex-wrap gap-2">
          <Link className="rounded-xl bg-white px-4 py-2.5 text-[10px] font-bold text-indigo-950 transition hover:bg-indigo-50" href="/candidate/practice">
            Try another test <span aria-hidden="true">→</span>
          </Link>
          <Link className="rounded-xl border border-white/20 px-4 py-2.5 text-[10px] font-semibold text-white transition hover:bg-white/10" href="/candidate/dashboard">
            Back to dashboard
          </Link>
          <Link className="rounded-xl border border-white/20 px-4 py-2.5 text-[10px] font-semibold text-white transition hover:bg-white/10" href="/candidate/practice/history">
            Practice history
          </Link>
        </div>
      </section>

      <section className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Correct answers" value={result.correctAnswers} detail={`Out of ${result.totalQuestions} questions`} />
        <StatCard label="Incorrect answers" value={result.incorrectAnswers} detail="Review these explanations below" />
        <StatCard label="Unanswered" value={result.unansweredQuestions} detail="Questions left blank" />
        <StatCard label="Time taken" value={formatDuration(result.timeTakenSeconds)} detail={`Test limit: ${formatDuration(result.durationSeconds)}`} />
      </section>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <DashboardPanel title="Performance by category">
          <div className="space-y-4">
            {result.categoryPerformance.map((item) => (
              <div key={item.category}>
                <div className="flex justify-between gap-3 text-sm">
                  <span className="font-medium text-slate-800">{item.category}</span>
                  <span className="text-slate-600">{item.correct}/{item.total} · {item.accuracy}%</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-violet-500" style={{ width: `${item.accuracy}%` }} />
                </div>
                <p className="mt-1 text-xs text-slate-500">{item.incorrect} incorrect · {item.unanswered} unanswered</p>
              </div>
            ))}
          </div>
        </DashboardPanel>

        <DashboardPanel title="Performance by difficulty">
          <div className="space-y-3">
            {result.difficultyPerformance.map((item) => (
              <div className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-4 py-3" key={item.difficulty}>
                <span className="text-sm font-medium text-slate-800">{item.difficulty}</span>
                <span className="text-sm text-slate-600">{item.correct}/{item.total} correct · {item.accuracy}%</span>
              </div>
            ))}
          </div>
        </DashboardPanel>

        <DashboardPanel title="Topic insights">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-semibold text-emerald-800">Strong areas</h3>
              {result.strongTopics.length ? (
                <ul className="mt-2 space-y-2 text-sm text-slate-700">
                  {result.strongTopics.map((topic) => <li className="rounded-md bg-emerald-50 px-3 py-2" key={topic}>{topic}</li>)}
                </ul>
              ) : (
                <p className="mt-2 text-sm text-slate-500">Keep practicing to identify your strongest topics.</p>
              )}
            </div>
            <div>
              <h3 className="text-sm font-semibold text-amber-800">Needs practice</h3>
              {result.weakTopics.length ? (
                <ul className="mt-2 space-y-2 text-sm text-slate-700">
                  {result.weakTopics.map((topic) => <li className="rounded-md bg-amber-50 px-3 py-2" key={topic}>{topic}</li>)}
                </ul>
              ) : (
                <p className="mt-2 text-sm text-slate-500">No weak topic identified in this test.</p>
              )}
            </div>
          </div>
          <p className="mt-5 rounded-lg border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm leading-6 text-indigo-950">
            {result.recommendation}
          </p>
        </DashboardPanel>

        <DashboardPanel title="Topic-wise performance">
          <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
            {result.topicPerformance.map((item) => (
              <div className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2.5" key={`${item.category}-${item.topic}`}>
                <div>
                  <p className="text-sm font-medium text-slate-800">{item.topic}</p>
                  <p className="text-xs text-slate-500">{item.category}</p>
                </div>
                <span className="shrink-0 text-sm text-slate-600">{item.correct}/{item.total} · {item.accuracy}%</span>
              </div>
            ))}
          </div>
        </DashboardPanel>
      </div>

      <DashboardPanel title="Answer review" description="Review the correct answer and explanation for each question.">
        <div className="space-y-4">
          {result.answers.map((answer, index) => (
            <article className="rounded-lg border border-slate-200 p-4" key={answer.questionId}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Question {index + 1} · {answer.topic} · {answer.difficulty}
                </p>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                  answer.isCorrect === true
                    ? "bg-emerald-50 text-emerald-800"
                    : answer.isCorrect === false
                      ? "bg-red-50 text-red-800"
                      : "bg-slate-100 text-slate-700"
                }`}>
                  {answer.isCorrect === true ? "Correct" : answer.isCorrect === false ? "Incorrect" : "Unanswered"}
                </span>
              </div>
              <h3 className="mt-3 text-sm font-semibold leading-6 text-slate-900">{answer.question}</h3>
              <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
                <p className="rounded-md bg-slate-50 px-3 py-2 text-slate-700">Your answer: {formatAnswer(answer.options, answer.selectedAnswer)}</p>
                <p className="rounded-md bg-emerald-50 px-3 py-2 text-emerald-900">Correct answer: {formatAnswer(answer.options, answer.correctAnswer)}</p>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-600">{answer.explanation}</p>
            </article>
          ))}
          {!result.answers.length && <EmptyState>No answers are available for this result.</EmptyState>}
        </div>
      </DashboardPanel>
    </DashboardFrame>
  );
}
