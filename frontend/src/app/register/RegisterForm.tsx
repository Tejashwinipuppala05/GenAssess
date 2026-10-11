"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import AuthCard from "@/components/AuthCard";
import SupabaseAuthOptions from "@/components/SupabaseAuthOptions";
import { register, type UserRole } from "@/lib/auth";

export default function RegisterForm({ role }: { role: UserRole }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }
    if (password.length < 12) {
      setError("Use a password with at least 12 characters.");
      return;
    }

    setLoading(true);
    try {
      await register(name, email, password, role, phone || undefined);
      setSuccess(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create your account.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard
      eyebrow="Get started"
      title={role === "RECRUITER" ? "Create a hiring account" : "Create a job seeker account"}
      description={
        role === "RECRUITER"
          ? "Create your hiring account. Company verification is required before publishing jobs."
          : "Register to securely access your GenAssess job seeker workspace."
      }
    >
      {success ? (
        <div className="space-y-4">
          <p className="rounded-lg bg-emerald-50 px-3 py-3 text-sm text-emerald-800">
            Your account is ready. Sign in as {role === "RECRUITER" ? "a hiring team" : "a job seeker"} to continue.
          </p>
          <Link
            className="block w-full rounded-lg bg-indigo-700 px-4 py-3 text-center text-sm font-semibold text-white transition hover:bg-indigo-800"
            href={`/login?role=${role}`}
          >
            Continue to sign in
          </Link>
        </div>
      ) : (
        <form className="space-y-5" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-800">
            Name
            <input
              autoComplete="name"
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
              maxLength={100}
              name="name"
              onChange={(event) => setName(event.target.value)}
              required
              type="text"
              value={name}
            />
          </label>
          <label className="block text-sm font-medium text-slate-800">
            Mobile number <span className="font-normal text-slate-500">(optional)</span>
            <input
              autoComplete="tel"
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
              name="phone"
              onChange={(event) => setPhone(event.target.value)}
              placeholder="+91 98765 43210"
              type="tel"
              value={phone}
            />
            <span className="mt-1 block text-xs font-normal text-slate-500">
              Contact detail only; we will not send paid SMS verification codes.
            </span>
          </label>
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
              autoComplete="new-password"
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
              minLength={12}
              name="password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
            <span className="mt-1 block text-xs font-normal text-slate-500">
              Use at least 12 characters.
            </span>
          </label>
          <label className="block text-sm font-medium text-slate-800">
            Confirm password
            <input
              autoComplete="new-password"
              className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100"
              name="confirmPassword"
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              type="password"
              value={confirmPassword}
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
            {loading ? "Creating account..." : role === "RECRUITER" ? "Create hiring account" : "Create account"}
          </button>
        </form>
      )}
      {!success && <SupabaseAuthOptions role={role} />}
      <p className="mt-6 text-center text-sm text-slate-600">
        Already registered?{" "}
        <Link className="font-semibold text-indigo-700 hover:text-indigo-900" href={`/login?role=${role}`}>
          Sign in
        </Link>
      </p>
      <p className="mt-3 text-center text-xs text-slate-500">
        {role === "RECRUITER" ? "Hiring team" : "Job seeker"} account?{" "}
        <Link
          className="font-semibold text-indigo-700 hover:text-indigo-900"
          href={`/register?role=${role === "RECRUITER" ? "CANDIDATE" : "RECRUITER"}`}
        >
          Switch account type
        </Link>
      </p>
    </AuthCard>
  );
}
