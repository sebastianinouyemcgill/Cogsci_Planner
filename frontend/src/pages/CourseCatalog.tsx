import { useEffect, useState } from "react";

import type { Course } from "../types/course";
import { getCourses } from "../api/courses";

import CourseForm from "../components/CourseForm";
import CourseList from "../components/CourseList";


function CourseCatalog() {
  const [courses, setCourses] = useState<Course[]>([]);

  async function loadCourses() {
    const data = await getCourses();
    setCourses(data);
  }

  useEffect(() => {
    loadCourses();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Course Planner</h1>

      <CourseForm onCourseAdded={loadCourses} />

      <CourseList courses={courses} />
    </div>
  );
}

export default CourseCatalog;