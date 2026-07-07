import { createContext, useContext, useState } from "react";
import type { Course } from "../types/course";


type PlannerContextType = {
  plannedCourses: Course[];
  addCourse: (course: Course) => void;
  removeCourse: (id: number) => void;
};


const PlannerContext = createContext<PlannerContextType | null>(null);


export function PlannerProvider({
  children,
}: {
  children: React.ReactNode;
}) {

  const [plannedCourses, setPlannedCourses] = useState<Course[]>([]);


  function addCourse(course: Course) {

    setPlannedCourses((prev) => {

      if (prev.some((c) => c.id === course.id)) {
        return prev;
      }

      return [...prev, course];
    });
  }


  function removeCourse(id: number) {
    setPlannedCourses((prev) =>
      prev.filter((c) => c.id !== id)
    );
  }


  return (
    <PlannerContext.Provider
      value={{
        plannedCourses,
        addCourse,
        removeCourse,
      }}
    >
      {children}
    </PlannerContext.Provider>
  );
}


export function usePlanner() {

  const context = useContext(PlannerContext);

  if (!context) {
    throw new Error(
      "usePlanner must be used inside PlannerProvider"
    );
  }

  return context;
}