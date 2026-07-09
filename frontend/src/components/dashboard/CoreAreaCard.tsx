import { CheckCircle2, Circle } from "lucide-react";

import { useCourseStatus } from "@/context/CourseStatusContext";
import type { Course } from "@/types/course";
import type { RequirementProgressBreakdown } from "@/types/requirement";
import {
  courseAllocation,
  formatBucketLabel,
  isElectiveCourse,
  shortAreaName,
} from "@/lib/dashboard-utils";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { BucketOverrideSelect } from "@/components/dashboard/BucketOverrideSelect";
import { CourseStatusSelect } from "@/components/dashboard/CourseStatusSelect";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type CoreAreaCardProps = {
  areaName: string;
  courses: Course[];
  projected: RequirementProgressBreakdown | undefined;
  overrideErrors: Record<string, string>;
  onOverrideAttempt: (
    courseCode: string,
    override: string | null,
    previousOverride: string | null
  ) => void;
};

export function CoreAreaCard({
  areaName,
  courses,
  projected,
  overrideErrors,
  onOverrideAttempt,
}: CoreAreaCardProps) {
  const { getStatus } = useCourseStatus();

  const isComplete =
    projected?.areas.completed_areas.includes(areaName) ?? false;
  const fillingCourseId = projected?.areas.area_course_ids?.[areaName];
  const fillingCourse = courses.find(
    (course) => course.id === Number(fillingCourseId)
  );

  const selectedInArea = courses.find(
    (course) => getStatus(course.code) !== "not_taken"
  );

  const displayCourse = fillingCourse ?? selectedInArea;

  return (
    <Card
      size="sm"
      className={isComplete ? "ring-primary/40" : undefined}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-sm leading-snug">
            {shortAreaName(areaName)}
          </CardTitle>
          {isComplete ? (
            <Badge variant="secondary" className="shrink-0 gap-1">
              <CheckCircle2 className="size-3" />
              Done
            </Badge>
          ) : (
            <Badge variant="outline" className="shrink-0 gap-1">
              <Circle className="size-3" />
              Open
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-xs text-muted-foreground">
          {displayCourse ? (
            <>
              <span className="font-medium text-foreground">
                {displayCourse.code}
              </span>
              {" · "}
              {displayCourse.title}
            </>
          ) : (
            "Not selected"
          )}
        </p>

        <div className="space-y-2">
          {courses.length === 0 ? (
            <p className="text-xs text-muted-foreground">No courses listed.</p>
          ) : (
            courses.map((course) => {
              const status = getStatus(course.code);
              const allocation = courseAllocation(projected, course.id);
              const showOverride =
                status !== "not_taken" &&
                (allocation?.eligible_buckets.length ?? 0) > 0;
              const fillsArea =
                fillingCourseId !== undefined &&
                Number(fillingCourseId) === course.id;

              return (
                <div
                  key={course.code}
                  className="space-y-1.5 rounded-lg border border-border/60 bg-muted/30 p-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <Tooltip>
                      <TooltipTrigger className="truncate text-left text-xs font-medium">
                        {course.code}
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-xs">
                        {course.title}
                      </TooltipContent>
                    </Tooltip>
                    <div className="flex shrink-0 items-center gap-1">
                      {fillsArea ? (
                        <Badge variant="secondary" className="text-[10px]">
                          Fills
                        </Badge>
                      ) : null}
                      {isElectiveCourse(projected, course.id) ? (
                        <Badge variant="outline" className="text-[10px]">
                          Elective
                        </Badge>
                      ) : null}
                    </div>
                  </div>
                  <CourseStatusSelect courseCode={course.code} />
                  {allocation?.allocated_bucket &&
                  !isElectiveCourse(projected, course.id) ? (
                    <p className="text-[10px] text-muted-foreground">
                      → {formatBucketLabel(allocation.allocated_bucket)}
                    </p>
                  ) : null}
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
            })
          )}
        </div>
      </CardContent>
    </Card>
  );
}
