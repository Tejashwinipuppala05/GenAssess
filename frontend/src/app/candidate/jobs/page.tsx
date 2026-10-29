"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function CandidateJobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [applied, setApplied] = useState<Record<number, string>>({});

  useEffect(() => {
    fetch(`${API_BASE}/candidate/jobs`, { credentials: "include" })
      .then((r) => r.json())
      .then(setJobs)
      .catch(() => {});
  }, []);

  async function apply(jobId: number) {
    const res = await fetch(`${API_BASE}/candidate/jobs/${jobId}/apply`, {
      method: "POST",
      credentials: "include",
    });
    if (res.ok) setApplied((prev) => ({ ...prev, [jobId]: "Applied" }));
    else setApplied((prev) => ({ ...prev, [jobId]: "Error/Already applied" }));
  }

  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-bold">Open Jobs</h1>
      <div className="mt-6 space-y-4">
        {jobs.map((job) => (
          <div key={job.id} className="rounded-xl border border-slate-200 p-4">
            <h2 className="font-semibold">{job.title}</h2>
            <p className="text-sm text-slate-600">{job.description}</p>
            <p className="mt-1 text-xs text-slate-500">
              {job.location} · {job.work_arrangement}
            </p>
            <button
              onClick={() => apply(job.id)}
              className="mt-3 rounded bg-indigo-600 px-3 py-1 text-white"
            >
              Apply
            </button>
            {applied[job.id] && <span className="ml-3 text-sm">{applied[job.id]}</span>}
          </div>
        ))}
      </div>
      <div className="mt-6">
        <Link href="/candidate/practice" className="text-indigo-700">Back to practice</Link>
      </div>
    </main>
  );
}