"""Idempotent seeding of the academic data model.

`seed_all(db)` populates streams, areas, courses, requirements, and the
relationships between them. It is safe to run repeatedly: existing rows are
matched by their natural key (name / code) and updated rather than
duplicated. This file contains no requirement-evaluation logic — only
persistence of the domain data defined in `data.py`.
"""

from sqlalchemy.orm import Session

from app.models import Area, Course, Faculty, Requirement, Stream
from app.seed import data


def _upsert_streams(db: Session) -> dict[str, Stream]:
    by_name: dict[str, Stream] = {}
    for row in data.STREAMS:
        stream = db.query(Stream).filter_by(name=row["name"]).first()
        if stream is None:
            stream = Stream(name=row["name"])
            db.add(stream)
        by_name[row["name"]] = stream
    db.flush()
    return by_name


def _upsert_areas(db: Session) -> dict[str, Area]:
    by_name: dict[str, Area] = {}
    for row in data.AREAS:
        area = db.query(Area).filter_by(name=row["name"]).first()
        if area is None:
            area = Area(name=row["name"])
            db.add(area)
        by_name[row["name"]] = area
    db.flush()
    return by_name


def _upsert_courses(db: Session) -> dict[str, Course]:
    by_code: dict[str, Course] = {}
    for row in data.COURSES:
        course = db.query(Course).filter_by(code=row["code"]).first()
        if course is None:
            course = Course(code=row["code"])
            db.add(course)
        course.title = row["title"]
        course.description = row.get("description")
        course.credits = row.get("credits")
        course.level = row.get("level")
        course.department = row.get("department")
        faculty = row.get("faculty")
        course.faculty = Faculty(faculty) if faculty is not None else None
        by_code[row["code"]] = course
    db.flush()
    return by_code


def _upsert_requirements(db: Session) -> None:
    for row in data.REQUIREMENTS:
        req = db.query(Requirement).filter_by(name=row["name"]).first()
        if req is None:
            req = Requirement(name=row["name"])
            db.add(req)
        req.type = row["type"]
        req.credits_required = row["credits_required"]
    db.flush()


def _link_course_streams(
    db: Session,
    courses: dict[str, Course],
    streams: dict[str, Stream],
) -> list[str]:
    warnings: list[str] = []
    desired_by_course: dict[str, set[str]] = {code: set() for code in courses}
    for course_code, stream_name in data.COURSE_STREAMS:
        desired_by_course.setdefault(course_code, set()).add(stream_name)
        course = courses.get(course_code)
        stream = streams.get(stream_name)
        if course is None or stream is None:
            warnings.append(
                f"course_stream skipped: {course_code} -> {stream_name}"
            )
            continue

    # Match seed data exactly when re-running, so corrected mappings remove
    # stale tags from existing databases (for example PSYC 211 -> Psychology).
    for course_code, course in courses.items():
        desired_streams = [
            streams[name]
            for name in sorted(desired_by_course.get(course_code, set()))
            if name in streams
        ]
        course.streams = desired_streams
    return warnings


def _link_area_courses(
    db: Session,
    courses: dict[str, Course],
    areas: dict[str, Area],
) -> list[str]:
    warnings: list[str] = []
    for area_name, course_code in data.AREA_COURSES:
        area = areas.get(area_name)
        course = courses.get(course_code)
        if area is None or course is None:
            warnings.append(
                f"area_course skipped: {area_name} -> {course_code}"
            )
            continue
        if course not in area.courses:
            area.courses.append(course)
    return warnings


def _link_prerequisites(
    db: Session,
    courses: dict[str, Course],
) -> list[str]:
    warnings: list[str] = []
    for course_code, prereq_code in data.PREREQUISITES:
        course = courses.get(course_code)
        prereq = courses.get(prereq_code)
        if course is None or prereq is None:
            warnings.append(
                f"prerequisite skipped: {course_code} requires {prereq_code}"
            )
            continue
        if prereq not in course.prerequisites:
            course.prerequisites.append(prereq)
    return warnings


def seed_all(db: Session) -> dict[str, object]:
    """Populate the database. Returns a small summary dict for logging/tests."""
    streams = _upsert_streams(db)
    areas = _upsert_areas(db)
    courses = _upsert_courses(db)
    _upsert_requirements(db)

    warnings: list[str] = []
    warnings += _link_course_streams(db, courses, streams)
    warnings += _link_area_courses(db, courses, areas)
    warnings += _link_prerequisites(db, courses)

    db.commit()

    return {
        "streams": len(streams),
        "areas": len(areas),
        "courses": len(courses),
        "requirements": len(data.REQUIREMENTS),
        "warnings": warnings,
    }
