"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";
import { logout, type User, type UserRole } from "@/lib/auth";

const navigationByRole: Record<UserRole, Array<{ label: string; href: string; icon: string }>> = {
  CANDIDATE: [
    { label: "Overview", href: "/candidate/dashboard", icon: "grid" },
    { label: "Practice", href: "/candidate/practice", icon: "target" },
    { label: "Practice history", href: "/candidate/practice/history", icon: "history" },
  ],
  RECRUITER: [
    { label: "Overview", href: "/recruiter/dashboard", icon: "grid" },
    { label: "Company profile", href: "/recruiter/company-verification", icon: "building" },
    { label: "Post a job", href: "/recruiter/jobs/new", icon: "plus" },
    { label: "Applicants", href: "/recruiter/applicants", icon: "users" },
  ],
};

function NavigationIcon({ name }: { name: string }) {
  const paths: Record<string, ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></>,
    target: <><circle cx="12" cy="12" r="8.5" /><circle cx="12" cy="12" r="4.5" /><circle cx="12" cy="12" r="1" /></>,
    building: <><path d="M4 21V5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v16M2 21h20M8 8h4M8 12h4M8 16h4M16 10h2M16 14h2M16 18h2" /></>,
    plus: <><path d="M12 5v14M5 12h14" /></>,
    history: <><path d="M3 12a9 9 0 1 0 2.64-6.36L3 8" /><path d="M3 3v5h5M12 7v5l3 2" /></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM20 8v6M23 11h-6" /></>,
  };

  return (
    <svg aria-hidden="true" className="h-[18px] w-[18px]" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.7" viewBox="0 0 24 24">
      {paths[name]}
    </svg>
  );
}

export function DashboardFrame({
  user,
  role,
  children,
}: {
  user: User;
  role: UserRole;
  children: ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [error, setError] = useState("");
  const [signingOut, setSigningOut] = useState(false);
  const isAssessment = pathname.includes("/aptitude/test");
  const navigation = navigationByRole[role];
  const initials = user.name
    .split(/\s+/)
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  async function handleLogout() {
    setSigningOut(true);
    setError("");
    try {
      await logout();
      router.replace("/");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign out.");
      setSigningOut(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f5f6fa] text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        {!isAssessment && (
          <aside className="hidden w-[248px] shrink-0 border-r border-slate-200/80 bg-white px-5 py-6 lg:flex lg:flex-col">
            <Link className="flex items-center gap-3 px-2" href="/">
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-indigo-600 text-sm font-black text-white shadow-md shadow-indigo-200">G</span>
              <span className="text-[15px] font-extrabold tracking-[0.13em] text-slate-900">GENASSESS</span>
            </Link>
            <div className="mt-10 px-3">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Workspace</p>
              <p className="mt-2 text-sm font-semibold text-slate-700">{role === "CANDIDATE" ? "Candidate portal" : "Hiring workspace"}</p>
            </div>
            <nav aria-label="Main navigation" className="mt-5 space-y-1.5">
              {navigation.map((item) => {
                const active = pathname === item.href || (item.href !== "/candidate/dashboard" && item.href !== "/recruiter/dashboard" && pathname.startsWith(item.href));
                return (
                  <Link
                    aria-current={active ? "page" : undefined}
                    className={`flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-semibold transition ${
                      active
                        ? "bg-indigo-50 text-indigo-700"
                        : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                    href={item.href}
                    key={item.href}
                  >
                    <NavigationIcon name={item.icon} />
                    {item.label}
                    {active && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-600" />}
                  </Link>
                );
              })}
            </nav>
            <div className="mt-auto rounded-2xl bg-slate-50 p-4">
              <p className="text-xs font-bold text-slate-800">Your next step</p>
              <p className="mt-1.5 text-xs leading-5 text-slate-500">
                {role === "CANDIDATE" ? "Build confidence one practice round at a time." : "Set up your company profile to get started."}
              </p>
            </div>
          </aside>
        )}
        <div className="min-w-0 flex-1">
          <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
            <div className="flex min-h-[68px] items-center justify-between gap-4 px-5 sm:px-8">
              <div className="flex min-w-0 items-center gap-3">
                {isAssessment ? (
                  <Link aria-label="GenAssess home" className="grid h-9 w-9 place-items-center rounded-xl bg-indigo-600 text-sm font-black text-white lg:hidden" href="/">G</Link>
                ) : (
                  <Link className="flex items-center gap-2.5 lg:hidden" href="/">
                    <span className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 text-xs font-black text-white">G</span>
                    <span className="text-xs font-extrabold tracking-[0.12em] text-slate-900">GENASSESS</span>
                  </Link>
                )}
                <div className="hidden sm:block">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
                    {role === "CANDIDATE" ? "Candidate workspace" : "Recruiter workspace"}
                  </p>
                  <p className="mt-0.5 text-sm font-semibold text-slate-800">
                    {isAssessment ? "Aptitude assessment" : pathname.includes("/practice") ? "Practice & preparation" : "Overview"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="hidden items-center gap-2.5 border-r border-slate-200 pr-4 sm:flex">
                  <span className="grid h-8 w-8 place-items-center rounded-full bg-indigo-100 text-[11px] font-bold text-indigo-700">{initials}</span>
                  <div>
                    <p className="max-w-40 truncate text-xs font-semibold text-slate-800">{user.name}</p>
                    <p className="text-[10px] text-slate-500">{role === "CANDIDATE" ? "Job seeker" : "Hiring team"}</p>
                  </div>
                </div>
                <button
                  className="rounded-lg px-3 py-2 text-xs font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 disabled:opacity-60"
                  disabled={signingOut}
                  onClick={handleLogout}
                  type="button"
                >
                  {signingOut ? "Signing out..." : "Sign out"}
                </button>
              </div>
            </div>
            {!isAssessment && (
              <nav aria-label="Mobile navigation" className="flex gap-2 overflow-x-auto border-t border-slate-100 px-5 py-2.5 lg:hidden">
                {navigation.map((item) => {
                  const active = pathname === item.href || (item.href !== "/candidate/dashboard" && item.href !== "/recruiter/dashboard" && pathname.startsWith(item.href));
                  return (
                    <Link className={`shrink-0 rounded-lg px-3 py-2 text-xs font-semibold ${active ? "bg-indigo-50 text-indigo-700" : "text-slate-500 hover:bg-slate-50"}`} href={item.href} key={item.href}>
                      {item.label}
                    </Link>
                  );
                })}
              </nav>
            )}
          </header>
          <div className="mx-auto max-w-[1320px] px-5 py-7 sm:px-8 sm:py-9 xl:px-10">
            {error && (
              <p aria-live="polite" className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </p>
            )}
            {children}
          </div>
        </div>
      </div>
    </main>
  );
}

export function StatCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <article className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_2px_12px_rgba(15,23,42,0.035)] transition hover:-translate-y-0.5 hover:shadow-[0_10px_30px_rgba(15,23,42,0.07)]">
      <p className="text-xs font-semibold text-slate-500">{label}</p>
      <p className="mt-3 text-[28px] font-bold tracking-tight text-slate-950">{value}</p>
      <p className="mt-1.5 text-xs leading-5 text-slate-500">{detail}</p>
    </article>
  );
}

export function DashboardPanel({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_2px_12px_rgba(15,23,42,0.035)] sm:p-6">
      <div>
        <h2 className="text-[15px] font-bold text-slate-950">{title}</h2>
        {description && <p className="mt-1 text-sm text-slate-500">{description}</p>}
      </div>
      <div className="mt-5">{children}</div>
    </section>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <p className="rounded-xl border border-dashed border-slate-300 bg-slate-50/80 px-4 py-6 text-center text-sm leading-6 text-slate-600">
      {children}
    </p>
  );
}

export function DashboardLoading() {
  return (
    <main aria-label="Loading your workspace" className="min-h-screen bg-[#f5f6fa] p-6 sm:p-10">
      <div className="mx-auto max-w-6xl animate-pulse">
        <div className="h-5 w-36 rounded bg-slate-200" />
        <div className="mt-8 h-44 rounded-3xl bg-slate-200" />
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="h-28 rounded-2xl bg-slate-200" />
          <div className="h-28 rounded-2xl bg-slate-200" />
          <div className="h-28 rounded-2xl bg-slate-200" />
        </div>
        <p className="mt-8 text-center text-xs font-medium text-slate-500">Preparing your workspace…</p>
      </div>
    </main>
  );
}

export function DashboardError({ message }: { message: string }) {
  return (
    <main className="mx-auto mt-12 max-w-xl rounded-xl border border-red-200 bg-white p-6 text-sm text-red-700">
      {message}
    </main>
  );
}
