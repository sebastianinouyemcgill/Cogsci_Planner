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

    phil210 = db.query(Course).filter_by(code="PHIL 210").one()
    assert phil210.faculty == Faculty.ARTS


def test_course_stream_relationship(db):
    seed_all(db)

    cs = db.query(Stream).filter_by(name="Computer Science").one()
    cs_codes = {c.code for c in cs.courses}
    assert "COMP 550" in cs_codes
    assert "COMP 551" in cs_codes
    # Foundation/area courses are not stream courses.
    assert "COMP 202" not in cs_codes


def test_area_course_relationship(db):
    seed_all(db)

    logic = db.query(Area).filter_by(name="Logic").one()
    logic_codes = {c.code for c in logic.courses}
    assert logic_codes == {"COMP 230", "MATH 318", "PHIL 210"}


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
