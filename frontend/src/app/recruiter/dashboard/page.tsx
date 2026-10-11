"use client";

import Link from "next/link";
import { DashboardError, DashboardFrame, DashboardLoading, DashboardPanel, EmptyState, StatCard } from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import { recruiterDashboard, recruiterJobs, type JobPost, type RecruiterDashboard } from "@/lib/auth";

async function loadRecruiterWorkspace() {
  const [dashboard, jobs] = await Promise.all([recruiterDashboard(), recruiterJobs()]);
  return { dashboard, jobs };
}

export default function RecruiterDashboardPage() {
  const { data, error, loading } = useRoleResource<{
    dashboard: RecruiterDashboard;
    jobs: JobPost[];
  }>("RECRUITER", loadRecruiterWorkspace);

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to load your dashboard."} />;

  const { dashboard, jobs } = data;

  return (
    <DashboardFrame role="RECRUITER" user={dashboard.user}>
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">
            Hiring workspace
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
            Welcome,             {dashboard.user.name}
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Manage interviews and review candidate outcomes from one place.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            className="inline-flex items-center justify-center rounded-lg bg-indigo-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-800"
            href="/recruiter/interviews/new"
          >
            Create Interview
          </Link>
          <Link
            className="inline-flex items-center justify-center rounded-lg border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-800 transition hover:bg-slate-50"
            href="/recruiter/jobs/new"
          >
            Post a job
          </Link>
        </div>
      </div>
      <Link
        className="mt-5 block rounded-xl border border-indigo-200 bg-indigo-50 px-5 py-4 text-sm text-indigo-950 transition hover:bg-indigo-100"
        href="/recruiter/company-verification"
      >
        <span className="font-semibold">Company verification</span>
        <span className="mt-1 block text-indigo-800">
          Submit your company details for manual verification before job publishing is enabled.
        </span>
      </Link>
      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          href="/recruiter/applicants"
        >
          View applicants
        </Link>
        <Link
          className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          href="/recruiter/evaluation"
        >
          Candidate evaluation
        </Link>
      </div>

      <section className="mt-8 grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Total interviews"
          value={dashboard.statistics.totalInterviews}
          detail="Interviews created by your account"
        />
        <StatCard
          label="Candidates evaluated"
          value={dashboard.statistics.candidatesEvaluated}
          detail="Candidates with completed assessments"
        />
        <StatCard
          label="Average score"
          value={dashboard.statistics.averageScore === null ? "—" : `${dashboard.statistics.averageScore}%`}
          detail="Across completed candidate assessments"
        />
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <DashboardPanel title="Your job posts">
          {jobs.length ? (
            <div className="space-y-3">
              {jobs.map((job) => (
                <div key={job.id} className="rounded-lg bg-slate-50 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-900">{job.title}</p>
                  <p className="mt-1 text-xs text-slate-600">
                    {job.location} · {job.workArrangement.toLowerCase()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState>No jobs published yet.</EmptyState>
          )}
        </DashboardPanel>
        <DashboardPanel title="Recruiter & company information">
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-slate-50 px-4 py-4">
            <span className="text-sm text-slate-600">Account</span>
            <span className="text-sm font-semibold text-slate-900">{dashboard.user.email || dashboard.user.phone || "—"}</span>
          </div>
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-lg bg-slate-50 px-4 py-4">
            <span className="text-sm text-slate-600">Company</span>
            <span className="text-sm font-semibold text-slate-900">{dashboard.company.name || "Not provided"}</span>
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-500">
            Company profile settings will be available in a later update.
          </p>
        </DashboardPanel>

        <DashboardPanel title="Created interviews">
          {dashboard.createdInterviews.length ? (
            <div className="space-y-3">
              {dashboard.createdInterviews.map((interview, index) => (
                <p key={index} className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-700">
                  {JSON.stringify(interview)}
                </p>
              ))}
            </div>
          ) : (
            <EmptyState>No interviews have been created yet. Interview creation is a future feature.</EmptyState>
          )}
        </DashboardPanel>

        <div className="lg:col-span-2">
          <DashboardPanel title="Candidate results">
            {dashboard.candidateResults.length ? (
              <div className="space-y-3">
                {dashboard.candidateResults.map((candidate, index) => (
                  <p key={index} className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    {JSON.stringify(candidate)}
                  </p>
                ))}
              </div>
            ) : (
              <EmptyState>Candidate results will appear here after recruiter interviews are available.</EmptyState>
            )}
          </DashboardPanel>
        </div>
      </div>
    </DashboardFrame>
  );
}
