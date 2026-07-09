import { createContext, useContext, useState } from "react";

import type { CourseProgressStatus } from "../types/requirement";

export type CourseSelectionStatus = "not_taken" | CourseProgressStatus;

type CourseStatusContextType = {
  getStatus: (courseCode: string) => CourseSelectionStatus;
  setStatus: (courseCode: string, status: CourseSelectionStatus) => void;
  getBucketOverride: (courseCode: string) => string | null;
  setBucketOverride: (courseCode: string, override: string | null) => void;
  clearAll: () => void;
  courseStatuses: Record<string, CourseProgressStatus>;
  bucketOverrides: Record<string, string>;
  hasAnySelection: boolean;
};

const CourseStatusContext = createContext<CourseStatusContextType | null>(null);

export function CourseStatusProvider({ children }: { children: React.ReactNode }) {
  const [courseStatuses, setCourseStatuses] = useState<
    Record<string, CourseProgressStatus>
  >({});
  const [bucketOverrides, setBucketOverrides] = useState<
    Record<string, string>
  >({});

  const hasAnySelection = Object.keys(courseStatuses).length > 0;

  function getStatus(courseCode: string): CourseSelectionStatus {
    return courseStatuses[courseCode] ?? "not_taken";
  }

  function setStatus(courseCode: string, status: CourseSelectionStatus) {
    setCourseStatuses((prev) => {
      const next = { ...prev };
      if (status === "not_taken") {
        delete next[courseCode];
      } else {
        next[courseCode] = status;
      }
      return next;
    });
    if (status === "not_taken") {
      setBucketOverrides((prev) => {
        if (!(courseCode in prev)) {
          return prev;
        }
        const next = { ...prev };
        delete next[courseCode];
        return next;
      });
    }
  }

  function getBucketOverride(courseCode: string): string | null {
    return bucketOverrides[courseCode] ?? null;
  }

  function setBucketOverride(courseCode: string, override: string | null) {
    setBucketOverrides((prev) => {
      const next = { ...prev };
      if (override === null) {
        delete next[courseCode];
      } else {
        next[courseCode] = override;
      }
      return next;
    });
  }

  function clearAll() {
    setCourseStatuses({});
    setBucketOverrides({});
  }

  return (
    <CourseStatusContext.Provider
      value={{
        getStatus,
        setStatus,
        getBucketOverride,
        setBucketOverride,
        clearAll,
        courseStatuses,
        bucketOverrides,
        hasAnySelection,
      }}
    >
      {children}
    </CourseStatusContext.Provider>
  );
}

export function useCourseStatus() {
  const context = useContext(CourseStatusContext);
  if (!context) {
    throw new Error("useCourseStatus must be used inside CourseStatusProvider");
  }
  return context;
}
