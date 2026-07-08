import { useState } from "react";

import { createCourse } from "../api/courses";

type Props = {
  onCourseAdded: () => void;
};

function CourseForm({ onCourseAdded }: Props) {
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [credits, setCredits] = useState("");
  const [level, setLevel] = useState("");
  const [faculty, setFaculty] = useState<"" | "Arts" | "Science">("");
  const [department, setDepartment] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await createCourse({
        code,
        title,
        description: description.trim() || null,
        credits: credits === "" ? null : Number(credits),
        level: level === "" ? null : Number(level),
        faculty: faculty === "" ? null : faculty,
        department: department.trim() || null,
        prerequisite_ids: [],
      });

      setCode("");
      setTitle("");
      setDescription("");
      setCredits("");
      setLevel("");
      setFaculty("");
      setDepartment("");

      onCourseAdded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add course");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "grid", gap: 8, marginBottom: 20 }}>
      {error ? <p style={{ color: "crimson", margin: 0 }}>{error}</p> : null}

      <input
        placeholder="Course code"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        required
      />

      <input
        placeholder="Course title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      <input
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <input
        type="number"
        placeholder="Credits (e.g. 3)"
        value={credits}
        onChange={(e) => setCredits(e.target.value)}
        min={0}
      />

      <input
        type="number"
        placeholder="Level (e.g. 300)"
        value={level}
        onChange={(e) => setLevel(e.target.value)}
        min={0}
      />

      <select
        value={faculty}
        onChange={(e) => setFaculty(e.target.value as "" | "Arts" | "Science")}
      >
        <option value="">Faculty (optional)</option>
        <option value="Arts">Arts</option>
        <option value="Science">Science</option>
      </select>

      <input
        placeholder="Department"
        value={department}
        onChange={(e) => setDepartment(e.target.value)}
      />

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Adding..." : "Add Course"}
      </button>
    </form>
  );
}

export default CourseForm;
