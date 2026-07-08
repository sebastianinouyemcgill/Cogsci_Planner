export type Course = {
  id: number;
  code: string;
  title: string;
  description: string | null;
  credits: number | null;
  level: number | null;
  faculty: "Arts" | "Science" | null;
  department: string | null;
  prerequisites: CourseSummary[];
  streams: NamedEntity[];
  areas: NamedEntity[];
};

export type CourseSummary = {
  id: number;
  code: string;
  title: string;
  description: string | null;
  credits: number | null;
  level: number | null;
  faculty: "Arts" | "Science" | null;
  department: string | null;
};

export type NamedEntity = {
  id: number;
  name: string;
};

export type CourseCreateInput = {
  code: string;
  title: string;
  description?: string | null;
  credits?: number | null;
  level?: number | null;
  faculty?: "Arts" | "Science" | null;
  department?: string | null;
  prerequisite_ids?: number[];
};