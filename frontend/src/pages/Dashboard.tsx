import { useEffect, useMemo, useRef, useState } from "react";

import { getCourses } from "../api/courses";
import {
  getRequirementsProgress,
  RequirementsProgressError,
} from "../api/requirements";
import {
  useCourseStatus,
  type CourseSelectionStatus,
} from "../context/CourseStatusContext";
import type { Course } from "../types/course";
import type {
  CourseBucketAllocation,
  CourseProgressStatus,
  RequirementProgressBreakdown,
  RequirementsProgressResponse,
} from "../types/requirement";

const STREAM_REQUIRED_CREDITS = 18;
const COMPLEMENTARY_REQUIRED_CREDITS = 12;
const LEVEL_400_PLUS_REQUIRED_CREDITS = 15;
const ARTS_REQUIRED_CREDITS = 21;
const SCIENCE_REQUIRED_CREDITS = 21;
const STANDARD_DEGREE_CREDITS = 54;
const HONOURS_DEGREE_CREDITS = 60;

const STREAM_ORDER = [
  "Computer Science",
  "Neuroscience",
  "Psychology",
  "Linguistics",
  "Philosophy",
];

const AREA_ORDER = [
  "Neuroscience (Required)",
  "Logic",
  "Statistics",
  "Computer Science Foundations",
  "Linguistics Foundations",
  "Philosophy Foundations",
  "Neuroscience Foundations",
  "Psychology Foundations",
];

const COGS_401_CODE = "COGS 401";
const COGS_444_CODE = "COGS 444";

function ratio(value: number, target: number) {
  if (target <= 0) return 0;
  return Math.min(1, value / target);
}

function activeStreamName(
  declaredStream: string | null,
  breakdown: RequirementProgressBreakdown | undefined
): string | null {
  if (declaredStream) {
    return declaredStream;
  }
  const official = breakdown?.official_stream_complementary;
  if (official?.stream_is_provisional && official.provisional_stream) {
    return official.provisional_stream;
  }
  return official?.declared_stream ?? null;
}

function overallCompletionPct(
  projected: RequirementProgressBreakdown,
  honoursEnabled: boolean
) {
  const official = projected.official_stream_complementary;
  const streamCredits = official?.stream_credits ?? 0;
  const streamRequired =
    official?.stream_credit_required ?? STREAM_REQUIRED_CREDITS;
  const complementaryCredits = official?.complementary_credits ?? 0;
  const complementaryRequired =
    official?.complementary_credit_required ?? COMPLEMENTARY_REQUIRED_CREDITS;

  const ratios = [
    ratio(
      projected.areas.completed_areas.length,
      projected.areas.required_areas.length
    ),
    ratio(streamCredits, streamRequired),
    ratio(complementaryCredits, complementaryRequired),
    ratio(projected.level_400_plus.credits, LEVEL_400_PLUS_REQUIRED_CREDITS),
    ratio(projected.arts_science.arts_credits, ARTS_REQUIRED_CREDITS),
    ratio(projected.arts_science.science_credits, SCIENCE_REQUIRED_CREDITS),
  ];

  if (honoursEnabled && projected.honours_research) {
    ratios.push(
      ratio(
        projected.honours_research.credits,
        projected.honours_research.required_credits
      )
    );
  }

  return Math.round(
    (ratios.reduce((sum, value) => sum + value, 0) / ratios.length) * 100
  );
}

function groupCoursesByName(
  courses: Course[],
  names: string[],
  getNames: (course: Course) => string[]
) {
  const grouped = new Map<string, Course[]>();
  for (const name of names) {
    grouped.set(name, []);
  }

  for (const course of courses) {
    for (const name of getNames(course)) {
      const bucket = grouped.get(name);
      if (bucket) {
        bucket.push(course);
      }
    }
  }

  for (const list of grouped.values()) {
    list.sort((a, b) => a.code.localeCompare(b.code));
  }

  return grouped;
}

function lookupRecordValue<T>(
  record: Record<number, T> | undefined,
  courseId: number
): T | undefined {
  if (!record) {
    return undefined;
  }
  return record[courseId] ?? record[String(courseId) as unknown as number];
}

function courseAllocation(
  breakdown: RequirementProgressBreakdown | undefined,
  courseId: number
): CourseBucketAllocation | undefined {
  const explore = lookupRecordValue(
    breakdown?.stream_complementary.course_allocations,
    courseId
  );
  if (explore) {
    return explore;
  }
  return lookupRecordValue(
    breakdown?.official_stream_complementary?.course_allocations,
    courseId
  );
}

function formatBucketLabel(bucket: string | null | undefined): string {
  if (!bucket) {
    return "Unallocated";
  }
  if (bucket === "complementary") {
    return "Complementary";
  }
  if (bucket === "electives") {
    return "Elective";
  }
  if (bucket.startsWith("stream:")) {
    return bucket.slice("stream:".length);
  }
  return bucket;
}

function isElectiveCourse(
  breakdown: RequirementProgressBreakdown | undefined,
  courseId: number
): boolean {
  const allocation = courseAllocation(breakdown, courseId);
  if (allocation?.allocated_bucket === "electives") {
    return true;
  }
  const electiveIds = breakdown?.electives?.course_ids ?? [];
  return electiveIds.some((id) => Number(id) === courseId);
}

function CourseStatusControl({
  courseCode,
}: {
  courseCode: string;
}) {
  const { getStatus, setStatus } = useCourseStatus();
  const status = getStatus(courseCode);

  const options: { value: CourseSelectionStatus; label: string }[] = [
    { value: "not_taken", label: "Not taken" },
    { value: "planned", label: "Planned" },
    { value: "completed", label: "Completed" },
  ];

  return (
    <div style={{ display: "inline-flex", gap: 8, flexWrap: "wrap" }}>
      {options.map((option) => (
        <label
          key={option.value}
          style={{ display: "inline-flex", alignItems: "center", gap: 4 }}
        >
          <input
            type="radio"
            name={`course-status-${courseCode}`}
            checked={status === option.value}
            onChange={() => setStatus(courseCode, option.value)}
          />
          {option.label}
        </label>
      ))}
    </div>
  );
}

function BucketOverrideControl({
  courseCode,
  allocation,
  overrideError,
  onOverrideAttempt,
}: {
  courseCode: string;
  allocation: CourseBucketAllocation;
  overrideError?: string;
  onOverrideAttempt: (
    courseCode: string,
    override: string | null,
    previousOverride: string | null
  ) => void;
}) {
  const { getBucketOverride, setBucketOverride } = useCourseStatus();
  const selectedOverride = getBucketOverride(courseCode);
  const autoLabel = formatBucketLabel(allocation.allocated_bucket);

  return (
    <div style={{ marginTop: 8 }}>
      <label style={{ display: "block", fontSize: 14 }}>
        Credit bucket:{" "}
        <select
          value={selectedOverride ?? ""}
          onChange={(event) => {
            const nextOverride =
              event.target.value === "" ? null : event.target.value;
            onOverrideAttempt(courseCode, nextOverride, selectedOverride);
            setBucketOverride(courseCode, nextOverride);
          }}
        >
          <option value="">Auto (currently: {autoLabel})</option>
          {allocation.eligible_buckets.map((bucket) => (
            <option key={bucket} value={bucket}>
              {bucket}
            </option>
          ))}
        </select>
      </label>
      {overrideError ? (
        <div style={{ color: "crimson", fontSize: 13, marginTop: 4 }}>
          {overrideError}
        </div>
      ) : null}
    </div>
  );
}

function AllocationTag({
  breakdown,
  courseId,
}: {
  breakdown: RequirementProgressBreakdown | undefined;
  courseId: number;
}) {
  if (!isElectiveCourse(breakdown, courseId)) {
    return null;
  }

  return (
    <span
      style={{
        display: "inline-block",
        marginLeft: 8,
        padding: "2px 8px",
        fontSize: 12,
        borderRadius: 999,
        background: "var(--code-bg)",
        border: "1px solid var(--border)",
        color: "var(--text-h)",
      }}
    >
      Elective
    </span>
  );
}

function DualProgressRow({
  label,
  completedNumerator,
  projectedNumerator,
  denominator,
}: {
  label: string;
  completedNumerator: number;
  projectedNumerator: number;
  denominator: number;
}) {
  const completedPct = ratio(completedNumerator, denominator) * 100;
  const projectedPct = ratio(projectedNumerator, denominator) * 100;

  return (
    <div style={{ marginBottom: 16, textAlign: "left" }}>
      <div style={{ marginBottom: 6, color: "var(--text-h)" }}>
        {label}: {completedNumerator} / {denominator}
        {projectedNumerator > completedNumerator
          ? ` (projected ${projectedNumerator})`
          : ""}
      </div>
      <div
        style={{
          position: "relative",
          height: 12,
          background: "var(--code-bg)",
          borderRadius: 6,
          overflow: "hidden",
          border: "1px solid var(--border)",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            height: "100%",
            width: `${projectedPct}%`,
            background:
              "repeating-linear-gradient(-45deg, #b8b8b8 0 4px, #e0e0e0 4px 8px)",
            borderRadius: 6,
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            height: "100%",
            width: `${completedPct}%`,
            background: "var(--text-h)",
            borderRadius: 6,
          }}
        />
      </div>
    </div>
  );
}

function CourseAccordion({
  title,
  courses,
  projected,
  overrideErrors,
  onOverrideAttempt,
  streamHighlight,
  areaName,
}: {
  title: string;
  courses: Course[];
  projected: RequirementProgressBreakdown | undefined;
  overrideErrors: Record<string, string>;
  onOverrideAttempt: (
    courseCode: string,
    override: string | null,
    previousOverride: string | null
  ) => void;
  streamHighlight?: "declared" | "provisional" | null;
  areaName?: string;
}) {
  const { getStatus } = useCourseStatus();

  const highlightLabel =
    streamHighlight === "declared"
      ? " — your stream"
      : streamHighlight === "provisional"
        ? " — provisional best fit"
        : "";

  const areaComplete =
    areaName !== undefined &&
    (projected?.areas.completed_areas.includes(areaName) ?? false);
  const areaFillingCourseId = areaName
    ? projected?.areas.area_course_ids?.[areaName]
    : undefined;

  return (
    <details
      style={{
        marginBottom: 10,
        border:
          streamHighlight === "declared"
            ? "2px solid var(--text-h)"
            : streamHighlight === "provisional"
              ? "2px dashed var(--text-h)"
              : areaComplete
                ? "2px solid color-mix(in srgb, var(--text-h) 60%, green 40%)"
                : "1px solid var(--border)",
        borderRadius: 8,
        padding: "8px 12px",
        textAlign: "left",
        background:
          streamHighlight === "declared"
            ? "color-mix(in srgb, var(--code-bg) 70%, var(--text-h) 5%)"
            : streamHighlight === "provisional"
              ? "color-mix(in srgb, var(--code-bg) 85%, var(--text-h) 3%)"
              : areaComplete
                ? "color-mix(in srgb, var(--code-bg) 90%, green 5%)"
                : undefined,
      }}
    >
      <summary style={{ cursor: "pointer", color: "var(--text-h)" }}>
        {areaComplete ? "✓ " : ""}
        {title}
        {highlightLabel} ({courses.length} course{courses.length === 1 ? "" : "s"})
      </summary>
      {courses.length === 0 ? (
        <p style={{ marginTop: 10 }}>No courses in this group.</p>
      ) : (
        <ul style={{ margin: "12px 0 0", paddingLeft: 18 }}>
          {courses.map((course) => {
            const status = getStatus(course.code);
            const allocation = courseAllocation(projected, course.id);
            const showOverrideControl =
              status !== "not_taken" &&
              (allocation?.eligible_buckets.length ?? 0) > 0;
            const fillsArea =
              areaFillingCourseId !== undefined &&
              Number(areaFillingCourseId) === course.id;

            return (
              <li key={course.code} style={{ marginBottom: 14 }}>
                <div style={{ color: "var(--text-h)" }}>
                  <strong>{course.code}</strong> — {course.title}
                  <AllocationTag breakdown={projected} courseId={course.id} />
                  {fillsArea ? (
                    <span
                      style={{
                        display: "inline-block",
                        marginLeft: 8,
                        padding: "2px 8px",
                        fontSize: 12,
                        borderRadius: 999,
                        background: "color-mix(in srgb, var(--code-bg) 80%, green 20%)",
                        border: "1px solid var(--border)",
                        color: "var(--text-h)",
                      }}
                    >
                      Fills area
                    </span>
                  ) : null}
                  {status !== "not_taken" ? (
                    <span
                      style={{
                        display: "inline-block",
                        marginLeft: 8,
                        padding: "2px 8px",
                        fontSize: 12,
                        borderRadius: 999,
                        background: "var(--code-bg)",
                        border: "1px solid var(--border)",
                        color: "var(--text-h)",
                      }}
                    >
                      {status === "completed" ? "Completed" : "Planned"}
                    </span>
                  ) : null}
                </div>
                <div style={{ fontSize: 14, marginBottom: 6 }}>
                  {course.credits ?? "?"} credits | level {course.level ?? "?"} |{" "}
                  {course.faculty ?? "Unknown faculty"}
                  {allocation?.allocated_bucket &&
                  !isElectiveCourse(projected, course.id) ? (
                    <span style={{ marginLeft: 8, color: "var(--text-h)" }}>
                      → {formatBucketLabel(allocation.allocated_bucket)}
                    </span>
                  ) : null}
                </div>
                <CourseStatusControl courseCode={course.code} />
                {showOverrideControl && allocation ? (
                  <BucketOverrideControl
                    courseCode={course.code}
                    allocation={allocation}
                    overrideError={overrideErrors[course.code]}
                    onOverrideAttempt={onOverrideAttempt}
                  />
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </details>
  );
}

function Dashboard() {
  const {
    courseStatuses,
    bucketOverrides,
    hasAnySelection,
    clearAll,
    setBucketOverride,
  } = useCourseStatus();

  const [courses, setCourses] = useState<Course[]>([]);
  const [progress, setProgress] = useState<RequirementsProgressResponse | null>(
    null
  );
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
      groupCoursesByName(
        courses,
        AREA_ORDER,
        (course) => course.areas.map((area) => area.name)
      ),
    [courses]
  );

  const coursesByStream = useMemo(
    () =>
      groupCoursesByName(
        courses,
        STREAM_ORDER,
        (course) => course.streams.map((stream) => stream.name)
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
  const officialCompleted = completed?.official_stream_complementary;
  const activeStream = activeStreamName(declaredStream, projected);
  const showProvisionalBanner =
    declaredStream === null &&
    officialProjected?.stream_is_provisional === true &&
    Boolean(officialProjected.provisional_stream);

  function streamHighlightFor(
    streamName: string
  ): "declared" | "provisional" | null {
    if (declaredStream === streamName) {
      return "declared";
    }
    if (
      declaredStream === null &&
      officialProjected?.stream_is_provisional &&
      officialProjected.provisional_stream === streamName
    ) {
      return "provisional";
    }
    return null;
  }

  function streamProgressLabel(streamName: string): string {
    const highlight = streamHighlightFor(streamName);
    if (highlight === "declared") {
      return `Stream: ${streamName} (your stream, explore view)`;
    }
    if (highlight === "provisional") {
      return `Stream: ${streamName} (provisional best fit, explore view)`;
    }
    return `Stream: ${streamName} (explore view)`;
  }

  return (
    <div style={{ padding: 20, textAlign: "left" }}>
      <h1 style={{ textAlign: "center" }}>Degree Dashboard</h1>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          alignItems: "center",
          justifyContent: "space-between",
          padding: "14px 16px",
          marginBottom: 20,
          border: "1px solid var(--border)",
          borderRadius: 8,
          background: "var(--code-bg)",
        }}
      >
        <div>
          <strong style={{ color: "var(--text-h)" }}>Overall completion</strong>
          <div style={{ fontSize: 28, color: "var(--text-h)" }}>
            {projected ? `${overallCompletionPct(projected, honours)}%` : "—"}
          </div>
        </div>
        <div>
          <strong style={{ color: "var(--text-h)" }}>Total credits</strong>
          <div>
            {totalSelectedCredits} / {degreeCreditTarget}
          </div>
        </div>
        <div>
          <strong style={{ color: "var(--text-h)" }}>Arts</strong>
          <div>{projected?.arts_science.arts_credits ?? 0}</div>
        </div>
        <div>
          <strong style={{ color: "var(--text-h)" }}>Science</strong>
          <div>{projected?.arts_science.science_credits ?? 0}</div>
        </div>
        <label
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            color: "var(--text-h)",
          }}
        >
          <input
            type="checkbox"
            checked={honours}
            onChange={(e) => setHonours(e.target.checked)}
          />
          Honours (60 cr)
        </label>
        <button type="button" onClick={clearAll}>
          Clear all
        </button>
      </div>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          alignItems: "center",
          marginBottom: 16,
          padding: "12px 16px",
          border: "1px solid var(--border)",
          borderRadius: 8,
        }}
      >
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <strong style={{ color: "var(--text-h)" }}>My Stream</strong>
          <select
            value={declaredStream ?? ""}
            onChange={(event) =>
              setDeclaredStream(event.target.value || null)
            }
          >
            <option value="">Not declared</option>
            {STREAM_ORDER.map((streamName) => (
              <option key={streamName} value={streamName}>
                {streamName}
              </option>
            ))}
          </select>
        </label>
        {activeStream ? (
          <span style={{ fontSize: 14, color: "var(--text-h)" }}>
            Official progress uses{" "}
            <strong>
              {declaredStream ? declaredStream : `${activeStream} (provisional)`}
            </strong>
          </span>
        ) : null}
      </div>

      {showProvisionalBanner && officialProjected?.provisional_stream ? (
        <div
          style={{
            marginBottom: 20,
            padding: "12px 16px",
            borderRadius: 8,
            border: "1px dashed var(--border)",
            background: "var(--code-bg)",
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <span style={{ fontSize: 14 }}>
            Currently defaulting to{" "}
            <strong>{officialProjected.provisional_stream}</strong> as your
            best-fit stream — select a stream to lock this in.
          </span>
          <button
            type="button"
            onClick={() =>
              setDeclaredStream(officialProjected.provisional_stream)
            }
          >
            Use this
          </button>
        </div>
      ) : null}

      {!hasAnySelection ? (
        <p
          style={{
            marginBottom: 24,
            padding: 16,
            border: "1px dashed var(--border)",
            borderRadius: 8,
            textAlign: "center",
          }}
        >
          No courses selected yet. Mark courses as planned or completed in the
          accordions below to see your progress.
        </p>
      ) : null}

      {loading && !progress ? <p>Loading progress...</p> : null}

      {completed && projected ? (
        <section style={{ marginBottom: 28 }}>
          <h2>Requirement progress</h2>
          <p style={{ fontSize: 14, marginBottom: 12 }}>
            Solid bar = completed only. Hatched overlay = projected (completed +
            planned).
          </p>

          <DualProgressRow
            label="Required Areas"
            completedNumerator={completed.areas.completed_areas.length}
            projectedNumerator={projected.areas.completed_areas.length}
            denominator={requiredAreasCount}
          />

          {STREAM_ORDER.map((streamName) => (
            <DualProgressRow
              key={streamName}
              label={streamProgressLabel(streamName)}
              completedNumerator={
                completed.stream_complementary.stream_credits[streamName] ?? 0
              }
              projectedNumerator={
                projected.stream_complementary.stream_credits[streamName] ?? 0
              }
              denominator={STREAM_REQUIRED_CREDITS}
            />
          ))}

          <DualProgressRow
            label={
              activeStream
                ? `Official Stream: ${activeStream}`
                : "Official Stream"
            }
            completedNumerator={officialCompleted?.stream_credits ?? 0}
            projectedNumerator={officialProjected?.stream_credits ?? 0}
            denominator={
              officialProjected?.stream_credit_required ?? STREAM_REQUIRED_CREDITS
            }
          />

          <DualProgressRow
            label="Complementary Credits (official)"
            completedNumerator={officialCompleted?.complementary_credits ?? 0}
            projectedNumerator={officialProjected?.complementary_credits ?? 0}
            denominator={
              officialProjected?.complementary_credit_required ??
              COMPLEMENTARY_REQUIRED_CREDITS
            }
          />

          <DualProgressRow
            label="400+ Credits"
            completedNumerator={completed.level_400_plus.credits}
            projectedNumerator={projected.level_400_plus.credits}
            denominator={LEVEL_400_PLUS_REQUIRED_CREDITS}
          />

          <DualProgressRow
            label="Arts Credits"
            completedNumerator={completed.arts_science.arts_credits}
            projectedNumerator={projected.arts_science.arts_credits}
            denominator={ARTS_REQUIRED_CREDITS}
          />

          <DualProgressRow
            label="Science Credits"
            completedNumerator={completed.arts_science.science_credits}
            projectedNumerator={projected.arts_science.science_credits}
            denominator={SCIENCE_REQUIRED_CREDITS}
          />
        </section>
      ) : null}

      {honours ? (
        <section style={{ marginBottom: 28 }}>
          <h2>Honours Research</h2>
          {completed && projected ? (
            <div style={{ marginBottom: 12 }}>
              <DualProgressRow
                label="Honours Research Requirement"
                completedNumerator={completed.honours_research?.credits ?? 0}
                projectedNumerator={projected.honours_research?.credits ?? 0}
                denominator={
                  projected.honours_research?.required_credits ?? 6
                }
              />
              {projected.honours_research?.satisfied ? (
                <p style={{ fontSize: 14, color: "var(--text-h)", marginTop: -8 }}>
                  Requirement satisfied (
                  {projected.honours_research.credits}/
                  {projected.honours_research.required_credits} credits).
                </p>
              ) : null}
            </div>
          ) : null}
          <CourseAccordion
            title="Honours Research"
            courses={honoursResearchCourses}
            projected={projected}
            overrideErrors={overrideErrors}
            onOverrideAttempt={handleOverrideAttempt}
          />
        </section>
      ) : null}

      <section style={{ marginBottom: 28 }}>
        <h2>Required areas</h2>
        {AREA_ORDER.map((areaName) => (
          <CourseAccordion
            key={areaName}
            title={areaName}
            areaName={areaName}
            courses={coursesByArea.get(areaName) ?? []}
            projected={projected}
            overrideErrors={overrideErrors}
            onOverrideAttempt={handleOverrideAttempt}
          />
        ))}
      </section>

      <section>
        <h2>Streams</h2>
        {STREAM_ORDER.map((streamName) => (
          <CourseAccordion
            key={streamName}
            title={streamName}
            courses={coursesByStream.get(streamName) ?? []}
            projected={projected}
            overrideErrors={overrideErrors}
            onOverrideAttempt={handleOverrideAttempt}
            streamHighlight={streamHighlightFor(streamName)}
          />
        ))}

        <h3 style={{ marginTop: 24, color: "var(--text-h)" }}>Research</h3>
        <CourseAccordion
          title="Research"
          courses={researchCourses}
          projected={projected}
          overrideErrors={overrideErrors}
          onOverrideAttempt={handleOverrideAttempt}
        />
      </section>
    </div>
  );
}

export default Dashboard;
