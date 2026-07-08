import type { RequirementsProgressResponse } from "../types/requirement";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function getRequirementsProgress(
  completedCourseIds: number[]
): Promise<RequirementsProgressResponse> {
  const response = await fetch(`${API_URL}/api/requirements/progress`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      completed_course_ids: completedCourseIds,
      manual_completed_courses: [],
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch requirements progress: ${response.status}`);
  }

  return response.json();
}

