"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { DashboardError, DashboardFrame, DashboardLoading } from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import { createJobPost, recruiterDashboard, type RecruiterDashboard } from "@/lib/auth";

export default function NewJobPage() {
  const router = useRouter();
  const { data, error: accessError, loading: checkingAccess } = useRoleResource<RecruiterDashboard>(
    "RECRUITER",
    recruiterDashboard,
  );
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [workArrangement, setWorkArrangement] = useState<"REMOTE" | "HYBRID" | "ONSITE">("HYBRID");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await createJobPost({
        title,
        description,
        location,
        work_arrangement: workArrangement,
      });
      router.replace("/recruiter/dashboard");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to publish this job.");
    } finally {
      setLoading(false);
    }
  }

  if (checkingAccess) return <DashboardLoading />;
  if (accessError || !data) return <DashboardError message={accessError || "Unable to verify recruiter access."} />;

  return (
    <DashboardFrame role="RECRUITER" user={data.user}>
      <div className="mx-auto max-w-3xl">
        <Link className="text-sm font-semibold text-indigo-700 hover:text-indigo-900" href="/recruiter/dashboard">
          ← Hiring dashboard
        </Link>
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-9">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">Hiring team</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">Post a job</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          Company verification is required before jobs can be published.
        </p>
        {error && <p aria-live="polite" className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
        <form className="mt-7 space-y-5" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-800">
            Job title
            <input
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5"
              maxLength={150}
              minLength={5}
              onChange={(event) => setTitle(event.target.value)}
              required
              value={title}
            />
          </label>
          <label className="block text-sm font-medium text-slate-800">
            Job description
            <textarea
              className="mt-2 min-h-40 w-full rounded-lg border border-slate-300 px-3 py-2.5"
              maxLength={10000}
              minLength={30}
              onChange={(event) => setDescription(event.target.value)}
              required
              value={description}
            />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm font-medium text-slate-800">
              Location
              <input
                className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5"
                maxLength={150}
                onChange={(event) => setLocation(event.target.value)}
                required
                value={location}
              />
            </label>
            <label className="block text-sm font-medium text-slate-800">
              Work arrangement
              <select
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5"
                onChange={(event) => setWorkArrangement(event.target.value as "REMOTE" | "HYBRID" | "ONSITE")}
                value={workArrangement}
              >
                <option value="REMOTE">Remote</option>
                <option value="HYBRID">Hybrid</option>
                <option value="ONSITE">On-site</option>
              </select>
            </label>
          </div>
          <button
            className="w-full rounded-lg bg-indigo-700 px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
            type="submit"
          >
            {loading ? "Publishing..." : "Publish job"}
          </button>
        </form>
        </section>
      </div>
    </DashboardFrame>
  );
}
