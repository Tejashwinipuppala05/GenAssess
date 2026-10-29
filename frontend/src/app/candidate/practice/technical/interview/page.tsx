"use client";

import { useState } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function TechnicalInterviewPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState<any>(null);
  const [answer, setAnswer] = useState("");
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [role, setRole] = useState("Software Engineer");
  const [experience, setExperience] = useState("Fresher");
  const [topic, setTopic] = useState("General");
  const [count, setCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/candidate/practice/technical/sessions`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ targetRole: role, experienceLevel: experience, topic, totalQuestions: count }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setSessionId(data.id);
      setQuestion(data.question);
      setAnswer("");
      setSelectedAnswer(null);
      setFeedback(null);
      setResult(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function submit() {
    if (!sessionId || !question) return;
    const res = await fetch(`${API_BASE}/candidate/practice/technical/sessions/${sessionId}/answers/${question.id}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer, selectedAnswer }),
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    const data = await res.json();
    setFeedback(data);
    if (data.nextQuestion) {
      setQuestion(data.nextQuestion);
      setAnswer("");
      setSelectedAnswer(null);
    } else {
      setQuestion(null);
    }
  }
  async function finish() {
    if (!sessionId) return;
    const res = await fetch(`${API_BASE}/candidate/practice/technical/sessions/${sessionId}/submit`, {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    setResult(await res.json());
  }

  if (!sessionId) {
    return (
      <main className="mx-auto max-w-4xl p-6">
        <h1 className="text-2xl font-bold">Adaptive Technical Interview</h1>
        <div className="mt-6 space-y-4">
          <div>
            <label className="mr-2 text-sm font-semibold">Role:</label>
            <select value={role} onChange={(e) => setRole(e.target.value)} className="rounded border border-slate-300 px-2 py-1 text-sm">
              <option>Software Engineer</option>
              <option>Data Analyst</option>
              <option>AI Engineer</option>
            </select>
          </div>
          <div>
            <label className="mr-2 text-sm font-semibold">Experience:</label>
            <select value={experience} onChange={(e) => setExperience(e.target.value)} className="rounded border border-slate-300 px-2 py-1 text-sm">
              <option>Fresher</option>
              <option>Experienced</option>
            </select>
          </div>
          <div>
            <label className="mr-2 text-sm font-semibold">Topic:</label>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} className="rounded border border-slate-300 px-2 py-1 text-sm" />
          </div>
          <div>
            <label className="mr-2 text-sm font-semibold">Questions:</label>
            <input type="number" value={count} onChange={(e) => setCount(Number(e.target.value))} className="rounded border border-slate-300 px-2 py-1 text-sm w-20" />
          </div>
          <button onClick={start} disabled={loading} className="rounded bg-indigo-600 px-4 py-2 text-white">
            {loading ? "Starting..." : "Start Interview"}
          </button>
          {error && <p className="text-red-600">{error}</p>}
        </div>
        <div className="mt-6">
          <Link href="/candidate/practice" className="text-indigo-700">Back to practice</Link>
        </div>
      </main>
    );
  }

  if (result) {
    return (
      <main className="mx-auto max-w-4xl p-6">
        <h1 className="text-2xl font-bold">Interview Results</h1>
        <p className="mt-4">Average score: {result.averageScore}/100</p>
        <p>Answered: {result.answered}/{result.totalQuestions}</p>
        <p>{result.recommendation}</p>
        <ul className="mt-4 space-y-2">
          {result.answers.map((a: any, i: number) => (
            <li key={i} className="rounded border border-slate-200 p-3">
              <p className="font-semibold">{a.question}</p>
              <p className="text-sm">Your answer: {a.answer}</p>
              <p className="text-sm">Score: {a.score}/100</p>
            </li>
          ))}
        </ul>
        <button onClick={() => { setSessionId(null); setResult(null); }} className="mt-4 rounded bg-slate-800 px-4 py-2 text-white">
          New Interview
        </button>
        <div className="mt-6">
          <Link href="/candidate/practice" className="text-indigo-700">Back to practice</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-bold">Adaptive Technical Interview</h1>
      {question ? (
        <div className="mt-6">
          <p className="mb-1 text-xs font-bold text-indigo-600">{question.topic} · {question.difficulty}</p>
          <p className="mb-4 font-semibold">{question.question}</p>
          {question.options && (
            <div className="mb-4 space-y-2">
              {question.options.map((opt: string, idx: number) => (
                <label key={idx} className="flex items-center gap-2 rounded border border-slate-200 p-2">
                  <input type="radio" name={question.id} checked={selectedAnswer === idx} onChange={() => setSelectedAnswer(idx)} />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
          )}
          <textarea
            className="w-full rounded border border-slate-300 p-2"
            rows={4}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Or type a descriptive answer..."
          />
          <button onClick={submit} className="mt-3 rounded bg-slate-800 px-4 py-2 text-white">
            Submit Answer
          </button>
        </div>
      ) : (
        <p className="mt-6">Loading question...</p>
      )}
      {feedback && (
        <div className="mt-4 rounded border border-slate-200 p-4">
          <p className="font-semibold">Score: {feedback.score}/100 ({feedback.method})</p>
          <p>{feedback.correctness}</p>
          {feedback.suggestions?.length > 0 && <p>Suggestions: {feedback.suggestions.join(" ")}</p>}
          <p className="mt-2 text-sm text-slate-600">Ideal: {feedback.idealAnswer}</p>
          {!question && (
            <button onClick={finish} className="mt-3 rounded bg-indigo-600 px-4 py-2 text-white">
              View Results
            </button>
          )}
        </div>
      )}
      <div className="mt-6">
        <Link href="/candidate/practice" className="text-indigo-700">Back to practice</Link>
      </div>
    </main>
  );
}