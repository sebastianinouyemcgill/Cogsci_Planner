import { useEffect, useState } from "react";

type Course = {
  id: number;
  code: string;
  title: string;
};

function App() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/courses")
      .then((res) => res.json())
      .then((data) => {
        setCourses(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Course Planner</h1>

      {loading ? (
        <p>Loading...</p>
      ) : courses.length === 0 ? (
        <p>No courses yet</p>
      ) : (
        <ul>
          {courses.map((course) => (
            <li key={course.id}>
              {course.code} — {course.title}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;