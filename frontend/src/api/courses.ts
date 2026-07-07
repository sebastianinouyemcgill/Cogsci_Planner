import type { Course } from "../types/course";

const API_URL = "http://localhost:8000";

export async function getCourses(): Promise<Course[]> {
  const response = await fetch(`${API_URL}/api/courses`);
  return response.json();
}

export async function createCourse(
  code: string,
  title: string
): Promise<Course> {
  const response = await fetch(`${API_URL}/api/courses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code,
      title,
    }),
  });

  return response.json();
}