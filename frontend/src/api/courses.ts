import type { Course, CourseCreateInput } from "../types/course";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function getCourses(): Promise<Course[]> {
  const response = await fetch(`${API_URL}/api/courses/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch courses: ${response.status}`);
  }
  return response.json();
}

export async function createCourse(
  payload: CourseCreateInput
): Promise<Course> {
  const response = await fetch(`${API_URL}/api/courses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Failed to create course: ${response.status}`);
  }

  return response.json();
}