import RegisterForm from "./RegisterForm";
import type { UserRole } from "@/lib/auth";

export default async function RegisterPage({
  searchParams,
}: {
  searchParams: Promise<{ role?: string }>;
}) {
  const { role: requestedRole } = await searchParams;
  const role: UserRole = requestedRole === "RECRUITER" ? "RECRUITER" : "CANDIDATE";
  return <RegisterForm role={role} />;
}
