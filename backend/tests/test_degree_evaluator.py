from app.services.degree_evaluator import (
    CompletedCourse,
    InvalidBucketOverrideError,
    allocate_official_with_declared_or_provisional_stream,
    allocate_streams_and_complementary_greedy_v1,
    calculate_400_plus_progress,
    calculate_arts_science_totals,
    calculate_completed_areas,
    evaluate_degree_progress_completed_and_projected,
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
    assert snapshot.area_course_ids == {"Area1": 1, "Area2": 2}
    assert snapshot.stream_complementary.stream_credits["S1"] == 0
    assert snapshot.stream_complementary.course_bucket == {}


def test_evaluate_degree_progress_completed_and_projected_runs_both_views():
    completed_only = [
        CompletedCourse(
            id=1,
            code="A",
            credits=4,
            level=420,
            faculty="Science",
            eligible_streams=("S1",),
            eligible_areas=("Area1",),
        ),
    ]
    completed_and_planned = [
        *completed_only,
        CompletedCourse(
            id=2,
            code="B",
            credits=3,
            level=450,
            faculty="Science",
            eligible_streams=("S1",),
            eligible_areas=("Area2",),
        ),
    ]

    dual = evaluate_degree_progress_completed_and_projected(
        completed_only_courses=completed_only,
        completed_and_planned_courses=completed_and_planned,
        required_areas=["Area1", "Area2"],
        eligible_streams=["S1"],
        stream_credit_required=5,
        complementary_credit_required=6,
        level_threshold=400,
    )

    assert dual.completed.credits_400_plus == 4
    assert dual.completed.completed_areas == {"Area1"}
    assert dual.completed.stream_complementary.stream_credits["S1"] == 0

    assert dual.projected.credits_400_plus == 7
    assert dual.projected.completed_areas == {"Area1", "Area2"}
    assert dual.projected.stream_complementary.stream_credits["S1"] == 0

    assert dual.completed != dual.projected


def test_extra_area_course_with_stream_mapping_flows_to_stream_pool():
    courses = [
        CompletedCourse(
            id=202,
            code="COMP 202",
            credits=3,
            level=202,
            faculty="Science",
            eligible_streams=("Computer Science",),
            eligible_areas=("Computer Science Foundations",),
        ),
        CompletedCourse(
            id=250,
            code="COMP 250",
            credits=3,
            level=250,
            faculty="Science",
            eligible_streams=("Computer Science",),
            eligible_areas=("Computer Science Foundations",),
        ),
    ]

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=courses,
        required_areas=["Computer Science Foundations"],
        eligible_streams=["Computer Science"],
        stream_credit_required=18,
        complementary_credit_required=12,
        level_threshold=400,
    )

    assert snapshot.completed_areas == {"Computer Science Foundations"}
    assert snapshot.area_course_ids == {"Computer Science Foundations": 202}
    assert (
        snapshot.stream_complementary.stream_credits["Computer Science"] == 3
    )
    assert snapshot.stream_complementary.course_bucket[250] == "stream:Computer Science"
    assert 202 not in snapshot.stream_complementary.course_bucket
    assert snapshot.electives.credits == 0
    assert snapshot.electives.course_ids == []


def test_extra_area_course_without_stream_mapping_flows_to_electives():
    courses = [
        CompletedCourse(
            id=203,
            code="MATH 203",
            credits=3,
            level=203,
            faculty="Science",
            eligible_streams=(),
            eligible_areas=("Statistics",),
            elective_only=True,
        ),
        CompletedCourse(
            id=323,
            code="MATH 323",
            credits=3,
            level=323,
            faculty="Science",
            eligible_streams=(),
            eligible_areas=("Statistics",),
            elective_only=True,
        ),
    ]

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=courses,
        required_areas=["Statistics"],
        eligible_streams=["Computer Science"],
        stream_credit_required=18,
        complementary_credit_required=12,
        level_threshold=400,
    )

    assert snapshot.completed_areas == {"Statistics"}
    assert snapshot.area_course_ids == {"Statistics": 203}
    assert snapshot.electives.credits == 3
    assert snapshot.electives.course_ids == [323]
    assert snapshot.stream_complementary.stream_credits["Computer Science"] == 0
    assert snapshot.stream_complementary.course_bucket == {}


def test_invalid_bucket_override_is_rejected():
    courses = [
        CompletedCourse(
            id=1,
            code="COMP 551",
            credits=4,
            level=551,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
    ]

    try:
        evaluate_degree_progress_greedy_v1(
            all_completed_courses=courses,
            required_areas=[],
            eligible_streams=["Computer Science", "Psychology"],
            stream_credit_required=18,
            complementary_credit_required=12,
            bucket_overrides={1: "Psychology"},
        )
    except InvalidBucketOverrideError as exc:
        assert "COMP 551" in str(exc)
        assert "Psychology" in str(exc)
        assert "allowed buckets" in str(exc)
    else:
        raise AssertionError("Expected InvalidBucketOverrideError")


def test_valid_bucket_override_is_honored_before_greedy_allocation():
    courses = [
        CompletedCourse(
            id=1,
            code="COMP 551",
            credits=4,
            level=551,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
        CompletedCourse(
            id=2,
            code="COMP 550",
            credits=3,
            level=550,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
        CompletedCourse(
            id=3,
            code="COMP 558",
            credits=4,
            level=558,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
    ]

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=courses,
        required_areas=[],
        eligible_streams=["Computer Science"],
        stream_credit_required=18,
        complementary_credit_required=12,
        bucket_overrides={1: "Complementary"},
    )

    allocation = snapshot.stream_complementary
    assert allocation.course_bucket[1] == "complementary"
    assert allocation.complementary_credits == 4
    assert allocation.stream_credits["Computer Science"] == 7
    assert allocation.course_bucket[2] == "stream:Computer Science"
    assert allocation.course_bucket[3] == "stream:Computer Science"
    assert allocation.course_allocations[1].allocated_bucket == "complementary"
    assert allocation.course_allocations[1].eligible_buckets == [
        "Computer Science",
        "Complementary",
    ]


def test_area_overflow_course_can_be_bucket_overridden():
    courses = [
        CompletedCourse(
            id=202,
            code="COMP 202",
            credits=3,
            level=202,
            faculty="Science",
            eligible_streams=("Computer Science",),
            eligible_areas=("Computer Science Foundations",),
        ),
        CompletedCourse(
            id=250,
            code="COMP 250",
            credits=3,
            level=250,
            faculty="Science",
            eligible_streams=("Computer Science",),
            eligible_areas=("Computer Science Foundations",),
        ),
    ]

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=courses,
        required_areas=["Computer Science Foundations"],
        eligible_streams=["Computer Science"],
        stream_credit_required=18,
        complementary_credit_required=12,
        bucket_overrides={250: "Complementary"},
    )

    allocation = snapshot.stream_complementary
    assert snapshot.area_course_ids == {"Computer Science Foundations": 202}
    assert allocation.course_bucket[250] == "complementary"
    assert allocation.complementary_credits == 3
    assert allocation.stream_credits["Computer Science"] == 0
    assert allocation.course_allocations[250].allocated_bucket == "complementary"


def test_arts_science_flexible_faculty_assigns_to_weaker_bucket():
    courses = [
        CompletedCourse(
            id=1,
            code="COMP 551",
            credits=4,
            level=551,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
        CompletedCourse(
            id=2,
            code="COGS 444",
            credits=6,
            level=444,
            faculty="Science",
            flexible_faculty=True,
            elective_only=True,
        ),
    ]

    totals = calculate_arts_science_totals(courses)
    assert totals.arts_credits == 6
    assert totals.science_credits == 4


def test_declared_stream_official_complementary_gets_other_stream_courses():
    courses = [
        CompletedCourse(
            id=1,
            code="COMP 206",
            credits=3,
            level=206,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
        CompletedCourse(
            id=2,
            code="COMP 251",
            credits=3,
            level=251,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
        CompletedCourse(
            id=3,
            code="PSYC 304",
            credits=3,
            level=304,
            faculty="Science",
            eligible_streams=("Psychology",),
        ),
    ]

    explore = allocate_streams_and_complementary_greedy_v1(
        courses,
        stream_credit_required=18,
        complementary_credit_required=12,
        eligible_streams=["Computer Science", "Psychology"],
    )
    assert explore.stream_credits["Computer Science"] == 6
    assert explore.stream_credits["Psychology"] == 3
    assert explore.complementary_credits == 0

    official = allocate_official_with_declared_or_provisional_stream(
        courses,
        declared_stream="Computer Science",
        stream_credit_required=18,
        complementary_credit_required=12,
        eligible_streams=["Computer Science", "Psychology"],
    )
    assert official.stream_is_provisional is False
    assert official.declared_stream == "Computer Science"
    assert official.stream_credits == 6
    assert official.complementary_credits == 3
    assert official.course_bucket[3] == "complementary"


def test_provisional_stream_auto_selects_best_combined_completion():
    courses = [
        CompletedCourse(
            id=1,
            code="COMP 206",
            credits=3,
            level=206,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
        CompletedCourse(
            id=2,
            code="COMP 251",
            credits=3,
            level=251,
            faculty="Science",
            eligible_streams=("Computer Science",),
        ),
        CompletedCourse(
            id=3,
            code="PSYC 304",
            credits=3,
            level=304,
            faculty="Science",
            eligible_streams=("Psychology",),
        ),
    ]

    official = allocate_official_with_declared_or_provisional_stream(
        courses,
        declared_stream=None,
        stream_credit_required=18,
        complementary_credit_required=12,
        eligible_streams=["Computer Science", "Psychology"],
    )
    assert official.stream_is_provisional is True
    assert official.provisional_stream == "Computer Science"
    assert official.stream_credits == 6
    assert official.complementary_credits == 3


def test_official_complementary_overflow_flows_to_electives():
    psych_courses = [
        CompletedCourse(
            id=index,
            code=f"PSYC {300 + index}",
            credits=3,
            level=300 + index,
            faculty="Science",
            eligible_streams=("Psychology",),
        )
        for index in range(1, 6)
    ]

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=psych_courses,
        required_areas=[],
        eligible_streams=["Computer Science", "Psychology"],
        stream_credit_required=18,
        complementary_credit_required=12,
        declared_stream="Computer Science",
    )

    official = snapshot.official_stream_complementary
    assert official.stream_credits == 0
    assert official.complementary_credits == 12
    assert snapshot.electives.credits == 3
    assert len(snapshot.electives.course_ids) == 1


def test_cogs401_and_cogs444_count_as_electives_when_not_area_consumed():
    courses = [
        CompletedCourse(
            id=1,
            code="COGS 401",
            credits=3,
            level=401,
            faculty="Science",
            elective_only=True,
        ),
        CompletedCourse(
            id=2,
            code="COGS 444",
            credits=6,
            level=444,
            faculty="Science",
            flexible_faculty=True,
            elective_only=True,
        ),
    ]

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=courses,
        required_areas=[],
        eligible_streams=["Computer Science"],
        stream_credit_required=18,
        complementary_credit_required=12,
    )

    assert snapshot.electives.credits == 9
    assert snapshot.electives.course_ids == [1, 2]
    assert snapshot.stream_complementary.stream_credits["Computer Science"] == 0

