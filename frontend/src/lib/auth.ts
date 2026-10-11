export type User = {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  role: UserRole;
  createdAt: string;
  updatedAt: string;
};

export type UserRole = "CANDIDATE" | "RECRUITER";

type LoginResult = {
  user: User;
  expiresAt: string;
};

export type CandidateDashboard = {
  user: User;
  profile: { targetRole: string | null };
  previousAttempts: unknown[];
  performance: { interviewsCompleted: number; overallScore: number | null };
  recentResults: unknown[];
  skillOverview: unknown[];
};

export type RecruiterDashboard = {
  user: User;
  company: { name: string | null };
  statistics: {
    totalInterviews: number;
    candidatesEvaluated: number;
    averageScore: number | null;
  };
  createdInterviews: unknown[];
  candidateResults: unknown[];
};

export type PlaceholderResponse = { message: string; user: User };

export type CompanyVerification = {
  companyName: string;
  identifierType: "CIN" | "GSTIN";
  identifier: string;
  websiteUrl: string;
  linkedinUrl: string;
  registryStatus: string;
  registryCompanyName: string | null;
  status: "PENDING_REVIEW" | "VERIFIED" | "REJECTED" | "REGISTRY_FAILED";
  reviewerNote: string | null;
  reviewedAt: string | null;
  updatedAt: string;
};

export type AdminCompanyVerification = CompanyVerification & {
  userId: number;
  userName: string;
  userEmail: string | null;
  userPhone: string | null;
};

export type JobPost = {
  id: number;
  title: string;
  description: string;
  location: string;
  workArrangement: "REMOTE" | "HYBRID" | "ONSITE";
  createdAt: string;
};

export type AptitudeSessionConfig = {
  questionCount: number;
  estimatedDurationSeconds: number;
  categoryCounts: Record<string, number>;
  difficultyDistribution: Record<string, number>;
  categories: string[];
};

export type AptitudeQuestion = {
  id: string;
  question: string;
  options: string[];
  topic: string;
  subtopic: string;
  category: string;
  difficulty: "Easy" | "Medium" | "Hard";
  estimatedTimeSeconds: number;
  sourceType: string;
  tags: string[];
  selectedAnswer: number | null;
  markedForReview: boolean;
};

export type AptitudeSession = {
  id: string;
  status: "IN_PROGRESS" | "COMPLETED";
  targetRole: string;
  companyType: string | null;
  experienceLevel: "Fresher" | "Experienced";
  startedAt: number;
  expiresAt: number;
  serverTime: number;
  durationSeconds: number;
  totalQuestions: number;
  questions: AptitudeQuestion[];
};

export type AptitudeHistoryItem = {
  sessionId: string;
  targetRole: string;
  companyType: string | null;
  experienceLevel: "Fresher" | "Experienced";
  status: "IN_PROGRESS" | "COMPLETED";
  startedAt: number;
  totalQuestions: number;
  correctAnswers: number | null;
  accuracy: number | null;
  timeTakenSeconds: number | null;
};

export type AptitudePerformance = {
  total: number;
  correct: number;
  incorrect: number;
  unanswered: number;
  accuracy: number;
};

export type AptitudeResult = {
  sessionId: string;
  targetRole: string;
  companyType: string | null;
  experienceLevel: "Fresher" | "Experienced";
  totalQuestions: number;
  correctAnswers: number;
  incorrectAnswers: number;
  unansweredQuestions: number;
  score: number;
  accuracy: number;
  timeTakenSeconds: number;
  durationSeconds: number;
  completedAt: number;
  categoryPerformance: Array<AptitudePerformance & { category: string }>;
  topicPerformance: Array<AptitudePerformance & { topic: string; category: string }>;
  difficultyPerformance: Array<AptitudePerformance & { difficulty: string }>;
  strongTopics: string[];
  weakTopics: string[];
  recommendation: string;
  answers: Array<{
    questionId: string;
    question: string;
    options: string[];
    selectedAnswer: number | null;
    correctAnswer: number;
    isCorrect: boolean | null;
    explanation: string;
    topic: string;
    subtopic: string;
    category: string;
    difficulty: string;
  }>;
};

type ApiErrorBody = {
  detail?: string | Array<{ msg?: string; loc?: Array<string | number> }>;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function dashboardPath(role: UserRole): string {
  return role === "RECRUITER" ? "/recruiter/dashboard" : "/candidate/dashboard";
}

const apiUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    const headers = new Headers(init?.headers);
    if (init?.body !== undefined && init.body !== null) {
      headers.set("Content-Type", "application/json");
    }
    response = await fetch(`${apiUrl}${path}`, {
      ...init,
      credentials: "include",
      headers,
    });
  } catch {
    throw new Error("Cannot reach GenAssess authentication. Check that the backend is running.");
  }

  let body: ApiErrorBody;
  try {
    body = (await response.json()) as ApiErrorBody;
  } catch {
    throw new ApiError("The authentication service returned an unreadable response.", response.status);
  }

  if (!response.ok) {
    const detail = body.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg || "Invalid input").join(" ")
          : "The request could not be completed.";
    throw new ApiError(message, response.status);
  }

  return body as T;
}

export function register(
  name: string,
  email: string,
  password: string,
  role: UserRole,
  phone?: string,
): Promise<User> {
  return request<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password, role, phone }),
  });
}

export function exchangeSupabaseToken(accessToken: string, role: UserRole): Promise<LoginResult> {
  return request<LoginResult>("/auth/supabase/exchange", {
    method: "POST",
    body: JSON.stringify({ access_token: accessToken, role }),
  });
}

export function login(email: string, password: string): Promise<LoginResult> {
  return request<LoginResult>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function currentUser(): Promise<User> {
  return request<User>("/auth/me");
}

export function candidateDashboard(): Promise<CandidateDashboard> {
  return request<CandidateDashboard>("/candidate/dashboard");
}

export function recruiterDashboard(): Promise<RecruiterDashboard> {
  return request<RecruiterDashboard>("/recruiter/dashboard");
}

export function candidateInterviewSetup(): Promise<PlaceholderResponse> {
  return request<PlaceholderResponse>("/candidate/interview/setup");
}

export function aptitudeSessionConfig(): Promise<AptitudeSessionConfig> {
  return request<AptitudeSessionConfig>("/candidate/practice/aptitude/config");
}

export function aptitudeHistory(): Promise<AptitudeHistoryItem[]> {
  return request<AptitudeHistoryItem[]>("/candidate/practice/aptitude/sessions");
}

export function createAptitudeSession(input: {
  targetRole: string;
  companyType: string | null;
  experienceLevel: "Fresher" | "Experienced";
}): Promise<AptitudeSession> {
  return request<AptitudeSession>("/candidate/practice/aptitude/sessions", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getAptitudeSession(sessionId: string): Promise<AptitudeSession> {
  return request<AptitudeSession>(`/candidate/practice/aptitude/sessions/${encodeURIComponent(sessionId)}`);
}

export function saveAptitudeAnswer(
  sessionId: string,
  questionId: string,
  input: { selectedAnswer: number | null; markedForReview: boolean },
): Promise<{ saved: boolean }> {
  return request<{ saved: boolean }>(
    `/candidate/practice/aptitude/sessions/${encodeURIComponent(sessionId)}/answers/${encodeURIComponent(questionId)}`,
    { method: "PUT", body: JSON.stringify(input) },
  );
}

export function submitAptitudeSession(sessionId: string): Promise<AptitudeResult> {
  return request<AptitudeResult>(
    `/candidate/practice/aptitude/sessions/${encodeURIComponent(sessionId)}/submit`,
    { method: "POST" },
  );
}

export function getAptitudeResult(sessionId: string): Promise<AptitudeResult> {
  return request<AptitudeResult>(
    `/candidate/practice/aptitude/sessions/${encodeURIComponent(sessionId)}/result`,
  );
}

export function recruiterInterviewSetup(): Promise<PlaceholderResponse> {
  return request<PlaceholderResponse>("/recruiter/interviews/new");
}

export function logout(): Promise<{ message: string }> {
  return request<{ message: string }>("/auth/logout", { method: "POST" });
}

export function companyVerification(): Promise<CompanyVerification> {
  return request<CompanyVerification>("/recruiter/company-verification");
}

export function submitCompanyVerification(input: {
  companyName: string;
  identifierType: "CIN" | "GSTIN";
  identifier: string;
  websiteUrl: string;
  linkedinUrl: string;
}): Promise<CompanyVerification> {
  return request<CompanyVerification>("/recruiter/company-verification", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function pendingCompanyVerifications(): Promise<AdminCompanyVerification[]> {
  return request<AdminCompanyVerification[]>("/admin/company-verifications");
}

export function reviewCompanyVerification(
  userId: number,
  decision: "VERIFIED" | "REJECTED",
  reviewerNote: string,
): Promise<AdminCompanyVerification> {
  return request<AdminCompanyVerification>(`/admin/company-verifications/${userId}/review`, {
    method: "POST",
    body: JSON.stringify({ decision, reviewer_note: reviewerNote }),
  });
}

export function createJobPost(input: {
  title: string;
  description: string;
  location: string;
  work_arrangement: "REMOTE" | "HYBRID" | "ONSITE";
}): Promise<JobPost> {
  return request<JobPost>("/recruiter/jobs", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function recruiterJobs(): Promise<JobPost[]> {
  return request<JobPost[]>("/recruiter/jobs");
}
