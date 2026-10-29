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
  options?: string[];
};

export default function TechnicalPracticePage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number | null>>({});
  const [markedForReview, setMarkedForReview] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<Record<string, { score: number; method: string }>>({});
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadQuestions() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/candidate/practice/rounds/technical/questions?limit=5&target_role=${encodeURIComponent(targetRole)}`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error(await res.text());
      setQuestions(await res.json());
      setSelectedAnswers({});
      setMarkedForReview({});
      setResults({});
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function submit(questionId: string) {
    const res = await fetch(`${API_BASE}/candidate/practice/rounds/technical/evaluate`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionId, answer: "", selectedAnswer: selectedAnswers[questionId] }),
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
      <h1 className="text-2xl font-bold">Technical Concepts Practice</h1>
      <div className="mb-6 rounded-xl border border-indigo-200 bg-indigo-50 p-4">
        <p className="text-sm font-semibold text-indigo-900">Want a full adaptive technical interview?</p>
        <p className="mt-1 text-xs text-indigo-700">Get AI-evaluated answers, difficulty progression, and a final result report.</p>
        <Link href="/candidate/practice/technical/interview" className="mt-3 inline-block rounded bg-indigo-600 px-4 py-2 text-sm font-semibold text-white">
          Start Adaptive Interview
        </Link>
      </div>

      <p className="mb-4 text-sm text-slate-600">Answer questions and get scored.</p>
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
            <div className="space-y-2">
              {(q.options || []).map((opt, idx) => (
                <label key={idx} className="flex items-center gap-2 rounded border border-slate-200 p-2">
                  <input
                    type="radio"
                    name={q.id}
                    checked={selectedAnswers[q.id] === idx}
                    onChange={() => setSelectedAnswers((prev) => ({ ...prev, [q.id]: idx }))}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            <div className="mt-3 flex items-center gap-3">
              <button
                onClick={() => submit(q.id)}
                className="rounded bg-slate-800 px-3 py-1 text-white"
              >
                Submit
              </button>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={markedForReview[q.id] || false}
                  onChange={(e) => setMarkedForReview((prev) => ({ ...prev, [q.id]: e.target.checked }))}
                />
                Mark for review
              </label>
            </div>
            {results[q.id] && (
              <p className="mt-2 text-sm font-semibold">
                Score: {results[q.id].score}/100 ({results[q.id].method})
              </p>
            )}
          </div>
        ))}
      </div>
      <div className="mt-6">
        <Link href="/candidate/practice/technical/interview" className="text-indigo-700">Adaptive interview</Link>
      </div>
    </main>
  );
}