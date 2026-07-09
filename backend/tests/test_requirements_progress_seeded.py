from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models import Course
from app.routers.requirements import get_db, router as requirements_router
from app.seed import seed_all


def _client_for_db(db):
    app = FastAPI()
    app.include_router(requirements_router)

    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


def test_post_progress_on_seeded_data_comp551_comp550_comp558(db):
    seed_all(db)

    # Canonical example courses (stream + 400+ expected).
    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 551", "COMP 550", "COMP 558"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    payload = {
        "courses": [
            {"course_id": by_code["COMP 551"], "status": "completed"},
            {"course_id": by_code["COMP 550"], "status": "completed"},
            {"course_id": by_code["COMP 558"], "status": "completed"},
        ],
        "manual_completed_courses": [],
    }

    client = _client_for_db(db)
    response = client.post("/api/requirements/progress", json=payload)
    assert response.status_code == 200

    data = response.json()

    for view in ("completed", "projected"):
        # All three are 400+ and all are tagged to the Computer Science stream
        # in the seeded dataset.
        assert data[view]["arts_science"]["arts_credits"] == 0
        assert data[view]["arts_science"]["science_credits"] == 11

        assert data[view]["level_400_plus"]["credits"] == 11

        assert data[view]["stream_complementary"]["complementary_credits"] == 0
        assert data[view]["stream_complementary"]["stream_credits"]["Computer Science"] == 11

        # In the current seeded mapping, these three do not contribute to any
        # of the 8 "areas".
        assert data[view]["areas"]["completed_areas"] == []


def test_post_progress_completed_vs_projected_with_planned_courses(db):
    seed_all(db)

    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 551", "COMP 550", "COMP 558"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    payload = {
        "courses": [
            {"course_id": by_code["COMP 551"], "status": "completed"},
            {"course_id": by_code["COMP 550"], "status": "planned"},
            {"course_id": by_code["COMP 558"], "status": "planned"},
        ],
        "manual_completed_courses": [],
    }

    client = _client_for_db(db)
    response = client.post("/api/requirements/progress", json=payload)
    assert response.status_code == 200

    data = response.json()
    completed = data["completed"]
    projected = data["projected"]

    # Completed view: only COMP 551 (4 credits).
    assert completed["arts_science"]["science_credits"] == 4
    assert completed["level_400_plus"]["credits"] == 4
    assert completed["stream_complementary"]["stream_credits"]["Computer Science"] == 4

    # Projected view: all three courses (4 + 3 + 4 = 11 credits).
    assert projected["arts_science"]["science_credits"] == 11
    assert projected["level_400_plus"]["credits"] == 11
    assert projected["stream_complementary"]["stream_credits"]["Computer Science"] == 11

    # The two views must differ when planned courses are present.
    assert completed != projected


def test_post_progress_extra_area_course_with_stream_mapping_counts_stream(db):
    seed_all(db)

    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 202", "COMP 250"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    payload = {
        "courses": [
            {"course_id": by_code["COMP 202"], "status": "completed"},
            {"course_id": by_code["COMP 250"], "status": "completed"},
        ],
        "manual_completed_courses": [],
    }

    client = _client_for_db(db)
    response = client.post("/api/requirements/progress", json=payload)
    assert response.status_code == 200

    completed = response.json()["completed"]

    assert completed["areas"]["completed_areas"] == [
        "Computer Science Foundations"
    ]
    assert (
        completed["areas"]["area_course_ids"]["Computer Science Foundations"]
        == by_code["COMP 202"]
    )
    assert (
        completed["stream_complementary"]["stream_credits"]["Computer Science"]
        == 3
    )
    assert (
        completed["stream_complementary"]["course_bucket"][str(by_code["COMP 250"])]
        == "stream:Computer Science"
    )


def test_post_progress_extra_area_course_without_stream_mapping_counts_elective(db):
    seed_all(db)

    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["MATH 203", "MATH 323"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    payload = {
        "courses": [
            {"course_id": by_code["MATH 203"], "status": "completed"},
            {"course_id": by_code["MATH 323"], "status": "completed"},
        ],
        "manual_completed_courses": [],
    }

    client = _client_for_db(db)
    response = client.post("/api/requirements/progress", json=payload)
    assert response.status_code == 200

    completed = response.json()["completed"]

    assert completed["areas"]["completed_areas"] == ["Statistics"]
    assert (
        completed["areas"]["area_course_ids"]["Statistics"]
        == by_code["MATH 203"]
    )
    assert completed["electives"]["credits"] == 3
    assert completed["electives"]["course_ids"] == [by_code["MATH 323"]]
    assert all(
        credits == 0
        for credits in completed["stream_complementary"]["stream_credits"].values()
    )


def test_post_progress_invalid_bucket_override_returns_422(db):
    seed_all(db)

    comp551_id = (
        db.query(Course.id).filter(Course.code == "COMP 551").scalar()
    )

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "courses": [
                {
                    "course_id": comp551_id,
                    "status": "completed",
                    "bucket_override": "Psychology",
                }
            ],
            "manual_completed_courses": [],
        },
    )

    assert response.status_code == 422
    assert "COMP 551" in response.json()["detail"]
    assert "Psychology" in response.json()["detail"]


def test_post_progress_valid_bucket_override_honored_with_auto_allocation(db):
    seed_all(db)

    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 551", "COMP 550", "COMP 558"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "courses": [
                {
                    "course_id": by_code["COMP 551"],
                    "status": "completed",
                    "bucket_override": "Complementary",
                },
                {"course_id": by_code["COMP 550"], "status": "completed"},
                {"course_id": by_code["COMP 558"], "status": "completed"},
            ],
            "manual_completed_courses": [],
        },
    )
    assert response.status_code == 200

    completed = response.json()["completed"]["stream_complementary"]
    assert completed["course_bucket"][str(by_code["COMP 551"])] == "complementary"
    assert completed["complementary_credits"] == 4
    assert completed["stream_credits"]["Computer Science"] == 7
    assert (
        completed["course_allocations"][str(by_code["COMP 551"])]["allocated_bucket"]
        == "complementary"
    )


def test_post_progress_area_overflow_course_bucket_override(db):
    seed_all(db)

    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 202", "COMP 250"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "courses": [
                {"course_id": by_code["COMP 202"], "status": "completed"},
                {
                    "course_id": by_code["COMP 250"],
                    "status": "completed",
                    "bucket_override": "Complementary",
                },
            ],
            "manual_completed_courses": [],
        },
    )
    assert response.status_code == 200

    completed = response.json()["completed"]
    stream = completed["stream_complementary"]

    assert completed["areas"]["area_course_ids"]["Computer Science Foundations"] == (
        by_code["COMP 202"]
    )
    assert stream["course_bucket"][str(by_code["COMP 250"])] == "complementary"
    assert stream["complementary_credits"] == 3
    assert stream["stream_credits"]["Computer Science"] == 0
    assert (
        stream["course_allocations"][str(by_code["COMP 250"])]["allocated_bucket"]
        == "complementary"
    )


def test_post_progress_honours_on_cogs444_completed_satisfies_requirement(db):
    seed_all(db)

    cogs444_id = db.query(Course.id).filter(Course.code == "COGS 444").scalar()

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "honours_enabled": True,
            "courses": [
                {"course_id": cogs444_id, "status": "completed"},
            ],
            "manual_completed_courses": [],
        },
    )
    assert response.status_code == 200

    data = response.json()
    for view in ("completed", "projected"):
        honours = data[view]["honours_research"]
        assert honours["required_credits"] == 6
        assert honours["credits"] == 6
        assert honours["remaining_credits"] == 0
        assert honours["course_ids"] == [cogs444_id]
        assert honours["satisfied"] is True


def test_post_progress_honours_on_cogs444_not_taken_shows_remaining(db):
    seed_all(db)

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "honours_enabled": True,
            "courses": [],
            "manual_completed_courses": [],
        },
    )
    assert response.status_code == 200

    data = response.json()
    for view in ("completed", "projected"):
        honours = data[view]["honours_research"]
        assert honours["required_credits"] == 6
        assert honours["credits"] == 0
        assert honours["remaining_credits"] == 6
        assert honours["course_ids"] == []
        assert honours["satisfied"] is False


def test_post_progress_honours_off_omits_requirement_even_with_cogs444(db):
    seed_all(db)

    cogs444_id = db.query(Course.id).filter(Course.code == "COGS 444").scalar()

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "honours_enabled": False,
            "courses": [
                {"course_id": cogs444_id, "status": "completed"},
            ],
            "manual_completed_courses": [],
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert "honours_research" not in data["completed"]
    assert "honours_research" not in data["projected"]


def test_post_progress_declared_stream_cs_puts_psych_in_official_complementary(db):
    seed_all(db)

    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 206", "COMP 251", "PSYC 304"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    payload = {
        "declared_stream": "Computer Science",
        "courses": [
            {"course_id": by_code["COMP 206"], "status": "completed"},
            {"course_id": by_code["COMP 251"], "status": "completed"},
            {"course_id": by_code["PSYC 304"], "status": "completed"},
        ],
        "manual_completed_courses": [],
    }

    client = _client_for_db(db)
    response = client.post("/api/requirements/progress", json=payload)
    assert response.status_code == 200

    data = response.json()["completed"]
    explore = data["stream_complementary"]
    official = data["official_stream_complementary"]

    # Explore view unchanged: independent per-stream tallies.
    assert explore["stream_credits"]["Computer Science"] == 6
    assert explore["stream_credits"]["Psychology"] == 3
    assert explore["complementary_credits"] == 0

    # Official view: CS stream + Psych in complementary.
    assert official["declared_stream"] == "Computer Science"
    assert official["stream_is_provisional"] is False
    assert official["stream_credits"] == 6
    assert official["complementary_credits"] == 3
    assert official["course_bucket"][str(by_code["PSYC 304"])] == "complementary"


def test_post_progress_provisional_stream_auto_selects_computer_science(db):
    seed_all(db)

    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 206", "COMP 251", "PSYC 304"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    payload = {
        "declared_stream": None,
        "courses": [
            {"course_id": by_code["COMP 206"], "status": "completed"},
            {"course_id": by_code["COMP 251"], "status": "completed"},
            {"course_id": by_code["PSYC 304"], "status": "completed"},
        ],
        "manual_completed_courses": [],
    }

    client = _client_for_db(db)
    response = client.post("/api/requirements/progress", json=payload)
    assert response.status_code == 200

    official = response.json()["completed"]["official_stream_complementary"]
    assert official["stream_is_provisional"] is True
    assert official["provisional_stream"] == "Computer Science"
    assert official["stream_credits"] == 6
    assert official["complementary_credits"] == 3


def test_post_progress_cogs444_flexible_faculty_and_electives(db):
    seed_all(db)

    cogs444_id = db.query(Course.id).filter(Course.code == "COGS 444").scalar()

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "courses": [
                {"course_id": cogs444_id, "status": "completed"},
            ],
            "manual_completed_courses": [],
        },
    )
    assert response.status_code == 200

    completed = response.json()["completed"]
    assert completed["arts_science"]["arts_credits"] == 6
    assert completed["arts_science"]["science_credits"] == 0
    assert completed["electives"]["credits"] == 6
    assert completed["electives"]["course_ids"] == [cogs444_id]
