import type { Course } from "../types/course";

type Props = {
  courses: Course[];
};

function CourseList({ courses }: Props) {
  return (
    <ul>
      {courses.map((course) => (
        <li key={course.id}>
          {course.code} — {course.title}
        </li>
      ))}
    </ul>
  );
}

export default CourseList;