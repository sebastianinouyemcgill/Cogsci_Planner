import type { Course } from "@/types/course";
import type {
  CourseBucketAllocation,
  RequirementProgressBreakdown,
} from "@/types/requirement";

export const STREAM_REQUIRED_CREDITS = 18;
export const COMPLEMENTARY_REQUIRED_CREDITS = 12;
export const LEVEL_400_PLUS_REQUIRED_CREDITS = 15;
export const ARTS_REQUIRED_CREDITS = 21;
export const SCIENCE_REQUIRED_CREDITS = 21;
export const STANDARD_DEGREE_CREDITS = 54;
export const HONOURS_DEGREE_CREDITS = 60;

export const STREAM_ORDER = [
  "Computer Science",
  "Neuroscience",
  "Psychology",
  "Linguistics",
  "Philosophy",
] as const;

export const AREA_ORDER = [
  "Neuroscience (Required)",
  "Logic",
  "Statistics",
  "Computer Science Foundations",
  "Linguistics Foundations",
  "Philosophy Foundations",
  "Neuroscience Foundations",
  "Psychology Foundations",
] as const;

export const COGS_401_CODE = "COGS 401";
export const COGS_444_CODE = "COGS 444";

export function ratio(value: number, target: number) {
  if (target <= 0) return 0;
  return Math.min(1, value / target);
}

export function activeStreamName(
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

export function overallCompletionPct(
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

export function groupCoursesByName(
  courses: Course[],
  names: readonly string[],
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

export function courseAllocation(
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

export function formatBucketLabel(bucket: string | null | undefined): string {
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

export function isElectiveCourse(
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

export function shortAreaName(areaName: string): string {
  return areaName.replace(" Foundations", "").replace(" (Required)", "");
}

export function streamHighlightFor(
  streamName: string,
  declaredStream: string | null,
  officialProjected: RequirementProgressBreakdown["official_stream_complementary"]
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
