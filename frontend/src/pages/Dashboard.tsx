import { useEffect, useMemo, useRef, useState } from "react";

import { getCourses } from "@/api/courses";
import {
  getRequirementsProgress,
  RequirementsProgressError,
} from "@/api/requirements";
import { useCourseStatus } from "@/context/CourseStatusContext";
import type { CourseProgressStatus } from "@/types/requirement";
import {
  AREA_ORDER,
  COGS_401_CODE,
  COGS_444_CODE,
  HONOURS_DEGREE_CREDITS,
  STANDARD_DEGREE_CREDITS,
  STREAM_ORDER,
  activeStreamName,
  groupCoursesByName,
} from "@/lib/dashboard-utils";
import { CoreAreaCard } from "@/components/dashboard/CoreAreaCard";
import { CoursePlannerSection } from "@/components/dashboard/CoursePlannerSection";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { DegreeProgressSection } from "@/components/dashboard/DegreeProgressSection";
import { StreamProgressSection } from "@/components/dashboard/StreamProgressSection";
import { StreamSelector } from "@/components/dashboard/StreamSelector";
import { SummaryCards } from "@/components/dashboard/SummaryCards";
import { Separator } from "@/components/ui/separator";

function Dashboard() {
  const {
    courseStatuses,
    bucketOverrides,
    hasAnySelection,
    clearAll,
    setBucketOverride,
  } = useCourseStatus();

  const [courses, setCourses] = useState<Awaited<ReturnType<typeof getCourses>>>(
    []
  );
  const [progress, setProgress] = useState<Awaited<
    ReturnType<typeof getRequirementsProgress>
  > | null>(null);
  const [honours, setHonours] = useState(false);
  const [declaredStream, setDeclaredStream] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overrideErrors, setOverrideErrors] = useState<Record<string, string>>(
    {}
  );
  const pendingOverrideRef = useRef<{
    courseCode: string;
    previousOverride: string | null;
  } | null>(null);

  const selectedCourseEntries = useMemo(() => {
    const entries: {
      course_id: number;
      status: CourseProgressStatus;
      bucket_override?: string;
    }[] = [];

    for (const course of courses) {
      const status = courseStatuses[course.code];
      if (!status) {
        continue;
      }
      const entry: {
        course_id: number;
        status: CourseProgressStatus;
        bucket_override?: string;
      } = {
        course_id: course.id,
        status,
      };
      const override = bucketOverrides[course.code];
      if (override) {
        entry.bucket_override = override;
      }
      entries.push(entry);
    }

    return entries;
  }, [courses, courseStatuses, bucketOverrides]);

  useEffect(() => {
    async function loadCourses() {
      try {
        const data = await getCourses();
        setCourses(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load courses");
      }
    }

    loadCourses();
  }, []);

  useEffect(() => {
    async function loadProgress() {
      setLoading(true);
      setError(null);
      try {
        const data = await getRequirementsProgress(selectedCourseEntries, {
          honoursEnabled: honours,
          declaredStream,
        });
        setProgress(data);
        const pending = pendingOverrideRef.current;
        if (pending) {
          setOverrideErrors((prev) => {
            const next = { ...prev };
            delete next[pending.courseCode];
            return next;
          });
          pendingOverrideRef.current = null;
        }
      } catch (err) {
        const pending = pendingOverrideRef.current;
        if (
          err instanceof RequirementsProgressError &&
          err.status === 422 &&
          pending
        ) {
          setBucketOverride(pending.courseCode, pending.previousOverride);
          setOverrideErrors((prev) => ({
            ...prev,
            [pending.courseCode]: err.message,
          }));
          pendingOverrideRef.current = null;
        } else {
          setError(
            err instanceof Error ? err.message : "Failed to load progress"
          );
        }
      } finally {
        setLoading(false);
      }
    }

    loadProgress();
  }, [selectedCourseEntries, honours, declaredStream, setBucketOverride]);

  function handleOverrideAttempt(
    courseCode: string,
    _override: string | null,
    previousOverride: string | null
  ) {
    pendingOverrideRef.current = { courseCode, previousOverride };
  }

  const coursesByArea = useMemo(
    () =>
      groupCoursesByName(courses, AREA_ORDER, (course) =>
        course.areas.map((area) => area.name)
      ),
    [courses]
  );

  const coursesByStream = useMemo(
    () =>
      groupCoursesByName(courses, STREAM_ORDER, (course) =>
        course.streams.map((stream) => stream.name)
      ),
    [courses]
  );

  const honoursResearchCourses = useMemo(
    () =>
      courses
        .filter((course) => course.code === COGS_444_CODE)
        .sort((a, b) => a.code.localeCompare(b.code)),
    [courses]
  );

  const researchCourses = useMemo(() => {
    const codes = honours
      ? [COGS_401_CODE, COGS_444_CODE]
      : [COGS_401_CODE];
    return courses
      .filter((course) => codes.includes(course.code))
      .sort((a, b) => a.code.localeCompare(b.code));
  }, [courses, honours]);

  const totalSelectedCredits = useMemo(
    () =>
      courses
        .filter((course) => course.code in courseStatuses)
        .reduce((sum, course) => sum + (course.credits ?? 0), 0),
    [courses, courseStatuses]
  );

  const degreeCreditTarget = honours
    ? HONOURS_DEGREE_CREDITS
    : STANDARD_DEGREE_CREDITS;

  const completed = progress?.completed;
  const projected = progress?.projected;
  const requiredAreasCount = projected?.areas.required_areas.length ?? 8;
  const officialProjected = projected?.official_stream_complementary;
  const activeStream = activeStreamName(declaredStream, projected);
  const isProvisionalStream =
    declaredStream === null &&
    officialProjected?.stream_is_provisional === true &&
    Boolean(officialProjected.provisional_stream);

  return (
    <div className="mx-auto w-full max-w-7xl space-y-8 px-4 py-8 text-left sm:px-6">
      <DashboardHeader
        honours={honours}
        onHonoursChange={setHonours}
        onClearAll={clearAll}
        totalSelectedCredits={totalSelectedCredits}
        degreeCreditTarget={degreeCreditTarget}
      />

      {error ? (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      <SummaryCards
        projected={projected}
        honours={honours}
        activeStream={activeStream}
        declaredStream={declaredStream}
        isProvisionalStream={isProvisionalStream}
        requiredAreasCount={requiredAreasCount}
      />

      <StreamSelector
        declaredStream={declaredStream}
        activeStream={activeStream}
        isProvisional={isProvisionalStream}
        provisionalStream={officialProjected?.provisional_stream ?? null}
        onDeclaredStreamChange={setDeclaredStream}
        onAcceptProvisional={() =>
          setDeclaredStream(officialProjected?.provisional_stream ?? null)
        }
      />

      {!hasAnySelection ? (
        <div className="rounded-lg border border-dashed border-border px-4 py-6 text-center text-sm text-muted-foreground">
          Select courses below to calculate your degree progress.
        </div>
      ) : null}

      {loading && !progress ? (
        <p className="text-sm text-muted-foreground">Loading progress…</p>
      ) : null}

      {completed && projected ? (
        <DegreeProgressSection
          completed={completed}
          projected={projected}
          requiredAreasCount={requiredAreasCount}
          activeStream={activeStream}
          honours={honours}
        />
      ) : null}

      <Separator />

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Core requirements
          </h2>
          <p className="text-sm text-muted-foreground">
            Eight required Cognitive Science areas — one course each.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {AREA_ORDER.map((areaName) => (
            <CoreAreaCard
              key={areaName}
              areaName={areaName}
              courses={coursesByArea.get(areaName) ?? []}
              projected={projected}
              overrideErrors={overrideErrors}
              onOverrideAttempt={handleOverrideAttempt}
            />
          ))}
        </div>
      </section>

      <Separator />

      <StreamProgressSection
        coursesByStream={coursesByStream}
        researchCourses={researchCourses}
        honoursResearchCourses={honoursResearchCourses}
        projected={projected}
        declaredStream={declaredStream}
        overrideErrors={overrideErrors}
        onOverrideAttempt={handleOverrideAttempt}
        honours={honours}
      />

      <Separator />

      <CoursePlannerSection />
    </div>
  );
}

export default Dashboard;
