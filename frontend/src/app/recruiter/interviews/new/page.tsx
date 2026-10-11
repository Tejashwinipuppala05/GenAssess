"use client";

import Link from "next/link";
import { DashboardFrame, DashboardLoading, DashboardPanel, EmptyState } from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import { recruiterInterviewSetup, type PlaceholderResponse } from "@/lib/auth";

export default function RecruiterInterviewPlaceholderPage() {
  const { data, error, loading } = useRoleResource<PlaceholderResponse>(
    "RECRUITER",
    recruiterInterviewSetup,
  );

  if (loading) return <DashboardLoading />;
  if (error || !data) {
    return (
      <main className="mx-auto mt-12 max-w-xl rounded-xl border border-red-200 bg-white p-6 text-sm text-red-700">
        {error || "Unable to open interview creation."}
      </main>
    );
  }

  return (
    <DashboardFrame role="RECRUITER" user={data.user}>
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">
        Recruiter workspace
      </p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">Create an interview</h1>
      <div className="mt-8 max-w-2xl">
        <DashboardPanel title="Coming next">
          <EmptyState>{data.message}</EmptyState>
        </DashboardPanel>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link
            className="inline-flex rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-white"
            href="/recruiter/dashboard"
          >
            Back to dashboard
          </Link>
          <Link
            className="inline-flex rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-white"
            href="/recruiter/applicants"
          >
            Applicants
          </Link>
          <Link
            className="inline-flex rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-white"
            href="/recruiter/evaluation"
          >
            Candidate evaluation
          </Link>
        </div>
      </div>
    </DashboardFrame>
  );
}
