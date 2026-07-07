import { useState } from "react";

type Props = {
  onCourseAdded: () => void;
};

function CourseForm({ onCourseAdded }: Props) {
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    await fetch("http://localhost:8000/api/courses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        title,
      }),
    });

    setCode("");
    setTitle("");

    onCourseAdded();
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Course code"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />

      <input
        placeholder="Course title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <button type="submit">
        Add Course
      </button>
    </form>
  );
}

export default CourseForm;