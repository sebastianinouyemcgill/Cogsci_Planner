from app.services.degree_evaluator import (
    CompletedCourse,
    allocate_streams_and_complementary_greedy_v1,
    calculate_400_plus_progress,
    calculate_arts_science_totals,
    calculate_completed_areas,
    evaluate_degree_progress_greedy_v1,
)


def test_arts_science_totals_counts_all_completed_courses():
    # Includes both CogSci and manually-entered non-major courses.
    courses = [
        CompletedCourse(
            id=1,
            code="COMP 551",
            credits=4,
            level=551,
            faculty="Science",
            eligible_streams=("Computer Science",),
            eligible_areas=(),
        ),
        CompletedCourse(
            id=2,
            code="PHIL 210",
            credits=3,
            level=210,
            faculty="Arts",
            eligible_streams=(),
            eligible_areas=("Logic",),
        ),
        CompletedCourse(
            id=3,
            code="HIST 200",
            credits=3,
            level=200,
            faculty="Arts",
            eligible_streams=(),
            eligible_areas=(),
        ),
    ]

    totals = calculate_arts_science_totals(courses)
    assert totals.arts_credits == 6  # PHIL210 + HIST200
    assert totals.science_credits == 4  # COMP551


def test_allocate_streams_and_complementary_greedy_v1_prefers_partially_finished_streams():
    # Two streams, each needs 5 credits.
    eligible_streams = ["StreamA", "StreamB"]
    stream_required = 5
    complementary_required = 4

    # Order is important: allocation is greedy and sequential.
    courses = [
        # Eligible for both, both partially-finished at start => tie-break by
        # stream name: StreamA.
        CompletedCourse(
            id=1,
            code="C1",
            credits=2,
            level=300,
            faculty="Science",
            eligible_streams=("StreamA", "StreamB"),
        ),
        # Still eligible for both; StreamA remaining is now smaller => StreamA.
        CompletedCourse(
            id=2,
            code="C2",
            credits=3,
            level=300,
            faculty="Science",
            eligible_streams=("StreamA", "StreamB"),
        ),
        # StreamA now complete; only StreamB partially finished => StreamB.
        CompletedCourse(
            id=3,
            code="C3",
            credits=3,
            level=300,
            faculty="Science",
            eligible_streams=("StreamA", "StreamB"),
        ),
        # StreamA complete; StreamB partially finished => StreamB.
        CompletedCourse(
            id=4,
            code="C4",
            credits=2,
            level=300,
            faculty="Science",
            eligible_streams=("StreamA", "StreamB"),
        ),
        # Both streams complete; next eligible course must go to complementary
        # until it is filled.
        CompletedCourse(
            id=5,
            code="C5",
            credits=2,
            level=300,
            faculty="Science",
            eligible_streams=("StreamA", "StreamB"),
        ),
    ]

    result = allocate_streams_and_complementary_greedy_v1(
        courses,
        stream_credit_required=stream_required,
        complementary_credit_required=complementary_required,
        eligible_streams=eligible_streams,
    )

    # Stream assignments.
    assert result.course_bucket[1] == "stream:StreamA"
    assert result.course_bucket[2] == "stream:StreamA"
    assert result.course_bucket[3] == "stream:StreamB"

    # StreamB fills from C4.
    assert result.course_bucket[4] == "stream:StreamB"

    # Complementary assignment once both streams are complete.
    assert result.course_bucket[5] == "complementary"

    assert result.stream_credits["StreamA"] == 5
    assert result.stream_credits["StreamB"] == 5
    assert result.complementary_credits == 2


def test_area_completion_is_independent_of_stream_eligibility():
    courses = [
        CompletedCourse(
            id=1,
            code="X",
            credits=3,
            level=450,
            faculty="Science",
            eligible_streams=("Computer Science",),
            eligible_areas=("Artificial Intelligence",),
        ),
    ]

    completed = calculate_completed_areas(
        courses, required_areas=["Artificial Intelligence"]
    )
    assert completed == {"Artificial Intelligence"}


def test_evaluate_degree_progress_greedy_v1_computes_all_components():
    courses = [
        CompletedCourse(
            id=1,
            code="A",
            credits=4,
            level=420,
            faculty="Science",
            eligible_streams=("S1",),
            eligible_areas=("Area1",),
        ),
        CompletedCourse(
            id=2,
            code="B",
            credits=3,
            level=210,
            faculty="Arts",
            eligible_streams=("S1",),
            eligible_areas=("Area2",),
        ),
    ]

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=courses,
        required_areas=["Area1", "Area2"],
        eligible_streams=["S1"],
        stream_credit_required=5,
        complementary_credit_required=6,
        level_threshold=400,
    )

    assert snapshot.arts_science.arts_credits == 3
    assert snapshot.arts_science.science_credits == 4

    # 400+ only from A.
    assert snapshot.credits_400_plus == 4
    assert snapshot.eligible_courses_400_plus == [1]

    assert snapshot.completed_areas == {"Area1", "Area2"}
    assert snapshot.stream_complementary.course_bucket[1] == "stream:S1"

