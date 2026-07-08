import { useEffect, useState } from "react";

import type { Course } from "../types/course";
import { getCourses } from "../api/courses";

import CourseForm from "../components/CourseForm";
import CourseList from "../components/CourseList";


function CourseCatalog() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadCourses() {
    try {
      setError(null);
      const data = await getCourses();
      setCourses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load courses");
    }
  }

  useEffect(() => {
    loadCourses();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Course Planner</h1>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      <CourseForm onCourseAdded={loadCourses} />

      <CourseList courses={courses} />
    </div>
  );
}

export default CourseCatalog;