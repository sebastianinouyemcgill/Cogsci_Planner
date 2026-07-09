import { useCourseStatus } from "@/context/CourseStatusContext";
import type { Course } from "@/types/course";
import type { RequirementProgressBreakdown } from "@/types/requirement";
import {
  courseAllocation,
  formatBucketLabel,
  isElectiveCourse,
} from "@/lib/dashboard-utils";
import { Badge } from "@/components/ui/badge";
import { BucketOverrideSelect } from "@/components/dashboard/BucketOverrideSelect";
import { CourseStatusSelect } from "@/components/dashboard/CourseStatusSelect";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type StreamCourseRowProps = {
  course: Course;
  projected: RequirementProgressBreakdown | undefined;
  overrideErrors: Record<string, string>;
  onOverrideAttempt: (
    courseCode: string,
    override: string | null,
    previousOverride: string | null
  ) => void;
};

export function StreamCourseRow({
  course,
  projected,
  overrideErrors,
  onOverrideAttempt,
}: StreamCourseRowProps) {
  const { getStatus } = useCourseStatus();
  const status = getStatus(course.code);
  const allocation = courseAllocation(projected, course.id);
  const showOverride =
    status !== "not_taken" &&
    (allocation?.eligible_buckets.length ?? 0) > 0;

  return (
    <div className="space-y-2 rounded-lg border border-border/60 bg-background p-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0 space-y-0.5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-sm font-medium">{course.code}</span>
            {isElectiveCourse(projected, course.id) ? (
              <Badge variant="outline">Elective</Badge>
            ) : null}
            {status !== "not_taken" ? (
              <Badge variant="secondary">
                {status === "completed" ? "Completed" : "Planned"}
              </Badge>
            ) : null}
          </div>
          <Tooltip>
            <TooltipTrigger className="truncate text-left text-xs text-muted-foreground">
              {course.title}
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-sm">
              {course.title}
            </TooltipContent>
          </Tooltip>
        </div>
        <span className="shrink-0 text-xs text-muted-foreground">
          {course.credits ?? "?"} cr · L{course.level ?? "?"}
        </span>
      </div>

      {allocation?.allocated_bucket &&
      !isElectiveCourse(projected, course.id) ? (
        <p className="text-xs text-muted-foreground">
          Allocated to {formatBucketLabel(allocation.allocated_bucket)}
        </p>
      ) : null}

      <CourseStatusSelect courseCode={course.code} />

      {showOverride && allocation ? (
        <BucketOverrideSelect
          courseCode={course.code}
          allocation={allocation}
          overrideError={overrideErrors[course.code]}
          onOverrideAttempt={onOverrideAttempt}
        />
      ) : null}
    </div>
  );
}
