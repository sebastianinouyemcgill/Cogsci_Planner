import type { Course } from "../types/course";
import { useCompletedCourses } from "../context/CompletedCoursesContext";

type Props = {
  courses: Course[];
};

function CourseList({ courses }: Props) {
  if (courses.length === 0) {
    return <p>No courses yet.</p>;
  }

  const { isCompleted, setCompleted } = useCompletedCourses();

  return (
    <ul>
      {courses.map((course) => (
        <li key={course.id} style={{ marginBottom: 10 }}>
          <label style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
            <input
              type="checkbox"
              checked={isCompleted(course.id)}
              onChange={(e) => setCompleted(course.id, e.target.checked)}
            />
            <span style={{ display: "inline-block" }} />
          </label>
          <strong>{course.code}</strong> — {course.title}
          <div style={{ fontSize: 14 }}>
            {course.credits ?? "?"} credits | level {course.level ?? "?"} |{" "}
            {course.faculty ?? "Unknown faculty"} | {course.department ?? "Unknown department"}
          </div>
          <div style={{ fontSize: 13 }}>
            Streams: {course.streams.length > 0 ? course.streams.map((s) => s.name).join(", ") : "None"}
          </div>
          <div style={{ fontSize: 13 }}>
            Areas: {course.areas.length > 0 ? course.areas.map((a) => a.name).join(", ") : "None"}
          </div>
          <div style={{ fontSize: 13 }}>
            Prereqs: {course.prerequisites.length > 0 ? course.prerequisites.map((p) => p.code).join(", ") : "None"}
          </div>
        </li>
      ))}
    </ul>
  );
}

export default CourseList;