from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Area, Course, Requirement, Stream
from app.schemas import (
    AreasProgress,
    ArtsScienceProgress,
    CourseBucketAllocation,
    ElectivesProgress,
    HonoursResearchProgress,
    LevelProgress,
    OfficialStreamComplementaryProgress,
    RequirementProgressBreakdown,
    RequirementsProgressRequest,
    RequirementsProgressResponse,
    StreamComplementaryProgress,
)
from app.seed import data as seed_data
from app.services.degree_evaluator import (
    CompletedCourse,
    InvalidBucketOverrideError,
    InvalidDeclaredStreamError,
    ProgressSnapshot,
    evaluate_degree_progress_completed_and_projected,
)


router = APIRouter(
    prefix="/api/requirements",
    tags=["requirements"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _to_completed_course(course: Course) -> CompletedCourse | None:
    # Incomplete rows are ignored in progress calculations.
    if course.credits is None or course.level is None or course.faculty is None:
        return None

    return CompletedCourse(
        id=course.id,
        code=course.code,
        credits=course.credits,
        level=course.level,
        faculty=course.faculty.value,
        eligible_streams=[s.name for s in course.streams],
        eligible_areas=[a.name for a in course.areas],
        elective_only=course.code in seed_data.ELECTIVES_BUCKET_COURSES,
        flexible_faculty=course.code in seed_data.FLEXIBLE_FACULTY_COURSES,
    )


def _manual_completed_courses(
    payload: RequirementsProgressRequest,
) -> list[CompletedCourse]:
    manual: list[CompletedCourse] = []
    next_manual_id = -1
    for manual_input in payload.manual_completed_courses:
        manual.append(
            CompletedCourse(
                id=next_manual_id,
                code=manual_input.code,
                credits=manual_input.credits,
                level=manual_input.level,
                faculty=manual_input.faculty,
                eligible_streams=[],
                eligible_areas=[],
                elective_only=False,
            )
        )
        next_manual_id -= 1
    return manual


def _db_courses_by_status(
    payload: RequirementsProgressRequest,
    db: Session,
) -> tuple[list[CompletedCourse], list[CompletedCourse]]:
    completed_ids = [e.course_id for e in payload.courses if e.status == "completed"]
    projected_ids = [
        e.course_id for e in payload.courses if e.status in ("completed", "planned")
    ]

    def _load(course_ids: list[int]) -> list[CompletedCourse]:
        if not course_ids:
            return []
        rows = (
            db.query(Course)
            .filter(Course.id.in_(course_ids))
            .order_by(Course.id.asc())
            .all()
        )
        loaded: list[CompletedCourse] = []
        for course in rows:
            converted = _to_completed_course(course)
            if converted is not None:
                loaded.append(converted)
        return loaded

    return _load(completed_ids), _load(projected_ids)


def _bucket_overrides_for_statuses(
    payload: RequirementsProgressRequest,
    statuses: set[str],
) -> dict[int, str]:
    overrides: dict[int, str] = {}
    for entry in payload.courses:
        if entry.status in statuses and entry.bucket_override is not None:
            overrides[entry.course_id] = entry.bucket_override
    return overrides


def _snapshot_to_breakdown(
    snapshot: ProgressSnapshot,
    *,
    required_areas: list[str],
    level_threshold: int,
    stream_credit_required: int,
    complementary_credit_required: int,
    honours_research: HonoursResearchProgress | None = None,
) -> RequirementProgressBreakdown:
    official = snapshot.official_stream_complementary
    return RequirementProgressBreakdown(
        arts_science=ArtsScienceProgress(
            arts_credits=snapshot.arts_science.arts_credits,
            science_credits=snapshot.arts_science.science_credits,
        ),
        level_400_plus=LevelProgress(
            threshold=level_threshold,
            credits=snapshot.credits_400_plus,
            course_ids=snapshot.eligible_courses_400_plus,
        ),
        stream_complementary=StreamComplementaryProgress(
            stream_credits=snapshot.stream_complementary.stream_credits,
            complementary_credits=snapshot.stream_complementary.complementary_credits,
            course_bucket=snapshot.stream_complementary.course_bucket,
            course_allocations={
                course_id: CourseBucketAllocation(
                    eligible_buckets=detail.eligible_buckets,
                    allocated_bucket=detail.allocated_bucket,
                )
                for course_id, detail in snapshot.stream_complementary.course_allocations.items()
            },
        ),
        official_stream_complementary=OfficialStreamComplementaryProgress(
            declared_stream=official.declared_stream,
            stream_is_provisional=official.stream_is_provisional,
            provisional_stream=official.provisional_stream,
            stream_credits=official.stream_credits,
            stream_credit_required=stream_credit_required,
            complementary_credits=official.complementary_credits,
            complementary_credit_required=complementary_credit_required,
            course_bucket=official.course_bucket,
            course_allocations={
                course_id: CourseBucketAllocation(
                    eligible_buckets=detail.eligible_buckets,
                    allocated_bucket=detail.allocated_bucket,
                )
                for course_id, detail in official.course_allocations.items()
            },
        ),
        electives=ElectivesProgress(
            credits=snapshot.electives.credits,
            course_ids=snapshot.electives.course_ids,
        ),
        areas=AreasProgress(
            required_areas=required_areas,
            completed_areas=sorted(snapshot.completed_areas),
            area_course_ids=snapshot.area_course_ids,
        ),
        honours_research=honours_research,
    )


def _honours_research_progress(
    courses: list[CompletedCourse],
    *,
    required_credits: int,
) -> HonoursResearchProgress:
    matching = [course for course in courses if course.code == "COGS 444"]
    credits = sum(course.credits for course in matching)
    capped_credits = min(credits, required_credits)
    return HonoursResearchProgress(
        required_credits=required_credits,
        credits=capped_credits,
        remaining_credits=max(0, required_credits - capped_credits),
        course_ids=[course.id for course in matching],
        satisfied=capped_credits >= required_credits,
    )


def _build_response(
    payload: RequirementsProgressRequest,
    db: Session,
) -> RequirementsProgressResponse:
    required_areas = [a.name for a in db.query(Area).all()]
    stream_names = [s.name for s in db.query(Stream).all()]

    stream_req = db.query(Requirement).filter(Requirement.type == "stream").first()
    complementary_req = (
        db.query(Requirement).filter(Requirement.type == "complementary").first()
    )
    honours_req = db.query(Requirement).filter(Requirement.type == "honours").first()

    stream_credit_required = stream_req.credits_required if stream_req else 18
    complementary_credit_required = (
        complementary_req.credits_required if complementary_req else 12
    )
    honours_credit_required = honours_req.credits_required if honours_req else 6
    level_threshold = 400

    completed_db, projected_db = _db_courses_by_status(payload, db)
    manual = _manual_completed_courses(payload)
    completed_courses = [*completed_db, *manual]
    projected_courses = [*projected_db, *manual]
    completed_overrides = _bucket_overrides_for_statuses(payload, {"completed"})
    projected_overrides = _bucket_overrides_for_statuses(
        payload,
        {"completed", "planned"},
    )

    try:
        dual = evaluate_degree_progress_completed_and_projected(
            completed_only_courses=completed_courses,
            completed_and_planned_courses=projected_courses,
            required_areas=required_areas,
            eligible_streams=stream_names,
            stream_credit_required=stream_credit_required,
            complementary_credit_required=complementary_credit_required,
            level_threshold=level_threshold,
            declared_stream=payload.declared_stream,
            completed_bucket_overrides=completed_overrides,
            projected_bucket_overrides=projected_overrides,
        )
    except InvalidBucketOverrideError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InvalidDeclaredStreamError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    completed_honours = None
    projected_honours = None
    if payload.honours_enabled:
        completed_honours = _honours_research_progress(
            completed_courses,
            required_credits=honours_credit_required,
        )
        projected_honours = _honours_research_progress(
            projected_courses,
            required_credits=honours_credit_required,
        )

    return RequirementsProgressResponse(
        completed=_snapshot_to_breakdown(
            dual.completed,
            required_areas=required_areas,
            level_threshold=level_threshold,
            stream_credit_required=stream_credit_required,
            complementary_credit_required=complementary_credit_required,
            honours_research=completed_honours,
        ),
        projected=_snapshot_to_breakdown(
            dual.projected,
            required_areas=required_areas,
            level_threshold=level_threshold,
            stream_credit_required=stream_credit_required,
            complementary_credit_required=complementary_credit_required,
            honours_research=projected_honours,
        ),
    )


@router.get(
    "/progress",
    response_model=RequirementsProgressResponse,
    response_model_exclude_none=True,
)
def get_progress(db: Session = Depends(get_db)):
    """
    Browser-friendly contract endpoint for immediate inspection.

    Returns an empty-progress baseline when no completed course input is
    provided.
    """
    return _build_response(
        RequirementsProgressRequest(
            courses=[],
            manual_completed_courses=[],
        ),
        db=db,
    )


@router.post(
    "/progress",
    response_model=RequirementsProgressResponse,
    response_model_exclude_none=True,
)
def post_progress(
    payload: RequirementsProgressRequest,
    db: Session = Depends(get_db),
):
    """
    Evaluate requirement progress from:
    - DB courses with status `completed` or `planned` (`courses`)
    - optional manually-entered non-major completed courses
    """
    return _build_response(payload, db=db)

