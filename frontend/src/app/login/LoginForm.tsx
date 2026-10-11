"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";
import AuthCard from "@/components/AuthCard";
import SupabaseAuthOptions from "@/components/SupabaseAuthOptions";
import { dashboardPath, login, type UserRole } from "@/lib/auth";

export default function LoginForm({ role }: { role: UserRole }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(email, password);
      router.replace(dashboardPath(result.user.role));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard
      eyebrow="Welcome back"
      title={role === "RECRUITER" ? "Sign in to your hiring account" : "Sign in to your job seeker account"}
      description="Use your account to continue to your GenAssess workspace."
    >
      <form className="space-y-5" onSubmit={handleSubmit}>
        <label className="block text-sm font-medium text-slate-800">
          Email
          <input
            autoComplete="email"
            className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
            name="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>
        <label className="block text-sm font-medium text-slate-800">
          Password
          <input
            autoComplete="current-password"
            className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
        </label>
        {error && (
          <p aria-live="polite" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}
        <button
          className="w-full rounded-lg bg-indigo-700 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-800 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={loading}
          type="submit"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
      <SupabaseAuthOptions role={role} />
      <p className="mt-6 text-center text-sm text-slate-600">
        New to GenAssess?{" "}
        <Link className="font-semibold text-indigo-700 hover:text-indigo-900" href={`/register?role=${role}`}>
          Create an account
        </Link>
      </p>
      <p className="mt-3 text-center text-xs text-slate-500">
        Not here to {role === "RECRUITER" ? "hire" : "look for a job"}?{" "}
        <Link
          className="font-semibold text-indigo-700 hover:text-indigo-900"
          href={`/login?role=${role === "RECRUITER" ? "CANDIDATE" : "RECRUITER"}`}
        >
          Switch account type
        </Link>
      </p>
    </AuthCard>
  );
}
