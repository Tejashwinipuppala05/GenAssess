"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { DashboardError, DashboardFrame, DashboardLoading } from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import {
  ApiError,
  candidateDashboard,
  getAptitudeResult,
  getAptitudeSession,
  saveAptitudeAnswer,
  submitAptitudeSession,
  type AptitudeQuestion,
  type AptitudeSession,
} from "@/lib/auth";

async function loadTestData(sessionId: string) {
  const [dashboard, session] = await Promise.all([
    candidateDashboard(),
    getAptitudeSession(sessionId),
  ]);
  return { user: dashboard.user, session };
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(remaining).padStart(2, "0")}`;
}

function updateQuestion(
  session: AptitudeSession,
  questionId: string,
  update: Partial<Pick<AptitudeQuestion, "selectedAnswer" | "markedForReview">>,
): AptitudeSession {
  return {
    ...session,
    questions: session.questions.map((question) =>
      question.id === questionId ? { ...question, ...update } : question,
    ),
  };
}

export default function AptitudeTest({ sessionId }: { sessionId: string }) {
  const router = useRouter();
  const loadData = useCallback(() => loadTestData(sessionId), [sessionId]);
  const { data, error, loading } = useRoleResource<
    { user: Awaited<ReturnType<typeof candidateDashboard>>["user"]; session: AptitudeSession }
  >("CANDIDATE", loadData);
  const [sessionOverride, setSessionOverride] = useState<AptitudeSession | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null);
  const [saveError, setSaveError] = useState("");
  const [failedSaveCount, setFailedSaveCount] = useState(0);
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const saveQueue = useRef<Promise<void>>(Promise.resolve());
  const isSubmitting = useRef(false);
  const deadlineMs = useRef<number | null>(null);
  const failedAnswers = useRef(new Map<string, { selectedAnswer: number | null; markedForReview: boolean }>());
  const session = sessionOverride ?? data?.session;

  const finishTest = useCallback(async (confirmIncomplete: boolean) => {
    if (isSubmitting.current || !session) return;
    if (confirmIncomplete) {
      const unanswered = session.questions.filter((question) => question.selectedAnswer === null).length;
      if (unanswered > 0 && !window.confirm(`You have ${unanswered} unanswered question(s). Submit your test?`)) {
        return;
      }
    }

    isSubmitting.current = true;
    setSubmitting(true);
    setSubmitError("");
    try {
      await saveQueue.current;
      if (failedSaveCount > 0 && confirmIncomplete) {
        throw new Error("At least one answer was not saved. Retry saving it before submitting.");
      }
      await submitAptitudeSession(sessionId);
      router.replace(`/candidate/practice/aptitude/result?sessionId=${encodeURIComponent(sessionId)}`);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 409) {
        try {
          await getAptitudeResult(sessionId);
          router.replace(`/candidate/practice/aptitude/result?sessionId=${encodeURIComponent(sessionId)}`);
          return;
        } catch {
          // Report the original submission failure below.
        }
      }
      setSubmitError(reason instanceof Error ? reason.message : "Unable to submit your test.");
      isSubmitting.current = false;
      setSubmitting(false);
    }
  }, [failedSaveCount, router, session, sessionId]);

  useEffect(() => {
    if (!data) return;
    if (data.session.status === "COMPLETED") {
      router.replace(`/candidate/practice/aptitude/result?sessionId=${encodeURIComponent(sessionId)}`);
      return;
    }
    if (deadlineMs.current === null) {
      deadlineMs.current = Date.now() + (data.session.expiresAt - data.session.serverTime) * 1000;
    }
    const tick = () => {
      const seconds = Math.max(0, Math.ceil(((deadlineMs.current ?? Date.now()) - Date.now()) / 1000));
      setRemainingSeconds(seconds);
      if (seconds === 0) void finishTest(false);
    };
    tick();
    const timer = window.setInterval(tick, 1000);
    return () => window.clearInterval(timer);
  }, [data, finishTest, router, sessionId]);

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load this aptitude test."} />;
  if (!session?.questions.length) {
    return <DashboardError message="This test session has no questions. Return to practice and start a new session." />;
  }

  const question = session.questions[currentIndex];
  const answeredCount = session.questions.filter((item) => item.selectedAnswer !== null).length;
  const markedCount = session.questions.filter((item) => item.markedForReview).length;

  function queueSave(questionId: string, selectedAnswer: number | null, markedForReview: boolean) {
    setSaveError("");
    const save = saveQueue.current.then(() =>
      saveAptitudeAnswer(sessionId, questionId, { selectedAnswer, markedForReview }),
    );
    failedAnswers.current.set(questionId, { selectedAnswer, markedForReview });
    saveQueue.current = save.then(
      () => {
        failedAnswers.current.delete(questionId);
        setFailedSaveCount(failedAnswers.current.size);
        if (failedAnswers.current.size === 0) setSaveError("");
      },
      (reason: unknown) => {
        setFailedSaveCount(failedAnswers.current.size);
        setSaveError(reason instanceof Error ? reason.message : "Your answer could not be saved.");
      },
    );
    return save;
  }

  function retryFailedAnswers() {
    for (const [questionId, answer] of failedAnswers.current) {
      void queueSave(questionId, answer.selectedAnswer, answer.markedForReview).catch(() => undefined);
    }
  }

  function selectAnswer(optionIndex: number) {
    if (!session) return;
    setSessionOverride((previous) => updateQuestion(previous ?? session, question.id, { selectedAnswer: optionIndex }));
    void queueSave(question.id, optionIndex, question.markedForReview).catch(() => undefined);
  }

  function markForReview() {
    if (!session) return;
    const markedForReview = !question.markedForReview;
    setSessionOverride((previous) => updateQuestion(previous ?? session, question.id, { markedForReview }));
    void queueSave(question.id, question.selectedAnswer, markedForReview).catch(() => undefined);
  }

  return (
    <DashboardFrame role="CANDIDATE" user={data.user}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-indigo-600">Round 01 · Aptitude &amp; reasoning</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-950">{session.targetRole} practice</h1>
          <Link className="mt-1 inline-flex text-[10px] font-semibold text-slate-500 hover:text-indigo-700" href="/candidate/dashboard">
            Exit to dashboard
          </Link>
        </div>
        <div aria-live="polite" className={`flex items-center gap-3 rounded-xl px-4 py-2.5 ${remainingSeconds !== null && remainingSeconds < 60 ? "bg-red-50 text-red-700 ring-1 ring-red-200" : "bg-[#171b3b] text-white"}`}>
          <span className={`grid h-8 w-8 place-items-center rounded-lg text-sm ${remainingSeconds !== null && remainingSeconds < 60 ? "bg-red-100" : "bg-white/10"}`}>◷</span>
          <div>
            <p className="text-[9px] font-bold uppercase tracking-[0.14em] opacity-70">Time remaining</p>
            <p className="font-mono text-lg font-bold leading-5">{remainingSeconds === null ? "--:--" : formatTime(remainingSeconds)}</p>
          </div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3 text-xs">
        <span className="font-bold text-slate-800">Question {currentIndex + 1} <span className="font-medium text-slate-400">of {session.totalQuestions}</span></span>
        <span className="font-medium text-slate-500">{answeredCount} answered <span className="px-1 text-slate-300">·</span> {markedCount} marked for review</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200/80">
        <div className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-violet-500 transition-all" style={{ width: `${(answeredCount / session.totalQuestions) * 100}%` }} />
      </div>

      <section className="mt-5 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_5px_24px_rgba(15,23,42,0.045)] sm:p-8">
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full bg-indigo-50 px-3 py-1.5 text-[10px] font-bold text-indigo-800">{question.category}</span>
          <span className="rounded-full bg-slate-100 px-3 py-1.5 text-[10px] font-bold text-slate-700">{question.topic}</span>
          <span className="rounded-full bg-amber-50 px-3 py-1.5 text-[10px] font-bold text-amber-800">{question.difficulty}</span>
        </div>
        <h2 className="mt-6 max-w-4xl text-lg font-semibold leading-8 text-slate-950 sm:text-xl">{question.question}</h2>
        <div className="mt-6 space-y-3">
          {question.options.map((option, optionIndex) => (
            <button
              aria-pressed={question.selectedAnswer === optionIndex}
              className={`flex w-full items-start gap-3 rounded-xl border px-4 py-3.5 text-left text-sm leading-6 transition ${
                question.selectedAnswer === optionIndex
                  ? "border-indigo-400 bg-indigo-50/80 text-indigo-950 ring-2 ring-indigo-100"
                  : "border-slate-200 bg-white text-slate-700 hover:border-indigo-200 hover:bg-slate-50/70"
              }`}
              key={`${question.id}-${optionIndex}`}
              onClick={() => selectAnswer(optionIndex)}
              type="button"
            >
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-current text-[10px] font-bold">
                {String.fromCharCode(65 + optionIndex)}
              </span>
              <span>{option}</span>
            </button>
          ))}
        </div>

        <div className="mt-7 flex flex-wrap justify-between gap-3 border-t border-slate-100 pt-5">
          <button
            className={`rounded-xl border px-4 py-2.5 text-xs font-bold transition ${
              question.markedForReview ? "border-amber-300 bg-amber-50 text-amber-900" : "border-slate-200 text-slate-600 hover:bg-slate-50"
            }`}
            onClick={markForReview}
            type="button"
          >
            {question.markedForReview ? "Marked for review" : "Mark for review"}
          </button>
          <div className="flex gap-3">
            <button
              className="rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-bold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              disabled={currentIndex === 0 || submitting}
              onClick={() => setCurrentIndex((index) => index - 1)}
              type="button"
            >
              Previous
            </button>
            {currentIndex < session.totalQuestions - 1 ? (
              <button
                className="rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white transition hover:bg-indigo-700 disabled:opacity-60"
                disabled={submitting}
                onClick={() => setCurrentIndex((index) => index + 1)}
                type="button"
              >
                Next
              </button>
            ) : (
              <button
                className="rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white transition hover:bg-indigo-700 disabled:opacity-60"
                disabled={submitting}
                onClick={() => void finishTest(true)}
                type="button"
              >
                {submitting ? "Submitting..." : "Submit test"}
              </button>
            )}
          </div>
        </div>
        {(saveError || submitError) && (
          <p aria-live="polite" className="mt-4 text-sm text-red-700">{saveError || submitError}</p>
        )}
        {failedSaveCount > 0 && (
          <button
            className="mt-3 rounded-lg border border-red-300 px-4 py-2 text-sm font-semibold text-red-800 hover:bg-red-50"
            onClick={retryFailedAnswers}
            type="button"
          >
            Retry saving unsaved answers ({failedSaveCount})
          </button>
        )}
      </section>

      <section className="mt-5 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_2px_12px_rgba(15,23,42,0.035)]">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-xs font-bold text-slate-900">Question navigator</h2>
          <p className="text-[10px] font-medium text-slate-400">Select a number to jump to that question</p>
        </div>
        <div className="mt-3 grid grid-cols-5 gap-2 sm:grid-cols-10">
          {session.questions.map((item, index) => (
            <button
              aria-current={index === currentIndex ? "step" : undefined}
              aria-label={`Question ${index + 1}${item.selectedAnswer === null ? ", unanswered" : ", answered"}${item.markedForReview ? ", marked for review" : ""}`}
              className={`relative h-10 rounded-xl border text-xs font-bold transition hover:-translate-y-0.5 ${
                index === currentIndex
                  ? "border-indigo-700 bg-indigo-700 text-white"
                  : item.markedForReview
                    ? "border-amber-300 bg-amber-50 text-amber-900"
                    : item.selectedAnswer !== null
                      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                      : "border-slate-200 bg-white text-slate-600"
              }`}
              key={item.id}
              onClick={() => setCurrentIndex(index)}
              type="button"
            >
              {index + 1}
            </button>
          ))}
        </div>
      </section>
      <div className="mt-5 flex justify-between">
        <Link className="text-xs font-semibold text-slate-500 hover:text-slate-900" href="/candidate/practice">
          Exit to practice
        </Link>
        {currentIndex < session.totalQuestions - 1 && (
          <button
            className="text-xs font-bold text-indigo-700 hover:text-indigo-900"
            disabled={submitting}
            onClick={() => void finishTest(true)}
            type="button"
          >
            Submit test
          </button>
        )}
      </div>
    </DashboardFrame>
  );
}
