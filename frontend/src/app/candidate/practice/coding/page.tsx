"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

type CodingQuestion = {
  id: string;
  question: string;
  topic: string;
  category: string;
  difficulty: string;
  test_cases: string[];
};

export default function CodingPracticePage() {
  const [questions, setQuestions] = useState<CodingQuestion[]>([]);
  const [code, setCode] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, { passed: boolean; stdout: string; stderr: string }>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [targetRole, setTargetRole] = useState("Software Engineer");

  async function loadQuestions() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/candidate/practice/rounds/coding/questions?limit=5&target_role=${encodeURIComponent(targetRole)}`, {
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

  async function runTests(questionId: string) {
    const res = await fetch(`${API_BASE}/candidate/practice/rounds/coding/run`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionId, code: code[questionId] || "" }),
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    const data = await res.json();
    setResults((prev) => ({
      ...prev,
      [questionId]: { passed: data.passed, stdout: data.stdout, stderr: data.stderr },
    }));
  }

  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-bold">Coding Challenge Practice</h1>
      <p className="mb-4 text-sm text-slate-600">Write Python code in the editor and run the provided tests.</p>
      <div className="mb-4">
        <label className="mr-2 text-sm font-semibold">Target role:</label>
        <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="rounded border border-slate-300 px-2 py-1 text-sm">
          <option>Software Engineer</option>
          <option>Data Analyst</option>
          <option>AI Engineer</option>
        </select>
      </div>
      <button onClick={loadQuestions} className="mb-6 rounded bg-indigo-600 px-4 py-2 text-white">
        {loading ? "Loading..." : "Load Problems"}
      </button>
      {error && <p className="mb-4 text-red-600">{error}</p>}
      <div className="space-y-8">
        {questions.map((q, index) => (
          <div key={q.id} className="rounded-xl border border-slate-200 p-4">
            <p className="mb-1 text-xs font-bold text-indigo-600">Question {index + 1}</p>
            <p className="mb-2 font-semibold">{q.question}</p>
            <p className="mb-2 text-xs text-slate-500">
              {q.category} · {q.topic} · {q.difficulty}
            </p>
            <p className="mb-2 text-xs text-slate-500">Tests:</p>
            <pre className="mb-3 rounded bg-slate-100 p-2 text-xs">{q.test_cases.join("\n")}</pre>
            <MonacoEditor
              height="260px"
              defaultLanguage="python"
              value={code[q.id] || ""}
              onChange={(value) => setCode((prev) => ({ ...prev, [q.id]: value || "" }))}
              options={{ minimap: { enabled: false }, fontSize: 14 }}
            />
            <button
              onClick={() => runTests(q.id)}
              className="mt-3 rounded bg-slate-800 px-3 py-1 text-white"
            >
              Run Tests
            </button>
            {results[q.id] && (
              <div className="mt-3">
                <p className={`font-semibold ${results[q.id].passed ? "text-green-600" : "text-red-600"}`}>
                  {results[q.id].passed ? "PASS" : "FAIL"}
                </p>
                {results[q.id].stderr && (
                  <pre className="mt-2 rounded bg-red-50 p-2 text-xs text-red-700">{results[q.id].stderr}</pre>
                )}
              </div>
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