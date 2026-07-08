from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Optional, Sequence, Set, Tuple


FacultyName = Literal["Arts", "Science"]
StreamName = str
AreaName = str


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

    # Area completion is computed without consuming credits from other
    # requirement buckets in the progress calculations.
    completed_areas: Set[AreaName]


def calculate_arts_science_totals(
    all_completed_courses: Iterable[CompletedCourse],
) -> ArtsScienceTotals:
    """
    Calculate Arts/Science totals from *all* completed courses (CogSci + non-major).
    """

    arts = 0
    science = 0
    for course in all_completed_courses:
        if course.faculty == "Arts":
            arts += course.credits
        elif course.faculty == "Science":
            science += course.credits
        else:
            # Defensive: type should prevent this.
            raise ValueError(f"Unknown faculty: {course.faculty}")
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


def allocate_streams_and_complementary_greedy_v1(
    courses: Sequence[CompletedCourse],
    *,
    # Stream requirement credits (e.g. 18).
    stream_credit_required: int,
    # Complementary requirement credits (e.g. 12).
    complementary_credit_required: int,
    eligible_streams: Sequence[StreamName],
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

    # Initialize per-stream credit tallies.
    stream_credits: Dict[StreamName, int] = {s: 0 for s in eligible_streams}
    complementary_credits = 0

    course_bucket: Dict[int, str] = {}

    def stream_remaining(stream: StreamName) -> int:
        return max(0, stream_credit_required - stream_credits.get(stream, 0))

    def is_stream_partially_finished(stream: StreamName) -> bool:
        return stream_remaining(stream) > 0

    for course in courses:
        # Complementary's pool is the SAME pool as streams: any course with
        # eligible stream tags can go to streams or complementary buckets.
        candidates_streams = [s for s in course.eligible_streams if s in stream_credits]

        # IMPORTANT: In v1, stream/complementary allocation does not exclude
        # courses that are also eligible for a required Area.
        # - Area completion is computed separately as a presence check.
        # - This avoids an accidental gap when the course catalog expands.
        # Phase 2 is where we can enforce any future mutual-exclusivity policy
        # across Area vs Stream if desired.
        if not candidates_streams:
            continue

        # 1) Try partially-finished streams first.
        partially_finished = [s for s in candidates_streams if is_stream_partially_finished(s)]
        chosen: Optional[StreamName] = None
        if partially_finished:
            # 2) Choose least credits remaining.
            chosen = sorted(partially_finished, key=lambda s: (stream_remaining(s), s))[0]

        if chosen is not None:
            bucket = f"stream:{chosen}"
            course_bucket[course.id] = bucket
            stream_credits[chosen] += course.credits
            continue

        # 3) No partially-finished eligible streams remain => complementary.
        if complementary_credits < complementary_credit_required:
            course_bucket[course.id] = "complementary"
            complementary_credits += course.credits
            continue

        # If complementary is also satisfied, we leave the course unallocated
        # (it still may satisfy independent requirements like 400+).

    return StreamComplementaryAllocation(
        course_bucket=course_bucket,
        stream_credits=stream_credits,
        complementary_credits=complementary_credits,
    )


def calculate_completed_areas(
    all_completed_courses: Iterable[CompletedCourse],
    *,
    required_areas: Sequence[AreaName],
) -> Set[AreaName]:
    """
    Compute which required areas are complete.

    Area completion is a progress calculation and does not consume credits from
    stream/complementary buckets.

    Area/stream overlap clarification:
    - If in the expanded course catalog a course is eligible for BOTH an Area
      and a Stream, this function will still mark the Area complete if the
      course appears in `all_completed_courses`.
    - Stream/complementary allocation happens independently and should NOT
      silently ignore area/stream overlaps; the allocation model will be
      explicitly decided in Phase 2 allocation logic.

    For now, this function is purely a presence check for each required area.
    """

    required: Set[AreaName] = set(required_areas)
    completed: Set[AreaName] = set()
    for course in all_completed_courses:
        for area in course.eligible_areas:
            if area in required:
                completed.add(area)
    return completed


def evaluate_degree_progress_greedy_v1(
    *,
    all_completed_courses: Sequence[CompletedCourse],
    required_areas: Sequence[AreaName],
    eligible_streams: Sequence[StreamName],
    stream_credit_required: int,
    complementary_credit_required: int,
    level_threshold: int = 400,
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

    # Stream/complementary allocation operates on the full list, but the
    # allocator itself only considers stream-tagged courses.
    stream_comp = allocate_streams_and_complementary_greedy_v1(
        all_completed_courses,
        stream_credit_required=stream_credit_required,
        complementary_credit_required=complementary_credit_required,
        eligible_streams=eligible_streams,
    )

    completed_areas = calculate_completed_areas(
        all_completed_courses, required_areas=required_areas
    )

    return ProgressSnapshot(
        arts_science=arts_science,
        credits_400_plus=credits_400_plus,
        eligible_courses_400_plus=eligible_ids_400_plus,
        stream_complementary=stream_comp,
        completed_areas=completed_areas,
    )

