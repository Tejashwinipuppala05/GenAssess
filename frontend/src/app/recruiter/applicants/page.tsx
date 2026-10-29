"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RecruiterApplicantsPage() {
  const [jobId, setJobId] = useState("");
  const [applicants, setApplicants] = useState<any[]>([]);

  async function load() {
    const res = await fetch(`${API_BASE}/recruiter/jobs/${jobId}/applicants`, {
      credentials: "include",
    });
    if (res.ok) setApplicants(await res.json());
    else alert(await res.text());
  }

  async function evaluate(id: number, score: number) {
    const res = await fetch(`${API_BASE}/recruiter/applications/${id}/evaluate`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ score, status: "REVIEWED" }),
    });
    if (res.ok) load();
  }

  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-bold">Applicants</h1>
      <div className="mt-4 flex gap-2">
        <input
          className="rounded border border-slate-300 px-3 py-2"
          placeholder="Job ID"
          value={jobId}
          onChange={(e) => setJobId(e.target.value)}
        />
        <button onClick={load} className="rounded bg-indigo-600 px-4 py-2 text-white">
          Load
        </button>
      </div>
      <div className="mt-6 space-y-4">
        {applicants.map((a) => (
          <div key={a.id} className="rounded-xl border border-slate-200 p-4">
            <p className="font-semibold">Application #{a.id}</p>
            <p className="text-sm text-slate-600">
              Candidate {a.candidateId} · {a.status} · Score: {a.score ?? "N/A"}
            </p>
            <div className="mt-2 flex gap-2">
              <button
                onClick={() => evaluate(a.id, 80)}
                className="rounded bg-green-600 px-3 py-1 text-white"
              >
                Score 80
              </button>
              <button
                onClick={() => evaluate(a.id, 50)}
                className="rounded bg-amber-600 px-3 py-1 text-white"
              >
                Score 50
              </button>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}