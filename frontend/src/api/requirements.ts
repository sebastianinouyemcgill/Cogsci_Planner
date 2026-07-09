import type {
  CourseProgressStatus,
  RequirementsProgressResponse,
} from "../types/requirement";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type ProgressCourseEntry = {
  course_id: number;
  status: CourseProgressStatus;
  bucket_override?: string;
};

export class RequirementsProgressError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "RequirementsProgressError";
    this.status = status;
  }
}

export async function getRequirementsProgress(
  courses: ProgressCourseEntry[],
  options?: { honoursEnabled?: boolean; declaredStream?: string | null }
): Promise<RequirementsProgressResponse> {
  const response = await fetch(`${API_URL}/api/requirements/progress`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      courses,
      manual_completed_courses: [],
      honours_enabled: options?.honoursEnabled ?? false,
      declared_stream: options?.declaredStream ?? null,
    }),
  });

  if (!response.ok) {
    let detail = `Failed to fetch requirements progress: ${response.status}`;
    if (response.status === 422) {
      try {
        const body = (await response.json()) as { detail?: string };
        if (typeof body.detail === "string") {
          detail = body.detail;
        }
      } catch {
        // Keep the generic message when the error body is not JSON.
      }
    }
    throw new RequirementsProgressError(detail, response.status);
  }

  return response.json();
}
