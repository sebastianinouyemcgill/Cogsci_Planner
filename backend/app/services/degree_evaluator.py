from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Optional, Sequence, Set, Tuple


FacultyName = Literal["Arts", "Science"]
StreamName = str
AreaName = str
BucketOverride = str
COMPLEMENTARY_BUCKET_LABEL = "Complementary"


class InvalidBucketOverrideError(ValueError):
    """Raised when a requested bucket override cannot be honored."""

    def __init__(
        self,
        *,
        course_id: int,
        course_code: str,
        bucket_override: str,
        reason: str,
    ) -> None:
        self.course_id = course_id
        self.course_code = course_code
        self.bucket_override = bucket_override
        self.reason = reason
        super().__init__(
            f"Invalid bucket_override for {course_code} (course_id={course_id}): "
            f"{bucket_override!r} — {reason}"
        )


class InvalidDeclaredStreamError(ValueError):
    """Raised when a declared stream name is not a valid stream."""

    def __init__(self, *, declared_stream: str, eligible_streams: Sequence[str]) -> None:
        self.declared_stream = declared_stream
        self.eligible_streams = list(eligible_streams)
        allowed = ", ".join(eligible_streams) if eligible_streams else "none"
        super().__init__(
            f"Invalid declared_stream {declared_stream!r} — allowed streams: {allowed}"
        )


ELECTIVES_BUCKET_KEY = "electives"


@dataclass(frozen=True)
class CompletedCourse:
    """
    A minimal course representation for pure evaluation logic.

    This interface is intentionally NOT tied to the SQLAlchemy models so the
    service layer can be tested with simple fixtures.

    IMPORTANT (Phase 2 requirement):
    - The arts/science calculator must accept "all completed courses" including
      manually-entered non-major courses. For such courses:
        - `eligible_streams` and `eligible_areas` should be empty lists.
        - only `credits`, `faculty`, and (for 400+) `level` matter.
    """

    id: int
    code: str

    # Credits + level are used for multiple independent requirements.
    credits: int
    level: int

    # Used for Arts/Science totals.
    faculty: FacultyName

    # Used for stream/complementary eligibility.
    eligible_streams: Sequence[StreamName] = ()

    # Used for required cognitive science area completion.
    eligible_areas: Sequence[AreaName] = ()

    # True for seeded courses with no real stream home that should be surfaced
    # as Electives if they are not consumed by an Area.
    elective_only: bool = False

    # When True, Arts/Science credit may be assigned to either faculty bucket
    # during evaluation (whichever benefits the student most).
    flexible_faculty: bool = False


@dataclass(frozen=True)
class CourseAllocationDetail:
    eligible_buckets: List[str]
    allocated_bucket: Optional[str] = None


@dataclass(frozen=True)
class OfficialStreamComplementaryAllocation:
    """
    Official allocation for a declared (or provisionally chosen) stream.

    Separate from the explore-all-streams `StreamComplementaryAllocation`.
    """

    declared_stream: Optional[StreamName]
    stream_is_provisional: bool
    provisional_stream: Optional[StreamName]
    stream_credits: int
    complementary_credits: int
    course_bucket: Dict[int, str]
    course_allocations: Dict[int, CourseAllocationDetail]
    elective_overflow_course_ids: Set[int]


@dataclass(frozen=True)
class StreamComplementaryAllocation:
    """
    Result of allocating courses into the mutually-exclusive buckets:
    - Stream bucket (one course can contribute to multiple streams, but the
      allocation chooses one stream bucket per course)
    - Complementary bucket (also one bucket per course)

    Courses allocated to either bucket are still eligible to satisfy the
    independent 400+ requirement (computed elsewhere as a separate progress
    calculation).
    """

    # course_id -> ("stream:<stream_name>" or "complementary")
    course_bucket: Dict[int, str]

    stream_credits: Dict[StreamName, int]
    complementary_credits: int
    course_allocations: Dict[int, CourseAllocationDetail]


@dataclass(frozen=True)
class AreaAllocation:
    """
    Result of consuming at most one course per required Area.
    """

    # area_name -> course_id
    area_course_ids: Dict[AreaName, int]
    consumed_course_ids: Set[int]

    @property
    def completed_areas(self) -> Set[AreaName]:
        return set(self.area_course_ids)


@dataclass(frozen=True)
class ElectivesAllocation:
    credits: int
    course_ids: List[int]


@dataclass(frozen=True)
class ArtsScienceTotals:
    arts_credits: int
    science_credits: int


@dataclass(frozen=True)
class ProgressSnapshot:
    """
    A container for the individual calculators in this v1 evaluator.
    """

    arts_science: ArtsScienceTotals
    credits_400_plus: int
    eligible_courses_400_plus: List[int]

    # Allocations used by the stream/complementary bucket logic.
    stream_complementary: StreamComplementaryAllocation

    # Official declared/provisional stream + complementary allocation.
    official_stream_complementary: OfficialStreamComplementaryAllocation

    # Area completion consumes one deterministic course per area.
    completed_areas: Set[AreaName]
    area_course_ids: Dict[AreaName, int]

    # Elective-only courses that were not consumed by an Area.
    electives: ElectivesAllocation


def calculate_arts_science_totals(
    all_completed_courses: Iterable[CompletedCourse],
) -> ArtsScienceTotals:
    """
    Calculate Arts/Science totals from *all* completed courses (CogSci + non-major).

    Courses with `flexible_faculty=True` are assigned to whichever bucket is
    currently lower so the student gets the most benefit (e.g. COGS 444 toward
    Arts when Arts credits are harder to fill).
    """

    fixed_arts = 0
    fixed_science = 0
    flexible_courses: List[CompletedCourse] = []

    for course in all_completed_courses:
        if course.flexible_faculty:
            flexible_courses.append(course)
            continue
        if course.faculty == "Arts":
            fixed_arts += course.credits
        elif course.faculty == "Science":
            fixed_science += course.credits
        else:
            raise ValueError(f"Unknown faculty: {course.faculty}")

    arts = fixed_arts
    science = fixed_science
    for course in sorted(flexible_courses, key=lambda c: (c.code, c.id)):
        if arts <= science:
            arts += course.credits
        else:
            science += course.credits

    return ArtsScienceTotals(arts_credits=arts, science_credits=science)


def calculate_400_plus_progress(
    all_completed_courses: Iterable[CompletedCourse],
    *,
    level_threshold: int = 400,
) -> Tuple[int, List[int]]:
    """
    Independent 400+ progress calculation.

    Note: this is not tied to stream/complementary allocation.
    """

    credits = 0
    eligible: List[int] = []
    for course in all_completed_courses:
        if course.level >= level_threshold:
            credits += course.credits
            eligible.append(course.id)
    return credits, eligible


def course_eligible_buckets(
    course: CompletedCourse,
    *,
    eligible_streams: Sequence[StreamName],
) -> List[str]:
    """
    Buckets a course may be assigned to in the stream/complementary pool.
    """

    stream_buckets = [s for s in course.eligible_streams if s in eligible_streams]
    if not stream_buckets:
        return []
    return sorted(
        [*stream_buckets, COMPLEMENTARY_BUCKET_LABEL],
        key=lambda bucket: (bucket == COMPLEMENTARY_BUCKET_LABEL, bucket),
    )


def _normalize_override_to_bucket_key(
    bucket_override: BucketOverride,
    course: CompletedCourse,
    *,
    eligible_streams: Sequence[StreamName],
) -> str:
    if bucket_override == COMPLEMENTARY_BUCKET_LABEL:
        if not course_eligible_buckets(course, eligible_streams=eligible_streams):
            raise InvalidBucketOverrideError(
                course_id=course.id,
                course_code=course.code,
                bucket_override=bucket_override,
                reason="course is not in the stream/complementary pool",
            )
        return "complementary"

    if (
        bucket_override in eligible_streams
        and bucket_override in course.eligible_streams
    ):
        return f"stream:{bucket_override}"

    allowed = course_eligible_buckets(course, eligible_streams=eligible_streams)
    allowed_text = ", ".join(allowed) if allowed else "none"
    raise InvalidBucketOverrideError(
        course_id=course.id,
        course_code=course.code,
        bucket_override=bucket_override,
        reason=f"allowed buckets are: {allowed_text}",
    )


def validate_bucket_overrides(
    *,
    all_completed_courses: Sequence[CompletedCourse],
    remaining_courses: Sequence[CompletedCourse],
    area_consumed_course_ids: Set[int],
    bucket_overrides: Dict[int, BucketOverride],
    eligible_streams: Sequence[StreamName],
) -> None:
    courses_by_id = {course.id: course for course in all_completed_courses}
    pool_course_ids = {
        course.id
        for course in remaining_courses
        if course_eligible_buckets(course, eligible_streams=eligible_streams)
    }

    for course_id, bucket_override in bucket_overrides.items():
        course = courses_by_id.get(course_id)
        if course is None:
            raise InvalidBucketOverrideError(
                course_id=course_id,
                course_code="?",
                bucket_override=bucket_override,
                reason="course is not in the evaluation set",
            )
        if course_id in area_consumed_course_ids:
            raise InvalidBucketOverrideError(
                course_id=course_id,
                course_code=course.code,
                bucket_override=bucket_override,
                reason="course is consumed by an area requirement",
            )
        if course_id not in pool_course_ids:
            raise InvalidBucketOverrideError(
                course_id=course_id,
                course_code=course.code,
                bucket_override=bucket_override,
                reason="course is not in the stream/complementary pool",
            )
        _normalize_override_to_bucket_key(
            bucket_override,
            course,
            eligible_streams=eligible_streams,
        )


def allocate_streams_and_complementary_greedy_v1(
    courses: Sequence[CompletedCourse],
    *,
    # Stream requirement credits (e.g. 18).
    stream_credit_required: int,
    # Complementary requirement credits (e.g. 12).
    complementary_credit_required: int,
    eligible_streams: Sequence[StreamName],
    bucket_overrides: Optional[Dict[int, BucketOverride]] = None,
) -> StreamComplementaryAllocation:
    """
    Greedy v1 allocation strategy (documented heuristic).

    Allocation strategy (v1):
    - Consider only courses that have `eligible_streams` non-empty. These are
      eligible for BOTH:
        - any of their eligible stream buckets
        - the complementary bucket
    - For each course, if it is eligible for multiple streams/complementary:
      1. Prefer stream buckets that are *partially finished* (i.e., stream
         credits allocated so far < stream_credit_required).
      2. Among partially finished eligible streams, choose the one with the
         LEAST credits remaining (closest to completion).
      3. If there are no partially-finished eligible streams left for that
         course, allocate to complementary (if complementary still needs
         credits).

    This is intentionally a heuristic and is NOT provably globally optimal.
    Candidate for a later phase: a constraint solver (e.g. OR-Tools) or an
    integer programming formulation once we start seeing cases where greedy
    under-allocates compared to a global optimum.
    """

    overrides = bucket_overrides or {}

    # Initialize per-stream credit tallies.
    stream_credits: Dict[StreamName, int] = {s: 0 for s in eligible_streams}
    complementary_credits = 0

    course_bucket: Dict[int, str] = {}
    course_allocations: Dict[int, CourseAllocationDetail] = {}

    pool_courses = [
        course
        for course in courses
        if course_eligible_buckets(course, eligible_streams=eligible_streams)
    ]
    for course in pool_courses:
        course_allocations[course.id] = CourseAllocationDetail(
            eligible_buckets=course_eligible_buckets(
                course, eligible_streams=eligible_streams
            )
        )

    def apply_bucket(course: CompletedCourse, bucket_key: str) -> None:
        nonlocal complementary_credits
        course_bucket[course.id] = bucket_key
        detail = course_allocations[course.id]
        course_allocations[course.id] = CourseAllocationDetail(
            eligible_buckets=detail.eligible_buckets,
            allocated_bucket=bucket_key,
        )
        if bucket_key == "complementary":
            complementary_credits += course.credits
            return
        stream_name = bucket_key.removeprefix("stream:")
        stream_credits[stream_name] += course.credits

    # Pin explicit overrides before running the greedy heuristic.
    auto_allocate_courses: List[CompletedCourse] = []
    for course in pool_courses:
        override = overrides.get(course.id)
        if override is not None:
            bucket_key = _normalize_override_to_bucket_key(
                override,
                course,
                eligible_streams=eligible_streams,
            )
            apply_bucket(course, bucket_key)
            continue
        auto_allocate_courses.append(course)

    def stream_remaining(stream: StreamName) -> int:
        return max(0, stream_credit_required - stream_credits.get(stream, 0))

    def is_stream_partially_finished(stream: StreamName) -> bool:
        return stream_remaining(stream) > 0

    for course in auto_allocate_courses:
        candidates_streams = [s for s in course.eligible_streams if s in stream_credits]
        if not candidates_streams:
            continue

        partially_finished = [
            s for s in candidates_streams if is_stream_partially_finished(s)
        ]
        chosen: Optional[StreamName] = None
        if partially_finished:
            chosen = sorted(partially_finished, key=lambda s: (stream_remaining(s), s))[0]

        if chosen is not None:
            apply_bucket(course, f"stream:{chosen}")
            continue

        if complementary_credits < complementary_credit_required:
            apply_bucket(course, "complementary")
            continue

    return StreamComplementaryAllocation(
        course_bucket=course_bucket,
        stream_credits=stream_credits,
        complementary_credits=complementary_credits,
        course_allocations=course_allocations,
    )


def _official_stream_credits_for_bucket(
    courses: Sequence[CompletedCourse],
    course_bucket: Dict[int, str],
    *,
    primary_stream: StreamName,
) -> int:
    primary_key = f"stream:{primary_stream}"
    return sum(
        course.credits
        for course in courses
        if course_bucket.get(course.id) == primary_key
    )


def _official_complementary_credits_for_bucket(
    courses: Sequence[CompletedCourse],
    course_bucket: Dict[int, str],
) -> int:
    return sum(
        course.credits
        for course in courses
        if course_bucket.get(course.id) == "complementary"
    )


def allocate_official_stream_complementary_v1(
    courses: Sequence[CompletedCourse],
    *,
    primary_stream: StreamName,
    stream_credit_required: int,
    complementary_credit_required: int,
    eligible_streams: Sequence[StreamName],
    bucket_overrides: Optional[Dict[int, BucketOverride]] = None,
) -> OfficialStreamComplementaryAllocation:
    """
    Official allocation for a declared or provisionally chosen primary stream.

    - Courses eligible for `primary_stream` fill that stream bucket first (up to
      the stream cap for auto-allocated courses).
    - Remaining pool courses fill Complementary (up to its cap for auto).
    - Further pool overflow flows to the shared Electives bucket.
    - Explicit bucket overrides are honored first and may exceed caps.
    """

    overrides = bucket_overrides or {}
    course_bucket: Dict[int, str] = {}
    course_allocations: Dict[int, CourseAllocationDetail] = {}

    pool_courses = [
        course
        for course in courses
        if course_eligible_buckets(course, eligible_streams=eligible_streams)
    ]
    for course in pool_courses:
        course_allocations[course.id] = CourseAllocationDetail(
            eligible_buckets=course_eligible_buckets(
                course, eligible_streams=eligible_streams
            )
        )

    stream_credits = 0
    complementary_credits = 0

    def apply_bucket(course: CompletedCourse, bucket_key: str) -> None:
        nonlocal stream_credits, complementary_credits
        course_bucket[course.id] = bucket_key
        detail = course_allocations[course.id]
        course_allocations[course.id] = CourseAllocationDetail(
            eligible_buckets=detail.eligible_buckets,
            allocated_bucket=bucket_key,
        )

    # Pin explicit overrides before running the official heuristic.
    auto_allocate_courses: List[CompletedCourse] = []
    for course in pool_courses:
        override = overrides.get(course.id)
        if override is not None:
            bucket_key = _normalize_override_to_bucket_key(
                override,
                course,
                eligible_streams=eligible_streams,
            )
            apply_bucket(course, bucket_key)
            continue
        auto_allocate_courses.append(course)

    primary_key = f"stream:{primary_stream}"
    stream_credits = _official_stream_credits_for_bucket(
        pool_courses, course_bucket, primary_stream=primary_stream
    )
    complementary_credits = _official_complementary_credits_for_bucket(
        pool_courses, course_bucket
    )

    for course in sorted(auto_allocate_courses, key=lambda c: (c.code, c.id)):
        if course.id in course_bucket:
            continue

        if (
            primary_stream in course.eligible_streams
            and stream_credits < stream_credit_required
        ):
            apply_bucket(course, primary_key)
            stream_credits += course.credits
            continue

        if complementary_credits < complementary_credit_required:
            apply_bucket(course, "complementary")
            complementary_credits += course.credits
            continue

        apply_bucket(course, ELECTIVES_BUCKET_KEY)

    elective_overflow_course_ids = {
        course.id
        for course in pool_courses
        if course_bucket.get(course.id) == ELECTIVES_BUCKET_KEY
    }

    return OfficialStreamComplementaryAllocation(
        declared_stream=primary_stream,
        stream_is_provisional=False,
        provisional_stream=None,
        stream_credits=_official_stream_credits_for_bucket(
            pool_courses, course_bucket, primary_stream=primary_stream
        ),
        complementary_credits=_official_complementary_credits_for_bucket(
            pool_courses, course_bucket
        ),
        course_bucket=course_bucket,
        course_allocations=course_allocations,
        elective_overflow_course_ids=elective_overflow_course_ids,
    )


def _official_completion_score(
    allocation: OfficialStreamComplementaryAllocation,
    *,
    stream_credit_required: int,
    complementary_credit_required: int,
) -> Tuple[int, int, str]:
    capped_stream = min(allocation.stream_credits, stream_credit_required)
    capped_comp = min(
        allocation.complementary_credits, complementary_credit_required
    )
    return (
        capped_stream + capped_comp,
        allocation.stream_credits,
        allocation.declared_stream or "",
    )


def allocate_official_with_declared_or_provisional_stream(
    courses: Sequence[CompletedCourse],
    *,
    declared_stream: Optional[StreamName],
    stream_credit_required: int,
    complementary_credit_required: int,
    eligible_streams: Sequence[StreamName],
    bucket_overrides: Optional[Dict[int, BucketOverride]] = None,
) -> OfficialStreamComplementaryAllocation:
    """
    Run official allocation for an explicit declared stream, or pick the
    provisional stream that maximizes combined Stream+Complementary progress.
    """

    if declared_stream is not None:
        if declared_stream not in eligible_streams:
            raise InvalidDeclaredStreamError(
                declared_stream=declared_stream,
                eligible_streams=eligible_streams,
            )
        result = allocate_official_stream_complementary_v1(
            courses,
            primary_stream=declared_stream,
            stream_credit_required=stream_credit_required,
            complementary_credit_required=complementary_credit_required,
            eligible_streams=eligible_streams,
            bucket_overrides=bucket_overrides,
        )
        return OfficialStreamComplementaryAllocation(
            declared_stream=declared_stream,
            stream_is_provisional=False,
            provisional_stream=None,
            stream_credits=result.stream_credits,
            complementary_credits=result.complementary_credits,
            course_bucket=result.course_bucket,
            course_allocations=result.course_allocations,
            elective_overflow_course_ids=result.elective_overflow_course_ids,
        )

    best_allocation: Optional[OfficialStreamComplementaryAllocation] = None
    best_score: Tuple[int, int, str] = (-1, -1, "")

    for stream in eligible_streams:
        candidate = allocate_official_stream_complementary_v1(
            courses,
            primary_stream=stream,
            stream_credit_required=stream_credit_required,
            complementary_credit_required=complementary_credit_required,
            eligible_streams=eligible_streams,
            bucket_overrides=bucket_overrides,
        )
        score = _official_completion_score(
            candidate,
            stream_credit_required=stream_credit_required,
            complementary_credit_required=complementary_credit_required,
        )
        if score > best_score:
            best_score = score
            best_allocation = candidate

    if best_allocation is None:
        return OfficialStreamComplementaryAllocation(
            declared_stream=None,
            stream_is_provisional=True,
            provisional_stream=None,
            stream_credits=0,
            complementary_credits=0,
            course_bucket={},
            course_allocations={},
            elective_overflow_course_ids=set(),
        )

    return OfficialStreamComplementaryAllocation(
        declared_stream=None,
        stream_is_provisional=True,
        provisional_stream=best_allocation.declared_stream,
        stream_credits=best_allocation.stream_credits,
        complementary_credits=best_allocation.complementary_credits,
        course_bucket=best_allocation.course_bucket,
        course_allocations=best_allocation.course_allocations,
        elective_overflow_course_ids=best_allocation.elective_overflow_course_ids,
    )


def allocate_areas_greedy_v1(
    all_completed_courses: Sequence[CompletedCourse],
    *,
    required_areas: Sequence[AreaName],
) -> AreaAllocation:
    """
    Choose exactly one course for each completed Area.

    Deterministic tie-break: lowest course code, then ID. A course can satisfy
    at most one Area.
    """

    area_course_ids: Dict[AreaName, int] = {}
    consumed_course_ids: Set[int] = set()

    for area in required_areas:
        candidates = sorted(
            (
                course
                for course in all_completed_courses
                if course.id not in consumed_course_ids
                and area in course.eligible_areas
            ),
            key=lambda course: (course.code, course.id),
        )
        if not candidates:
            continue

        chosen = candidates[0]
        area_course_ids[area] = chosen.id
        consumed_course_ids.add(chosen.id)

    return AreaAllocation(
        area_course_ids=area_course_ids,
        consumed_course_ids=consumed_course_ids,
    )


def calculate_completed_areas(
    all_completed_courses: Sequence[CompletedCourse],
    *,
    required_areas: Sequence[AreaName],
) -> Set[AreaName]:
    """
    Compatibility helper for callers that only need completed Area names.
    """

    return allocate_areas_greedy_v1(
        all_completed_courses,
        required_areas=required_areas,
    ).completed_areas


def allocate_electives(
    courses: Iterable[CompletedCourse],
    *,
    official_elective_overflow_ids: Optional[Set[int]] = None,
) -> ElectivesAllocation:
    """
    Track elective-only courses and official stream-pool overflow so credits
    remain visible in a single Electives bucket.
    """

    overflow_ids = official_elective_overflow_ids or set()
    credits = 0
    course_ids: List[int] = []
    for course in sorted(courses, key=lambda c: (c.code, c.id)):
        if course.elective_only:
            credits += course.credits
            course_ids.append(course.id)
        elif course.id in overflow_ids:
            credits += course.credits
            course_ids.append(course.id)
    return ElectivesAllocation(credits=credits, course_ids=course_ids)


@dataclass(frozen=True)
class DualProgressSnapshot:
    """Completed-only and completed+planned progress from the same evaluator."""

    completed: ProgressSnapshot
    projected: ProgressSnapshot


def evaluate_degree_progress_completed_and_projected(
    *,
    completed_only_courses: Sequence[CompletedCourse],
    completed_and_planned_courses: Sequence[CompletedCourse],
    required_areas: Sequence[AreaName],
    eligible_streams: Sequence[StreamName],
    stream_credit_required: int,
    complementary_credit_required: int,
    level_threshold: int = 400,
    declared_stream: Optional[StreamName] = None,
    completed_bucket_overrides: Optional[Dict[int, BucketOverride]] = None,
    projected_bucket_overrides: Optional[Dict[int, BucketOverride]] = None,
) -> DualProgressSnapshot:
    """
    Run the v1 greedy evaluator twice:
    1. `completed` — courses with status == completed (plus manual entries).
    2. `projected` — completed OR planned courses combined.
    """

    common_kwargs = {
        "required_areas": required_areas,
        "eligible_streams": eligible_streams,
        "stream_credit_required": stream_credit_required,
        "complementary_credit_required": complementary_credit_required,
        "level_threshold": level_threshold,
        "declared_stream": declared_stream,
    }

    return DualProgressSnapshot(
        completed=evaluate_degree_progress_greedy_v1(
            all_completed_courses=completed_only_courses,
            bucket_overrides=completed_bucket_overrides,
            **common_kwargs,
        ),
        projected=evaluate_degree_progress_greedy_v1(
            all_completed_courses=completed_and_planned_courses,
            bucket_overrides=projected_bucket_overrides,
            **common_kwargs,
        ),
    )


def evaluate_degree_progress_greedy_v1(
    *,
    all_completed_courses: Sequence[CompletedCourse],
    required_areas: Sequence[AreaName],
    eligible_streams: Sequence[StreamName],
    stream_credit_required: int,
    complementary_credit_required: int,
    level_threshold: int = 400,
    declared_stream: Optional[StreamName] = None,
    bucket_overrides: Optional[Dict[int, BucketOverride]] = None,
) -> ProgressSnapshot:
    """
    v1 evaluator wrapper combining:
    - Arts/Science totals
    - 400+ progress (independent)
    - stream/complementary greedy allocation
    - required area completion

    This stays strictly in the service layer: no routers / no DB operations.
    """

    arts_science = calculate_arts_science_totals(all_completed_courses)
    credits_400_plus, eligible_ids_400_plus = calculate_400_plus_progress(
        all_completed_courses, level_threshold=level_threshold
    )

    area_allocation = allocate_areas_greedy_v1(
        all_completed_courses, required_areas=required_areas
    )

    # Area-consumed courses do not also flow into the mutually-exclusive
    # stream/complementary/electives buckets.
    remaining_courses = [
        course
        for course in all_completed_courses
        if course.id not in area_allocation.consumed_course_ids
    ]

    overrides = bucket_overrides or {}
    validate_bucket_overrides(
        all_completed_courses=all_completed_courses,
        remaining_courses=remaining_courses,
        area_consumed_course_ids=area_allocation.consumed_course_ids,
        bucket_overrides=overrides,
        eligible_streams=eligible_streams,
    )

    stream_comp = allocate_streams_and_complementary_greedy_v1(
        remaining_courses,
        stream_credit_required=stream_credit_required,
        complementary_credit_required=complementary_credit_required,
        eligible_streams=eligible_streams,
        bucket_overrides=overrides,
    )

    official_stream_comp = allocate_official_with_declared_or_provisional_stream(
        remaining_courses,
        declared_stream=declared_stream,
        stream_credit_required=stream_credit_required,
        complementary_credit_required=complementary_credit_required,
        eligible_streams=eligible_streams,
        bucket_overrides=overrides,
    )

    electives = allocate_electives(
        remaining_courses,
        official_elective_overflow_ids=official_stream_comp.elective_overflow_course_ids,
    )

    return ProgressSnapshot(
        arts_science=arts_science,
        credits_400_plus=credits_400_plus,
        eligible_courses_400_plus=eligible_ids_400_plus,
        stream_complementary=stream_comp,
        official_stream_complementary=official_stream_comp,
        completed_areas=area_allocation.completed_areas,
        area_course_ids=area_allocation.area_course_ids,
        electives=electives,
    )

