import Link from "next/link";
import AptitudeTest from "./AptitudeTest";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function AptitudeTestPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const value = params.sessionId;
  const sessionId = Array.isArray(value) ? value[0] : value;

  if (!sessionId) {
    return (
      <main className="mx-auto mt-12 max-w-xl rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-700 shadow-sm">
        <p>This test link is missing its session. Return to practice and start a test.</p>
        <div className="mt-5 flex flex-wrap gap-4">
          <Link className="font-semibold text-indigo-700 hover:text-indigo-900" href="/candidate/practice">Practice setup</Link>
          <Link className="font-semibold text-slate-600 hover:text-slate-900" href="/candidate/dashboard">Candidate dashboard</Link>
        </div>
      </main>
    );
  }

  return <AptitudeTest sessionId={sessionId} />;
}
