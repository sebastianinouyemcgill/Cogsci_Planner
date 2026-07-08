import { createContext, useContext, useMemo, useState } from "react";

type CompletedCoursesContextType = {
  completedCourseIds: number[];
  isCompleted: (courseId: number) => boolean;
  setCompleted: (courseId: number, checked: boolean) => void;
  clearCompleted: () => void;
};

const CompletedCoursesContext =
  createContext<CompletedCoursesContextType | null>(null);

export function CompletedCoursesProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [completedCourseIds, setCompletedCourseIds] = useState<number[]>([]);

  const completedSet = useMemo(
    () => new Set(completedCourseIds),
    [completedCourseIds]
  );

  function isCompleted(courseId: number) {
    return completedSet.has(courseId);
  }

  function setCompleted(courseId: number, checked: boolean) {
    setCompletedCourseIds((prev) => {
      const next = new Set(prev);
      if (checked) next.add(courseId);
      else next.delete(courseId);
      return Array.from(next).sort((a, b) => a - b);
    });
  }

  function clearCompleted() {
    setCompletedCourseIds([]);
  }

  return (
    <CompletedCoursesContext.Provider
      value={{
        completedCourseIds,
        isCompleted,
        setCompleted,
        clearCompleted,
      }}
    >
      {children}
    </CompletedCoursesContext.Provider>
  );
}

export function useCompletedCourses() {
  const context = useContext(CompletedCoursesContext);
  if (!context) {
    throw new Error(
      "useCompletedCourses must be used inside CompletedCoursesProvider"
    );
  }
  return context;
}

