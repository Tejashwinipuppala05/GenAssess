"use client";

import Link from "next/link";
import {
  DashboardError,
  DashboardFrame,
  DashboardLoading,
  DashboardPanel,
} from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import {
  recruiterDashboard,
  type RecruiterDashboard,
} from "@/lib/auth";

export default function RecruiterComingSoon({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  const { data, error, loading } = useRoleResource<RecruiterDashboard>(
    "RECRUITER",
    recruiterDashboard,
  );

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load this recruiter page."} />;

  return (
    <DashboardFrame role="RECRUITER" user={data.user}>
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">Hiring workspace</p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{title}</h1>
      <div className="mt-8 max-w-2xl">
        <DashboardPanel title="Coming soon">
          <div className="space-y-5">
            <p className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-center text-sm leading-6 text-slate-600">
              {description}
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                className="rounded-lg bg-indigo-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-800"
                href="/recruiter/dashboard"
              >
                Back to dashboard
              </Link>
              <Link
                className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                href="/recruiter/jobs/new"
              >
                Post a job
              </Link>
              <Link
                className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                href={title === "Applicants" ? "/recruiter/evaluation" : "/recruiter/applicants"}
              >
                {title === "Applicants" ? "Candidate evaluation" : "Applicants"}
              </Link>
            </div>
          </div>
        </DashboardPanel>
      </div>
    </DashboardFrame>
  );
}
