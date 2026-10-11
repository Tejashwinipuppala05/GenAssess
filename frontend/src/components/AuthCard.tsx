import type { ReactNode } from "react";
import Link from "next/link";

export default function AuthCard({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-12">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <Link href="/" className="text-sm font-bold tracking-[0.18em] text-indigo-700">
          GENASSESS
        </Link>
        <p className="mt-10 text-xs font-semibold uppercase tracking-[0.16em] text-indigo-700">
          {eyebrow}
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{title}</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
        <div className="mt-8">{children}</div>
      </section>
    </main>
  );
}
