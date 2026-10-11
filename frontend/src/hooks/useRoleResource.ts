"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ApiError, currentUser, dashboardPath, type UserRole } from "@/lib/auth";

export default function useRoleResource<T>(
  role: UserRole,
  loadResource: () => Promise<T>,
): { data: T | null; error: string; loading: boolean } {
  const router = useRouter();
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const user = await currentUser();
        if (user.role !== role) {
          router.replace(dashboardPath(user.role));
          return;
        }
        const resource = await loadResource();
        if (active) setData(resource);
      } catch (reason: unknown) {
        if (!active) return;
        if (reason instanceof ApiError && reason.status === 401) {
          router.replace("/login");
          return;
        }
        setError(reason instanceof Error ? reason.message : "Unable to load this page.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [loadResource, role, router]);

  return { data, error, loading };
}
