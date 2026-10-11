"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  pendingCompanyVerifications,
  reviewCompanyVerification,
  type AdminCompanyVerification,
} from "@/lib/auth";

export default function CompanyVerificationReviewPage() {
  const [items, setItems] = useState<AdminCompanyVerification[]>([]);
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState<number | null>(null);

  useEffect(() => {
    let active = true;
    pendingCompanyVerifications()
      .then((result) => {
        if (active) setItems(result);
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Unable to load company reviews.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function decide(userId: number, decision: "VERIFIED" | "REJECTED") {
    setError("");
    setReviewing(userId);
    try {
      await reviewCompanyVerification(userId, decision, notes[userId] || "");
      setItems((current) => current.filter((item) => item.userId !== userId));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to record the review.");
    } finally {
      setReviewing(null);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl px-5 py-10">
      <Link className="text-sm font-semibold text-indigo-700 hover:text-indigo-900" href="/">
        ← GenAssess
      </Link>
      <h1 className="mt-7 text-3xl font-semibold tracking-tight text-slate-950">Company verification reviews</h1>
      <p className="mt-2 text-sm text-slate-600">
        Manually verify the CIN against the{" "}
        <a className="text-indigo-700 underline" href="https://www.mca.gov.in/" rel="noreferrer" target="_blank">
          Ministry of Corporate Affairs
        </a>{" "}
        portal, or the GSTIN against the{" "}
        <a className="text-indigo-700 underline" href="https://www.gst.gov.in/" rel="noreferrer" target="_blank">
          GST portal
        </a>
        . Compare the registered business with the submitted website and LinkedIn page before deciding.
      </p>
      {error && <p aria-live="polite" className="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
      {loading ? (
        <p className="mt-7 text-sm text-slate-600">Loading review queue...</p>
      ) : items.length === 0 && !error ? (
        <p className="mt-7 rounded-lg bg-white p-6 text-sm text-slate-600">There are no pending company reviews.</p>
      ) : (
        <div className="mt-7 space-y-5">
          {items.map((item) => (
            <article key={item.userId} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-950">{item.companyName}</h2>
              <p className="mt-1 text-sm text-slate-600">
                Applicant: {item.userName} · {item.userEmail || item.userPhone || "No contact"}
              </p>
              <dl className="mt-5 grid gap-3 text-sm sm:grid-cols-2">
                <div><dt className="font-medium text-slate-500">{item.identifierType}</dt><dd className="mt-1 text-slate-900">{item.identifier}</dd></div>
                <div><dt className="font-medium text-slate-500">Registry result</dt><dd className="mt-1 text-slate-900">Manual check required</dd></div>
                {item.registryCompanyName && (
                  <div><dt className="font-medium text-slate-500">Registry company name</dt><dd className="mt-1 text-slate-900">{item.registryCompanyName}</dd></div>
                )}
                <div><dt className="font-medium text-slate-500">Submitted company name</dt><dd className="mt-1 text-slate-900">{item.companyName}</dd></div>
                <div><dt className="font-medium text-slate-500">Website</dt><dd className="mt-1 break-all"><a className="text-indigo-700 underline" href={item.websiteUrl} rel="noreferrer" target="_blank">{item.websiteUrl}</a></dd></div>
                <div><dt className="font-medium text-slate-500">LinkedIn</dt><dd className="mt-1 break-all"><a className="text-indigo-700 underline" href={item.linkedinUrl} rel="noreferrer" target="_blank">{item.linkedinUrl}</a></dd></div>
              </dl>
              <label className="mt-5 block text-sm font-medium text-slate-800">
                Review note (required)
                <textarea
                  className="mt-2 min-h-20 w-full rounded-lg border border-slate-300 px-3 py-2.5"
                  onChange={(event) => setNotes((current) => ({ ...current, [item.userId]: event.target.value }))}
                  value={notes[item.userId] || ""}
                />
              </label>
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  className="rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                  disabled={reviewing !== null}
                  onClick={() => void decide(item.userId, "VERIFIED")}
                  type="button"
                >
                  {reviewing === item.userId ? "Saving..." : "Approve company"}
                </button>
                <button
                  className="rounded-lg border border-red-300 px-4 py-2.5 text-sm font-semibold text-red-700 disabled:opacity-60"
                  disabled={reviewing !== null}
                  onClick={() => void decide(item.userId, "REJECTED")}
                  type="button"
                >
                  Reject
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
