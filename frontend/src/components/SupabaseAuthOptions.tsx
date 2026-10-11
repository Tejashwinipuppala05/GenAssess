"use client";

import { useState } from "react";
import type { UserRole } from "@/lib/auth";
import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";

export default function SupabaseAuthOptions({ role }: { role: UserRole }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const configured = isSupabaseConfigured();

  async function signInWithGoogle() {
    setError("");
    setLoading(true);
    try {
      const redirectTo = `${window.location.origin}/auth/callback?role=${role}`;
      const { error: authError } = await getSupabaseClient().auth.signInWithOAuth({
        provider: "google",
        options: { redirectTo },
      });
      if (authError) throw authError;
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to continue with Google.");
      setLoading(false);
    }
  }

  return (
    <section className="mt-7 border-t border-slate-200 pt-6">
      <p className="text-center text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        Or sign in with Google
      </p>
      {configured ? (
        <button
          className="mt-4 w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-800 transition hover:bg-slate-50 disabled:opacity-60"
          disabled={loading}
          onClick={signInWithGoogle}
          type="button"
        >
          {loading ? "Redirecting to Google..." : "Continue with Google"}
        </button>
      ) : (
        <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-900">
          Configure Google in Supabase to enable this option. Email and password sign-in is available now.
        </p>
      )}
      <p className="mt-3 text-center text-xs leading-5 text-slate-500">
        No paid SMS is used. Mobile numbers are optional contact details, not an authentication method.
      </p>
      {error && (
        <p aria-live="polite" className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}
    </section>
  );
}
