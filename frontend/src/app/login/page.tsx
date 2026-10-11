import LoginForm from "./LoginForm";
import type { UserRole } from "@/lib/auth";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ role?: string }>;
}) {
  const { role: requestedRole } = await searchParams;
  const role: UserRole = requestedRole === "RECRUITER" ? "RECRUITER" : "CANDIDATE";
  return <LoginForm role={role} />;
}
