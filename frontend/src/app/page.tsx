import Link from "next/link";

const paths = {
  candidate: { role: "CANDIDATE", label: "I'm looking for a job", detail: "Practice interviews and prepare for your next role." },
  recruiter: { role: "RECRUITER", label: "I'm hiring", detail: "Prepare your team to assess candidates with confidence." },
} as const;

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-12">
      <section className="w-full max-w-4xl">
        <p className="text-center text-sm font-bold tracking-[0.2em] text-indigo-700">GENASSESS</p>
        <h1 className="mt-8 text-center text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
          What brings you to GenAssess?
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-center text-sm leading-6 text-slate-600">
          Choose how you’ll use GenAssess. You can create an account or sign in on the next step.
        </p>
        <div className="mt-9 grid gap-5 sm:grid-cols-2">
          {Object.entries(paths).map(([key, option]) => (
            <article key={key} className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
              <h2 className="text-xl font-semibold text-slate-950">{option.label}</h2>
              <p className="mt-2 min-h-12 text-sm leading-6 text-slate-600">{option.detail}</p>
              <div className="mt-6 grid gap-3 sm:grid-cols-2">
                <Link
                  className="rounded-lg bg-indigo-700 px-4 py-3 text-center text-sm font-semibold text-white transition hover:bg-indigo-800"
                  href={`/register?role=${option.role}`}
                >
                  Create account
                </Link>
                <Link
                  className="rounded-lg border border-slate-300 px-4 py-3 text-center text-sm font-semibold text-slate-800 transition hover:bg-slate-50"
                  href={`/login?role=${option.role}`}
                >
                  Sign in
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
