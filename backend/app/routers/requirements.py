from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Area, Course, Stream
from app.schemas import (
    AreasProgress,
    ArtsScienceProgress,
    LevelProgress,
    RequirementsProgressRequest,
    RequirementsProgressResponse,
    StreamComplementaryProgress,
)
from app.services.degree_evaluator import (
    CompletedCourse,
    evaluate_degree_progress_greedy_v1,
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
    )


def _build_response(
    payload: RequirementsProgressRequest,
    db: Session,
) -> RequirementsProgressResponse:
    required_areas = [a.name for a in db.query(Area).all()]
    stream_names = [s.name for s in db.query(Stream).all()]

    db_courses = []
    if payload.completed_course_ids:
        db_courses = (
            db.query(Course)
            .filter(Course.id.in_(payload.completed_course_ids))
            .all()
        )

    completed: list[CompletedCourse] = []
    for c in db_courses:
        converted = _to_completed_course(c)
        if converted is not None:
            completed.append(converted)

    # Manually-entered (non-major) completed courses can contribute to Arts/
    # Science and 400+ calculators even without stream/area eligibility.
    next_manual_id = -1
    for manual in payload.manual_completed_courses:
        completed.append(
            CompletedCourse(
                id=next_manual_id,
                code=manual.code,
                credits=manual.credits,
                level=manual.level,
                faculty=manual.faculty,
                eligible_streams=[],
                eligible_areas=[],
            )
        )
        next_manual_id -= 1

    snapshot = evaluate_degree_progress_greedy_v1(
        all_completed_courses=completed,
        required_areas=required_areas,
        eligible_streams=stream_names,
        stream_credit_required=18,
        complementary_credit_required=12,
        level_threshold=400,
    )

    return RequirementsProgressResponse(
        arts_science=ArtsScienceProgress(
            arts_credits=snapshot.arts_science.arts_credits,
            science_credits=snapshot.arts_science.science_credits,
        ),
        level_400_plus=LevelProgress(
            threshold=400,
            credits=snapshot.credits_400_plus,
            course_ids=snapshot.eligible_courses_400_plus,
        ),
        stream_complementary=StreamComplementaryProgress(
            stream_credits=snapshot.stream_complementary.stream_credits,
            complementary_credits=snapshot.stream_complementary.complementary_credits,
            course_bucket=snapshot.stream_complementary.course_bucket,
        ),
        areas=AreasProgress(
            required_areas=required_areas,
            completed_areas=sorted(snapshot.completed_areas),
        ),
    )


@router.get("/progress", response_model=RequirementsProgressResponse)
def get_progress(db: Session = Depends(get_db)):
    """
    Browser-friendly contract endpoint for immediate inspection.

    Returns an empty-progress baseline when no completed course input is
    provided.
    """
    return _build_response(
        RequirementsProgressRequest(
            completed_course_ids=[],
            manual_completed_courses=[],
        ),
        db=db,
    )


@router.post("/progress", response_model=RequirementsProgressResponse)
def post_progress(
    payload: RequirementsProgressRequest,
    db: Session = Depends(get_db),
):
    """
    Evaluate requirement progress from:
    - completed DB courses (`completed_course_ids`)
    - optional manually-entered non-major courses
    """
    return _build_response(payload, db=db)

