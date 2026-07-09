"""Tests for the Phase 1 academic data model and seeder.

These run against an in-memory SQLite database (see conftest.py), so they
exercise the models, relationships, and seeding logic without needing a
running Postgres instance.
"""

from app.models import Area, Course, Faculty, Requirement, Stream
from app.seed import data
from app.seed.seeder import seed_all


def test_seed_populates_expected_counts(db):
    summary = seed_all(db)

    assert db.query(Stream).count() == len(data.STREAMS) == 5
    assert db.query(Area).count() == len(data.AREAS) == 8
    assert db.query(Course).count() == len(data.COURSES)
    assert db.query(Requirement).count() == len(data.REQUIREMENTS)

    # Every relationship row in the provided data resolves to real rows.
    assert summary["warnings"] == []


def test_seed_is_idempotent(db):
    seed_all(db)
    course_count = db.query(Course).count()
    stream_count = db.query(Stream).count()

    # Running again must not duplicate rows or relationships.
    seed_all(db)

    assert db.query(Course).count() == course_count
    assert db.query(Stream).count() == stream_count

    comp550 = db.query(Course).filter_by(code="COMP 550").one()
    stream_names = [s.name for s in comp550.streams]
    assert stream_names.count("Computer Science") == 1


def test_course_metadata_and_faculty_enum(db):
    seed_all(db)

    comp551 = db.query(Course).filter_by(code="COMP 551").one()
    assert comp551.credits == 4
    assert comp551.level == 551
    assert comp551.faculty == Faculty.SCIENCE
    assert comp551.department == "Computer Science"

    cogs444 = db.query(Course).filter_by(code="COGS 444").one()
    assert cogs444.title == "Honours Research"
    assert cogs444.credits == 6
    assert cogs444.level == 444
    # McGill lists this as Arts & Science Admin (Shared); current model stores
    # only Arts/Science, so the seed uses the documented Science fallback.
    assert cogs444.faculty == Faculty.SCIENCE
    assert cogs444.department == "Cognitive Science"

    phil210 = db.query(Course).filter_by(code="PHIL 210").one()
    assert phil210.faculty == Faculty.ARTS


def test_course_stream_relationship(db):
    seed_all(db)

    cs = db.query(Stream).filter_by(name="Computer Science").one()
    cs_codes = {c.code for c in cs.courses}
    # COMP 202 is area-only (not on the CS stream complementary list).
    assert "COMP 202" not in cs_codes
    assert "COMP 250" in cs_codes
    assert "COMP 550" in cs_codes
    assert "COMP 551" in cs_codes

    comp202 = db.query(Course).filter_by(code="COMP 202").one()
    assert comp202.streams == []

    neuro = db.query(Stream).filter_by(name="Neuroscience").one()
    neuro_codes = {c.code for c in neuro.courses}
    assert "NSCI 201" in neuro_codes
    # PSYC 211 is area-only (Neuro Foundations), not on the Neuro stream list.
    assert "PSYC 211" not in neuro_codes

    psych = db.query(Stream).filter_by(name="Psychology").one()
    psych_codes = {c.code for c in psych.courses}
    assert "PSYC 211" not in psych_codes
    assert "PSYC 304" in psych_codes

    for electives_only_code in data.ELECTIVES_BUCKET_COURSES:
        course = db.query(Course).filter_by(code=electives_only_code).one()
        assert course.streams == []


def test_cogs401_and_cogs444_are_elective_bucket_courses(db):
    seed_all(db)

    cogs401 = db.query(Course).filter_by(code="COGS 401").one()
    assert cogs401.credits == 6
    assert cogs401.title == "Research Cognitive Science 1"
    assert cogs401.level == 401
    assert cogs401.streams == []

    cogs444 = db.query(Course).filter_by(code="COGS 444").one()
    assert cogs444.credits == 6
    assert cogs444.streams == []
    assert "COGS 444" in data.FLEXIBLE_FACULTY_COURSES


def test_area_course_relationship(db):
    seed_all(db)

    logic = db.query(Area).filter_by(name="Logic").one()
    logic_codes = {c.code for c in logic.courses}
    assert logic_codes == {"COMP 230", "MATH 318", "PHIL 210"}

    phil = db.query(Area).filter_by(name="Philosophy Foundations").one()
    phil_codes = {c.code for c in phil.courses}
    assert phil_codes == {"PHIL 200", "PHIL 201", "PHIL 203", "PHIL 221"}


def test_prerequisite_relationship_is_self_referencing(db):
    seed_all(db)

    comp251 = db.query(Course).filter_by(code="COMP 251").one()
    prereq_codes = {c.code for c in comp251.prerequisites}
    assert "COMP 250" in prereq_codes

    # The backref exposes the inverse direction ("required_for").
    comp250 = db.query(Course).filter_by(code="COMP 250").one()
    required_for_codes = {c.code for c in comp250.required_for}
    assert "COMP 251" in required_for_codes


def test_requirements_have_types_and_credits(db):
    seed_all(db)

    stream_req = db.query(Requirement).filter_by(name="Stream Requirement").one()
    assert stream_req.type == "stream"
    assert stream_req.credits_required == 18
