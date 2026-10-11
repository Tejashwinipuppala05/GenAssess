"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, currentUser, dashboardPath } from "@/lib/auth";

export default function DashboardRedirectPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    currentUser()
      .then((user) => {
        if (active) router.replace(dashboardPath(user.role));
      })
      .catch((reason: unknown) => {
        if (!active) return;
        if (reason instanceof ApiError && reason.status === 401) {
          router.replace("/login");
          return;
        }
        setError(reason instanceof Error ? reason.message : "Unable to identify your account.");
      });
    return () => {
      active = false;
    };
  }, [router]);

  return (
    <main className="p-8 text-center text-sm text-slate-600">
      {error || "Opening your GenAssess workspace..."}
    </main>
  );
}
