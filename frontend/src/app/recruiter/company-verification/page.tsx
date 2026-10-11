"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { DashboardError, DashboardFrame, DashboardLoading } from "@/components/dashboard/DashboardUI";
import useRoleResource from "@/hooks/useRoleResource";
import {
  ApiError,
  companyVerification,
  recruiterDashboard,
  submitCompanyVerification,
  type CompanyVerification,
  type RecruiterDashboard,
} from "@/lib/auth";

export default function CompanyVerificationPage() {
  const { data, error, loading } = useRoleResource<RecruiterDashboard>(
    "RECRUITER",
    recruiterDashboard,
  );

  if (loading) return <DashboardLoading />;
  if (error || !data) return <DashboardError message={error || "Unable to verify recruiter access."} />;

  return <CompanyVerificationForm user={data.user} />;
}

function CompanyVerificationForm({ user }: { user: RecruiterDashboard["user"] }) {
  const [verification, setVerification] = useState<CompanyVerification | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [identifierType, setIdentifierType] = useState<"CIN" | "GSTIN">("CIN");
  const [identifier, setIdentifier] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    companyVerification()
      .then((result) => {
        if (!active) return;
        setVerification(result);
        setCompanyName(result.companyName);
        setIdentifierType(result.identifierType);
        setIdentifier(
          result.status === "REJECTED" || result.status === "REGISTRY_FAILED" ? "" : result.identifier,
        );
        setWebsiteUrl(result.websiteUrl);
        setLinkedinUrl(result.linkedinUrl);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        if (!(reason instanceof ApiError && reason.status === 404)) {
          setError(reason instanceof Error ? reason.message : "Unable to load company verification.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const result = await submitCompanyVerification({
        companyName,
        identifierType,
        identifier,
        websiteUrl,
        linkedinUrl,
      });
      setVerification(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to submit company verification.");
    } finally {
      setSubmitting(false);
    }
  }

  const editable = !verification || verification.status === "REJECTED" || verification.status === "REGISTRY_FAILED";

  return (
    <DashboardFrame role="RECRUITER" user={user}>
      <div className="mx-auto max-w-3xl">
        <Link className="text-sm font-semibold text-indigo-700 hover:text-indigo-900" href="/recruiter/dashboard">
          ← Hiring dashboard
        </Link>
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-9">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">Hiring account</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">Verify your company</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
        Submit your CIN or GSTIN plus your company website and LinkedIn page. An admin will manually check the
        registration on the official registry and review the company links. Job publishing stays locked until approval.
        </p>

        {loading ? (
          <p className="mt-7 text-sm text-slate-600">Loading verification status...</p>
        ) : verification ? (
          <div className="mt-6 rounded-lg bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-900">
              Status: {verification.status.replaceAll("_", " ")}
            </p>
            <p className="mt-2 text-sm text-slate-700">
              Registry result: {verification.registryStatus}
              {verification.registryCompanyName ? ` — ${verification.registryCompanyName}` : ""}
            </p>
            <p className="mt-1 text-sm text-slate-600">
              Identifier: {verification.identifierType} {verification.identifier}
            </p>
            {verification.reviewerNote && (
              <p className="mt-2 text-sm text-slate-700">Reviewer note: {verification.reviewerNote}</p>
            )}
          </div>
        ) : null}

        {verification?.status === "PENDING_REVIEW" && (
          <p className="mt-5 rounded-lg bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
            Your submission is waiting for manual review. No paid registry lookup was used.
          </p>
        )}
        {verification?.status === "VERIFIED" && (
          <p className="mt-5 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
            Your company is verified. Job publishing can now be enabled for this account.
          </p>
        )}
        {verification?.status === "REGISTRY_FAILED" && (
          <p className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">
            The previous review could not verify your details. Check the CIN/GSTIN and submit again.
          </p>
        )}
        {error && (
          <p aria-live="polite" className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </p>
        )}

        {!loading && editable && (
          <form className="mt-7 space-y-5" onSubmit={handleSubmit}>
            <label className="block text-sm font-medium text-slate-800">
              Registered company name
              <input
                autoComplete="organization"
                className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
                maxLength={200}
                onChange={(event) => setCompanyName(event.target.value)}
                required
                value={companyName}
              />
            </label>
            <div className="grid gap-4 sm:grid-cols-[140px_1fr]">
              <label className="block text-sm font-medium text-slate-800">
                Registry ID
                <select
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5"
                  onChange={(event) => setIdentifierType(event.target.value as "CIN" | "GSTIN")}
                  value={identifierType}
                >
                  <option value="CIN">CIN</option>
                  <option value="GSTIN">GSTIN</option>
                </select>
              </label>
              <label className="block text-sm font-medium text-slate-800">
                {identifierType}
                <input
                  autoComplete="off"
                  className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 uppercase outline-none focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
                  maxLength={identifierType === "CIN" ? 21 : 15}
                  minLength={identifierType === "CIN" ? 21 : 15}
                  onChange={(event) => setIdentifier(event.target.value.toUpperCase())}
                  required
                  value={identifier}
                />
              </label>
            </div>
            <label className="block text-sm font-medium text-slate-800">
              Company website
              <input
                className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
                onChange={(event) => setWebsiteUrl(event.target.value)}
                placeholder="https://example.com"
                required
                type="url"
                value={websiteUrl}
              />
            </label>
            <label className="block text-sm font-medium text-slate-800">
              Company LinkedIn page
              <input
                className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
                onChange={(event) => setLinkedinUrl(event.target.value)}
                placeholder="https://www.linkedin.com/company/example"
                required
                type="url"
                value={linkedinUrl}
              />
            </label>
            <button
              className="w-full rounded-lg bg-indigo-700 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-800 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={submitting}
              type="submit"
            >
              {submitting ? "Checking company registry..." : "Verify and submit for review"}
            </button>
          </form>
        )}
        </section>
      </div>
    </DashboardFrame>
  );
}
