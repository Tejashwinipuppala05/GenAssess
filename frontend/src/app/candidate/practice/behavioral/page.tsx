"use client";

import { useState } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Question = {
  id: string;
  question: string;
  topic: string;
  category: string;
  difficulty: string;
  follow_up_dimensions?: string[];
};

export default function BehavioralPracticePage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, { score: number; method: string }>>({});
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadQuestions() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/candidate/practice/rounds/behavioral/questions?limit=3&target_role=${encodeURIComponent(targetRole)}`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error(await res.text());
      setQuestions(await res.json());
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function submit(questionId: string) {
    const res = await fetch(`${API_BASE}/candidate/practice/rounds/behavioral/evaluate`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionId, answer: answers[questionId] || "" }),
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    const data = await res.json();
    setResults((prev) => ({ ...prev, [questionId]: { score: data.score, method: data.method } }));
  }

  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-bold">Behavioral / HR Practice</h1>
      <p className="mb-4 text-sm text-slate-600">Answer behavioral questions and get AI/rule-based scoring.</p>
      <div className="mb-4">
        <label className="mr-2 text-sm font-semibold">Target role:</label>
        <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="rounded border border-slate-300 px-2 py-1 text-sm">
          <option>Software Engineer</option>
          <option>Data Analyst</option>
          <option>AI Engineer</option>
        </select>
      </div>
      <button onClick={loadQuestions} className="mb-6 rounded bg-indigo-600 px-4 py-2 text-white">
        {loading ? "Loading..." : "Load Questions"}
      </button>
      {error && <p className="mb-4 text-red-600">{error}</p>}
      <div className="space-y-6">
        {questions.map((q, index) => (
          <div key={q.id} className="rounded-xl border border-slate-200 p-4">
            <p className="mb-1 text-xs font-bold text-indigo-600">Question {index + 1}</p>
            <p className="mb-2 font-semibold">{q.question}</p>
            <p className="mb-2 text-xs text-slate-500">
              {q.category} · {q.topic} · {q.difficulty}
            </p>
            {q.follow_up_dimensions && (
              <p className="mb-2 text-xs text-slate-500">
                Focus: {q.follow_up_dimensions.join(", ")}
              </p>
            )}
            <textarea
              className="w-full rounded border border-slate-300 p-2"
              rows={5}
              value={answers[q.id] || ""}
              onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
            />
            <button
              onClick={() => submit(q.id)}
              className="mt-2 rounded bg-slate-800 px-3 py-1 text-white"
            >
              Submit
            </button>
            {results[q.id] && (
              <p className="mt-2 text-sm font-semibold">
                Score: {results[q.id].score}/100 ({results[q.id].method})
              </p>
            )}
          </div>
        ))}
      </div>
      <div className="mt-6">
        <Link href="/candidate/practice" className="text-indigo-700">Back to practice</Link>
      </div>
    </main>
  );
}