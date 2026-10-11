"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { dashboardPath, exchangeSupabaseToken, type UserRole } from "@/lib/auth";
import { getSupabaseClient } from "@/lib/supabase";

export default function AuthCallbackPage() {
  const router = useRouter();
  const started = useRef(false);
  const [error, setError] = useState("");
  const [role, setRole] = useState<UserRole>("CANDIDATE");

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    async function completeSignIn() {
      const params = new URLSearchParams(window.location.search);
      const requestedRole = params.get("role");
      const selectedRole =
        requestedRole === "RECRUITER" || requestedRole === "CANDIDATE"
          ? requestedRole
          : "CANDIDATE";
      setRole(selectedRole);

      try {
        const supabase = getSupabaseClient();
        const code = params.get("code");
        if (code) {
          const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
          if (exchangeError) throw exchangeError;
        }
        const { data, error: sessionError } = await supabase.auth.getSession();
        if (sessionError) throw sessionError;
        if (!data.session) throw new Error("Google did not return a sign-in session.");
        const result = await exchangeSupabaseToken(data.session.access_token, selectedRole);
        router.replace(dashboardPath(result.user.role));
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : "Unable to complete sign-in.");
      }
    }

    void completeSignIn();
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-12">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-sm font-bold tracking-[0.18em] text-indigo-700">GENASSESS</p>
        {error ? (
          <>
            <h1 className="mt-8 text-xl font-semibold text-slate-950">Sign-in could not be completed</h1>
            <p aria-live="polite" className="mt-3 text-sm text-red-700">{error}</p>
            <Link className="mt-6 inline-block font-semibold text-indigo-700" href={`/login?role=${role}`}>
              Return to sign in
            </Link>
          </>
        ) : (
          <p className="mt-8 text-sm text-slate-600">Finishing your secure sign-in...</p>
        )}
      </section>
    </main>
  );
}
